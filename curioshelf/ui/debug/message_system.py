"""
Message system for headless UI implementation

This module provides a structured message logging system that can be used
for both testing assertions and command-line output. Messages are collected
in a structured format that allows for easy testing and debugging.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import time
from datetime import datetime


class MessageType(Enum):
    """Types of messages that can be logged"""
    UI_EVENT = "ui_event"
    USER_ACTION = "user_action"
    STATE_CHANGE = "state_change"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


@dataclass
class UIMessage:
    """A structured message for UI events and actions"""
    
    message_type: MessageType
    component: str
    action: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: Optional[str] = None
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        timestamp_str = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S.%f")[:-3]
        
        # Format the message based on type
        if self.message_type == MessageType.UI_EVENT:
            return f"[{timestamp_str}] {self.component}: {self.action}"
        elif self.message_type == MessageType.USER_ACTION:
            return f"[{timestamp_str}] USER ACTION: {self.component}.{self.action}"
        elif self.message_type == MessageType.STATE_CHANGE:
            return f"[{timestamp_str}] STATE: {self.component} -> {self.action}"
        elif self.message_type == MessageType.ERROR:
            return f"[{timestamp_str}] ERROR: {self.component} - {self.action}"
        elif self.message_type == MessageType.WARNING:
            return f"[{timestamp_str}] WARNING: {self.component} - {self.action}"
        elif self.message_type == MessageType.INFO:
            return f"[{timestamp_str}] INFO: {self.component} - {self.action}"
        elif self.message_type == MessageType.DEBUG:
            return f"[{timestamp_str}] DEBUG: {self.component} - {self.action}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "message_type": self.message_type.value,
            "component": self.component,
            "action": self.action,
            "data": self.data,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }
    
    def matches(self, component: Optional[str] = None, action: Optional[str] = None, 
                message_type: Optional[MessageType] = None) -> bool:
        """Check if this message matches the given criteria"""
        if component is not None and self.component != component:
            return False
        if action is not None and self.action != action:
            return False
        if message_type is not None and self.message_type != message_type:
            return False
        return True


class MessageLogger:
    """Logger for collecting and managing UI messages"""
    
    def __init__(self, collect_messages: bool = True, print_messages: bool = True):
        """
        Initialize the message logger
        
        Args:
            collect_messages: Whether to collect messages in memory
            print_messages: Whether to print messages to console
        """
        self.collect_messages = collect_messages
        self.print_messages = print_messages
        self.messages: List[UIMessage] = []
        self._message_counter = 0
    
    def log(self, message_type: MessageType, component: str, action: str, 
            data: Optional[Dict[str, Any]] = None, message_id: Optional[str] = None) -> UIMessage:
        """
        Log a message
        
        Args:
            message_type: Type of message
            component: UI component that generated the message
            action: Action or event that occurred
            data: Additional data associated with the message
            message_id: Optional unique identifier for the message
        
        Returns:
            The created UIMessage object
        """
        if data is None:
            data = {}
        
        if message_id is None:
            self._message_counter += 1
            message_id = f"msg_{self._message_counter}"
        
        message = UIMessage(
            message_type=message_type,
            component=component,
            action=action,
            data=data,
            message_id=message_id
        )
        
        if self.collect_messages:
            self.messages.append(message)
        
        if self.print_messages:
            print(str(message))
        
        return message
    
    def log_ui_event(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> UIMessage:
        """Log a UI event"""
        return self.log(MessageType.UI_EVENT, component, action, data)
    
    def log_user_action(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> UIMessage:
        """Log a user action"""
        return self.log(MessageType.USER_ACTION, component, action, data)
    
    def log_state_change(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> UIMessage:
        """Log a state change"""
        return self.log(MessageType.STATE_CHANGE, component, action, data)
    
    def log_error(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> UIMessage:
        """Log an error"""
        return self.log(MessageType.ERROR, component, action, data)
    
    def log_warning(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> UIMessage:
        """Log a warning"""
        return self.log(MessageType.WARNING, component, action, data)
    
    def log_info(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> UIMessage:
        """Log an info message"""
        return self.log(MessageType.INFO, component, action, data)
    
    def log_debug(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> UIMessage:
        """Log a debug message"""
        return self.log(MessageType.DEBUG, component, action, data)
    
    def get_messages(self, component: Optional[str] = None, action: Optional[str] = None,
                    message_type: Optional[MessageType] = None) -> List[UIMessage]:
        """Get messages matching the given criteria"""
        if not self.collect_messages:
            return []
        
        return [msg for msg in self.messages if msg.matches(component, action, message_type)]
    
    def get_messages_by_type(self, message_type: MessageType) -> List[UIMessage]:
        """Get all messages of a specific type"""
        return self.get_messages(message_type=message_type)
    
    def get_messages_by_component(self, component: str) -> List[UIMessage]:
        """Get all messages from a specific component"""
        return self.get_messages(component=component)
    
    def clear_messages(self) -> None:
        """Clear all collected messages"""
        self.messages.clear()
        self._message_counter = 0
    
    def get_message_count(self) -> int:
        """Get the total number of messages collected"""
        return len(self.messages)
    
    def has_message(self, component: Optional[str] = None, action: Optional[str] = None,
                   message_type: Optional[MessageType] = None) -> bool:
        """Check if any messages match the given criteria"""
        return len(self.get_messages(component, action, message_type)) > 0
    
    def get_latest_message(self, component: Optional[str] = None, action: Optional[str] = None,
                          message_type: Optional[MessageType] = None) -> Optional[UIMessage]:
        """Get the most recent message matching the given criteria"""
        matching_messages = self.get_messages(component, action, message_type)
        return matching_messages[-1] if matching_messages else None
    
    def export_messages(self, format: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """
        Export messages in the specified format
        
        Args:
            format: Export format ("dict" or "json")
        
        Returns:
            Exported messages in the specified format
        """
        if format == "dict":
            return [msg.to_dict() for msg in self.messages]
        elif format == "json":
            import json
            return json.dumps([msg.to_dict() for msg in self.messages], indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


class MessageCollector:
    """Helper class for testing with message collection"""
    
    def __init__(self) -> None:
        self.logger = MessageLogger(collect_messages=True, print_messages=False)
    
    def get_ui_events(self, component: Optional[str] = None) -> List[UIMessage]:
        """Get UI events for testing"""
        return self.logger.get_messages(component=component, message_type=MessageType.UI_EVENT)
    
    def get_user_actions(self, component: Optional[str] = None) -> List[UIMessage]:
        """Get user actions for testing"""
        return self.logger.get_messages(component=component, message_type=MessageType.USER_ACTION)
    
    def get_state_changes(self, component: Optional[str] = None) -> List[UIMessage]:
        """Get state changes for testing"""
        return self.logger.get_messages(component=component, message_type=MessageType.STATE_CHANGE)
    
    def get_errors(self) -> List[UIMessage]:
        """Get error messages for testing"""
        return self.logger.get_messages(message_type=MessageType.ERROR)
    
    def get_warnings(self) -> List[UIMessage]:
        """Get warning messages for testing"""
        return self.logger.get_messages(message_type=MessageType.WARNING)
    
    def get_messages(self, component: Optional[str] = None, 
                    message_type: Optional[MessageType] = None) -> List[UIMessage]:
        """Get all messages or filtered messages"""
        return self.logger.get_messages(component=component, message_type=message_type)
    
    def assert_message_sequence(self, expected_sequence: List[Dict[str, str]]) -> None:
        """
        Assert that messages appear in the expected sequence
        
        Args:
            expected_sequence: List of dicts with 'component', 'action', and optionally 'message_type'
        """
        messages = self.logger.messages
        assert len(messages) >= len(expected_sequence), \
            f"Expected at least {len(expected_sequence)} messages, got {len(messages)}"
        
        for i, expected in enumerate(expected_sequence):
            message = messages[i]
            assert message.component == expected['component'], \
                f"Message {i}: expected component '{expected['component']}', got '{message.component}'"
            assert message.action == expected['action'], \
                f"Message {i}: expected action '{expected['action']}', got '{message.action}'"
            if 'message_type' in expected:
                expected_type = MessageType(expected['message_type'])
                assert message.message_type == expected_type, \
                    f"Message {i}: expected type '{expected_type}', got '{message.message_type}'"
    
    def assert_ui_event(self, component: str, action: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Assert that a specific UI event occurred"""
        messages = self.get_ui_events(component)
        matching = [msg for msg in messages if msg.action == action]
        assert len(matching) > 0, f"No UI event found for {component}.{action}"
        
        if data:
            for msg in matching:
                if all(msg.data.get(k) == v for k, v in data.items()):
                    return
            assert False, f"UI event {component}.{action} found but data doesn't match: {data}"
    
    def assert_user_action(self, component: str, action: str) -> None:
        """Assert that a specific user action occurred"""
        messages = self.get_user_actions(component)
        matching = [msg for msg in messages if msg.action == action]
        assert len(matching) > 0, f"No user action found for {component}.{action}"
    
    def assert_state_change(self, component: str, action: str) -> None:
        """Assert that a specific state change occurred"""
        messages = self.get_state_changes(component)
        matching = [msg for msg in messages if msg.action == action]
        assert len(matching) > 0, f"No state change found for {component}.{action}"
    
    def clear(self) -> None:
        """Clear all collected messages"""
        self.logger.clear_messages()
    
    def get_logger(self) -> MessageLogger:
        """Get the underlying message logger"""
        return self.logger
