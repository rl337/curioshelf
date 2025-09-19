"""
UI Instrumentation Server

This module provides a server for remotely controlling and debugging UI components.
It allows external tools to connect and send commands to the UI system.
"""

import json
import socket
import threading
import time
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

from .ui_debug import UIDebugger, UIRemoteController, DebugMessage, DebugMessageType


class UIInstrumentationServer:
    """Server for remote UI instrumentation and control"""
    
    def __init__(self, debugger: UIDebugger, host: str = "localhost", port: int = 8888):
        self.debugger = debugger
        self.host = host
        self.port = port
        self.remote_controller = UIRemoteController(debugger)
        self.server_socket: Optional[socket.socket] = None
        self.clients: List[socket.socket] = []
        self.running = False
        self.server_thread: Optional[threading.Thread] = None
        
        # Subscribe to debug messages
        self.debugger.subscribe(self._on_debug_message)
    
    def start(self):
        """Start the instrumentation server"""
        if self.running:
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
        self.debugger.log(DebugMessageType.INFO, "UIInstrumentationServer", 
                         "server_started", {"host": self.host, "port": self.port})
    
    def stop(self):
        """Stop the instrumentation server"""
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        self.debugger.log(DebugMessageType.INFO, "UIInstrumentationServer", 
                         "server_stopped", {})
    
    def _run_server(self):
        """Run the server in a separate thread"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.debugger.log(DebugMessageType.INFO, "UIInstrumentationServer", 
                             "listening", {"host": self.host, "port": self.port})
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.clients.append(client_socket)
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client, 
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        self.debugger.log(DebugMessageType.ERROR, "UIInstrumentationServer", 
                                         "accept_error", {})
                    break
                    
        except Exception as e:
            self.debugger.log(DebugMessageType.ERROR, "UIInstrumentationServer", 
                             "server_error", {"error": str(e)})
        finally:
            self.running = False
    
    def _handle_client(self, client_socket: socket.socket, address):
        """Handle a client connection"""
        try:
            self.debugger.log(DebugMessageType.INFO, "UIInstrumentationServer", 
                             "client_connected", {"address": str(address)})
            
            while self.running:
                try:
                    # Receive data from client
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    # Parse JSON command
                    try:
                        command = json.loads(data.decode('utf-8'))
                        response = self._process_command(command)
                        
                        # Send response back to client
                        response_data = json.dumps(response).encode('utf-8')
                        client_socket.send(response_data)
                        
                    except json.JSONDecodeError as e:
                        response = {"error": f"Invalid JSON: {e}"}
                        client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except socket.error:
                    break
                    
        except Exception as e:
            self.debugger.log(DebugMessageType.ERROR, "UIInstrumentationServer", 
                             "client_error", {"error": str(e)})
        finally:
            try:
                client_socket.close()
            except:
                pass
            
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            
            self.debugger.log(DebugMessageType.INFO, "UIInstrumentationServer", 
                             "client_disconnected", {"address": str(address)})
    
    def _process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process a command from a client"""
        try:
            cmd_type = command.get("type")
            
            if cmd_type == "list_controllers":
                return {
                    "success": True,
                    "data": self.remote_controller.list_controllers()
                }
            
            elif cmd_type == "list_commands":
                controller_name = command.get("controller")
                if not controller_name:
                    return {"error": "Controller name required"}
                
                return {
                    "success": True,
                    "data": self.remote_controller.list_commands(controller_name)
                }
            
            elif cmd_type == "send_command":
                controller_name = command.get("controller")
                command_name = command.get("command")
                args = command.get("args", {})
                
                if not controller_name or not command_name:
                    return {"error": "Controller name and command required"}
                
                success = self.remote_controller.send_command(controller_name, command_name, args)
                return {"success": success}
            
            elif cmd_type == "get_messages":
                message_type = command.get("message_type")
                component = command.get("component")
                
                messages = self.debugger.get_messages(
                    message_type=DebugMessageType(message_type) if message_type else None,
                    component=component
                )
                
                return {
                    "success": True,
                    "data": [msg.to_dict() for msg in messages]
                }
            
            elif cmd_type == "clear_messages":
                self.debugger.clear_messages()
                return {"success": True}
            
            elif cmd_type == "export_messages":
                file_path = command.get("file_path")
                if not file_path:
                    return {"error": "File path required"}
                
                self.debugger.export_messages(Path(file_path))
                return {"success": True}
            
            else:
                return {"error": f"Unknown command type: {cmd_type}"}
                
        except Exception as e:
            return {"error": f"Command processing error: {e}"}
    
    def _on_debug_message(self, message: DebugMessage):
        """Handle debug messages (for logging)"""
        # This could be used to broadcast messages to connected clients
        pass
    
    def register_controller(self, name: str, controller: Any):
        """Register a controller for remote access"""
        self.remote_controller.register_controller(name, controller)


class UIDebugClient:
    """Client for connecting to the UI instrumentation server"""
    
    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
    
    def connect(self) -> bool:
        """Connect to the instrumentation server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send a command to the server"""
        if not self.socket:
            return {"error": "Not connected to server"}
        
        try:
            # Send command
            data = json.dumps(command).encode('utf-8')
            self.socket.send(data)
            
            # Receive response
            response_data = self.socket.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            return response
            
        except Exception as e:
            return {"error": f"Communication error: {e}"}
    
    def list_controllers(self) -> List[str]:
        """List available controllers"""
        response = self.send_command({"type": "list_controllers"})
        if response.get("success"):
            return response.get("data", [])
        return []
    
    def list_commands(self, controller_name: str) -> List[str]:
        """List commands for a controller"""
        response = self.send_command({
            "type": "list_commands",
            "controller": controller_name
        })
        if response.get("success"):
            return response.get("data", [])
        return []
    
    def send_controller_command(self, controller_name: str, command_name: str, 
                              args: Optional[Dict[str, Any]] = None) -> bool:
        """Send a command to a controller"""
        response = self.send_command({
            "type": "send_command",
            "controller": controller_name,
            "command": command_name,
            "args": args or {}
        })
        return response.get("success", False)
    
    def get_messages(self, message_type: Optional[str] = None, 
                    component: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get debug messages"""
        response = self.send_command({
            "type": "get_messages",
            "message_type": message_type,
            "component": component
        })
        if response.get("success"):
            return response.get("data", [])
        return []
    
    def clear_messages(self) -> bool:
        """Clear debug messages"""
        response = self.send_command({"type": "clear_messages"})
        return response.get("success", False)
    
    def export_messages(self, file_path: str) -> bool:
        """Export messages to a file"""
        response = self.send_command({
            "type": "export_messages",
            "file_path": file_path
        })
        return response.get("success", False)
