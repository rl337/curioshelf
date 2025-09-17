#!/usr/bin/env python3
"""
UI Debug Client

This script provides a command-line interface for debugging and controlling
the UI system remotely.
"""

import sys
import json
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from curioshelf.ui_instrumentation_server import UIDebugClient


def print_help():
    """Print help information"""
    print("UI Debug Client Commands:")
    print("  help                    - Show this help")
    print("  list                    - List available controllers")
    print("  commands <controller>   - List commands for a controller")
    print("  send <controller> <command> [args] - Send a command to a controller")
    print("  messages [type] [component] - Get debug messages")
    print("  clear                   - Clear debug messages")
    print("  export <file>           - Export messages to file")
    print("  quit                    - Exit the client")


def main():
    """Main debug client loop"""
    print("UI Debug Client")
    print("Connecting to server...")
    
    client = UIDebugClient()
    if not client.connect():
        print("Failed to connect to server. Make sure the application is running with debugging enabled.")
        return
    
    print("Connected to server!")
    print("Type 'help' for available commands.")
    
    while True:
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == "help":
                print_help()
            
            elif cmd == "list":
                controllers = client.list_controllers()
                print(f"Available controllers: {controllers}")
            
            elif cmd == "commands":
                if len(command) < 2:
                    print("Usage: commands <controller>")
                    continue
                
                controller_name = command[1]
                commands = client.list_commands(controller_name)
                print(f"Commands for {controller_name}: {commands}")
            
            elif cmd == "send":
                if len(command) < 3:
                    print("Usage: send <controller> <command> [args]")
                    continue
                
                controller_name = command[1]
                command_name = command[2]
                args = {}
                
                # Parse additional arguments
                if len(command) > 3:
                    try:
                        args = json.loads(" ".join(command[3:]))
                    except json.JSONDecodeError:
                        print("Invalid JSON in arguments")
                        continue
                
                success = client.send_controller_command(controller_name, command_name, args)
                print(f"Command {'succeeded' if success else 'failed'}")
            
            elif cmd == "messages":
                message_type = command[1] if len(command) > 1 else None
                component = command[2] if len(command) > 2 else None
                
                messages = client.get_messages(message_type, component)
                print(f"Found {len(messages)} messages:")
                for msg in messages[-10:]:  # Show last 10 messages
                    print(f"  {msg['timestamp']:.3f} [{msg['message_type']}] {msg['component']}.{msg['action']}")
            
            elif cmd == "clear":
                success = client.clear_messages()
                print(f"Messages {'cleared' if success else 'not cleared'}")
            
            elif cmd == "export":
                if len(command) < 2:
                    print("Usage: export <file>")
                    continue
                
                file_path = command[1]
                success = client.export_messages(file_path)
                print(f"Messages {'exported' if success else 'not exported'} to {file_path}")
            
            elif cmd == "quit":
                break
            
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    client.disconnect()
    print("Disconnected from server.")


if __name__ == "__main__":
    main()
