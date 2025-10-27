"""
UI Enhancement Utilities for Streamlit Dashboard

This module provides utilities for enhanced user interface components,
including loading states, error handling, notifications, and improved
user experience elements.
"""

import streamlit as st
import time
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
import logging
from datetime import datetime, timedelta
import traceback

# Configure logging
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications."""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class LoadingStyle(Enum):
    """Loading indicator styles."""
    SPINNER = "spinner"
    PROGRESS_BAR = "progress_bar"
    DOTS = "dots"
    PULSE = "pulse"

@dataclass
class LoadingConfig:
    """Configuration for loading indicators."""
    style: LoadingStyle = LoadingStyle.SPINNER
    message: str = "Loading..."
    show_time: bool = True
    auto_hide: bool = True
    timeout_seconds: int = 30

@dataclass
class ErrorConfig:
    """Configuration for error handling."""
    show_details: bool = False
    show_traceback: bool = False
    auto_retry: bool = False
    max_retries: int = 3
    retry_delay: float = 1.0

class LoadingIndicator:
    """
    Enhanced loading indicator with multiple styles and configurations.
    """
    
    def __init__(self, config: Optional[LoadingConfig] = None):
        """
        Initialize loading indicator.
        
        Args:
            config: Loading configuration
        """
        self.config = config or LoadingConfig()
        self._start_time = None
        self._container = None
        self._progress_bar = None
        self._status_text = None
    
    def __enter__(self):
        """Enter context manager."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.stop()
    
    def start(self, container: Optional[st.container] = None):
        """
        Start the loading indicator.
        
        Args:
            container: Optional Streamlit container
        """
        self._start_time = time.time()
        self._container = container or st
        
        if self.config.style == LoadingStyle.SPINNER:
            self._show_spinner()
        elif self.config.style == LoadingStyle.PROGRESS_BAR:
            self._show_progress_bar()
        elif self.config.style == LoadingStyle.DOTS:
            self._show_dots()
        elif self.config.style == LoadingStyle.PULSE:
            self._show_pulse()
    
    def stop(self):
        """Stop the loading indicator."""
        if self.config.auto_hide and self._container:
            # Clear the loading indicator
            if hasattr(self._container, 'empty'):
                self._container.empty()
    
    def update(self, progress: float = None, message: str = None):
        """
        Update the loading indicator.
        
        Args:
            progress: Progress value (0-1)
            message: Updated message
        """
        if message:
            self.config.message = message
        
        if self._progress_bar and progress is not None:
            self._progress_bar.progress(progress)
        
        if self._status_text:
            elapsed = time.time() - self._start_time if self._start_time else 0
            time_str = f" ({elapsed:.1f}s)" if self.config.show_time else ""
            self._status_text.text(f"{self.config.message}{time_str}")
    
    def _show_spinner(self):
        """Show spinner loading indicator."""
        with self._container.spinner(self.config.message):
            pass
    
    def _show_progress_bar(self):
        """Show progress bar loading indicator."""
        self._progress_bar = self._container.progress(0)
        self._status_text = self._container.empty()
        self.update(0)
    
    def _show_dots(self):
        """Show dots loading indicator."""
        self._status_text = self._container.empty()
        # Animate dots
        for i in range(4):
            dots = "." * (i % 4)
            self._status_text.text(f"{self.config.message}{dots}")
            time.sleep(0.5)
    
    def _show_pulse(self):
        """Show pulse loading indicator."""
        self._status_text = self._container.empty()
        self._status_text.markdown(f"🔄 {self.config.message}")

class ErrorHandler:
    """
    Enhanced error handler with retry logic and user-friendly messages.
    """
    
    def __init__(self, config: Optional[ErrorConfig] = None):
        """
        Initialize error handler.
        
        Args:
            config: Error handling configuration
        """
        self.config = config or ErrorConfig()
        self._retry_count = 0
    
    def handle_error(
        self, 
        error: Exception, 
        container: Optional[st.container] = None,
        context: str = "Operation"
    ):
        """
        Handle an error with user-friendly display.
        
        Args:
            error: The exception that occurred
            container: Optional Streamlit container
            context: Context description for the error
        """
        container = container or st
        
        # Log the error
        logger.error(f"Error in {context}: {error}", exc_info=True)
        
        # Display user-friendly error message
        with container.container():
            st.error(f"❌ {context} failed: {str(error)}")
            
            if self.config.show_details:
                with st.expander("Error Details", expanded=False):
                    st.code(str(error))
                    
                    if self.config.show_traceback:
                        st.code(traceback.format_exc())
            
            # Show retry option if enabled
            if self.config.auto_retry and self._retry_count < self.config.max_retries:
                if st.button(f"Retry ({self.config.max_retries - self._retry_count} attempts left)"):
                    self._retry_count += 1
                    time.sleep(self.config.retry_delay)
                    return True  # Indicate retry requested
        
        return False
    
    @contextmanager
    def error_boundary(self, context: str = "Operation", container: Optional[st.container] = None):
        """
        Context manager for error handling.
        
        Args:
            context: Context description
            container: Optional Streamlit container
        """
        try:
            yield
        except Exception as e:
            self.handle_error(e, container, context)
            raise

class NotificationManager:
    """
    Notification manager for displaying user feedback.
    """
    
    def __init__(self):
        """Initialize notification manager."""
        self._notifications = []
    
    def show(
        self, 
        message: str, 
        notification_type: NotificationType = NotificationType.INFO,
        container: Optional[st.container] = None,
        duration: Optional[float] = None
    ):
        """
        Show a notification.
        
        Args:
            message: Notification message
            notification_type: Type of notification
            container: Optional Streamlit container
            duration: Auto-hide duration in seconds
        """
        container = container or st
        
        # Create notification
        notification = {
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now(),
            'container': container
        }
        
        # Display notification
        if notification_type == NotificationType.SUCCESS:
            container.success(f"✅ {message}")
        elif notification_type == NotificationType.INFO:
            container.info(f"ℹ️ {message}")
        elif notification_type == NotificationType.WARNING:
            container.warning(f"⚠️ {message}")
        elif notification_type == NotificationType.ERROR:
            container.error(f"❌ {message}")
        
        self._notifications.append(notification)
        
        # Auto-hide if duration specified
        if duration:
            time.sleep(duration)
            self.clear_last()
    
    def clear_last(self):
        """Clear the last notification."""
        if self._notifications:
            notification = self._notifications.pop()
            if hasattr(notification['container'], 'empty'):
                notification['container'].empty()
    
    def clear_all(self):
        """Clear all notifications."""
        for notification in self._notifications:
            if hasattr(notification['container'], 'empty'):
                notification['container'].empty()
        self._notifications.clear()

class PerformanceMonitor:
    """
    Performance monitoring for UI operations.
    """
    
    def __init__(self):
        """Initialize performance monitor."""
        self._metrics = {}
        self._start_times = {}
    
    def start_timer(self, operation: str):
        """
        Start timing an operation.
        
        Args:
            operation: Operation name
        """
        self._start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """
        End timing an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Elapsed time in seconds
        """
        if operation in self._start_times:
            elapsed = time.time() - self._start_times[operation]
            self._metrics[operation] = elapsed
            del self._start_times[operation]
            return elapsed
        return 0.0
    
    @contextmanager
    def time_operation(self, operation: str):
        """
        Context manager for timing operations.
        
        Args:
            operation: Operation name
        """
        self.start_timer(operation)
        try:
            yield
        finally:
            self.end_timer(operation)
    
    def get_metrics(self) -> Dict[str, float]:
        """
        Get performance metrics.
        
        Returns:
            Dictionary of operation times
        """
        return self._metrics.copy()
    
    def display_metrics(self, container: Optional[st.container] = None):
        """
        Display performance metrics.
        
        Args:
            container: Optional Streamlit container
        """
        container = container or st
        
        if self._metrics:
            with container.expander("Performance Metrics", expanded=False):
                for operation, duration in self._metrics.items():
                    st.metric(
                        label=operation,
                        value=f"{duration:.3f}s",
                        delta=None
                    )

class UIEnhancer:
    """
    Main UI enhancer class that combines all enhancement utilities.
    """
    
    def __init__(self):
        """Initialize UI enhancer."""
        self.notifications = NotificationManager()
        self.performance = PerformanceMonitor()
    
    def create_loading_context(
        self, 
        message: str = "Loading...",
        style: LoadingStyle = LoadingStyle.SPINNER,
        container: Optional[st.container] = None
    ):
        """
        Create a loading context.
        
        Args:
            message: Loading message
            style: Loading style
            container: Optional Streamlit container
            
        Returns:
            LoadingIndicator context manager
        """
        config = LoadingConfig(style=style, message=message)
        indicator = LoadingIndicator(config)
        if container:
            indicator.start(container)
        return indicator
    
    def create_error_boundary(
        self,
        context: str = "Operation",
        show_details: bool = False,
        container: Optional[st.container] = None
    ):
        """
        Create an error boundary.
        
        Args:
            context: Context description
            show_details: Whether to show error details
            container: Optional Streamlit container
            
        Returns:
            ErrorHandler context manager
        """
        config = ErrorConfig(show_details=show_details)
        handler = ErrorHandler(config)
        return handler.error_boundary(context, container)
    
    def show_success(self, message: str, container: Optional[st.container] = None):
        """Show success notification."""
        self.notifications.show(message, NotificationType.SUCCESS, container)
    
    def show_error(self, message: str, container: Optional[st.container] = None):
        """Show error notification."""
        self.notifications.show(message, NotificationType.ERROR, container)
    
    def show_warning(self, message: str, container: Optional[st.container] = None):
        """Show warning notification."""
        self.notifications.show(message, NotificationType.WARNING, container)
    
    def show_info(self, message: str, container: Optional[st.container] = None):
        """Show info notification."""
        self.notifications.show(message, NotificationType.INFO, container)

# Global UI enhancer instance
ui_enhancer = UIEnhancer()

# Convenience functions
def with_loading(
    message: str = "Loading...",
    style: LoadingStyle = LoadingStyle.SPINNER,
    container: Optional[st.container] = None
):
    """
    Decorator for adding loading indicators to functions.
    
    Args:
        message: Loading message
        style: Loading style
        container: Optional Streamlit container
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with ui_enhancer.create_loading_context(message, style, container):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def with_error_handling(
    context: str = "Operation",
    show_details: bool = False,
    container: Optional[st.container] = None
):
    """
    Decorator for adding error handling to functions.
    
    Args:
        context: Context description
        show_details: Whether to show error details
        container: Optional Streamlit container
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with ui_enhancer.create_error_boundary(context, show_details, container):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def with_performance_monitoring(operation: str):
    """
    Decorator for monitoring function performance.
    
    Args:
        operation: Operation name
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with ui_enhancer.performance.time_operation(operation):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Streamlit component helpers
def st_loading_button(
    label: str,
    key: Optional[str] = None,
    loading_message: str = "Processing...",
    **button_kwargs
) -> bool:
    """
    Create a button with loading state.
    
    Args:
        label: Button label
        key: Button key
        loading_message: Message to show while loading
        **button_kwargs: Additional button arguments
        
    Returns:
        True if button was clicked
    """
    if st.button(label, key=key, **button_kwargs):
        with st.spinner(loading_message):
            return True
    return False

def st_error_container(
    error: Exception,
    context: str = "Operation",
    show_details: bool = False
):
    """
    Create an error display container.
    
    Args:
        error: The exception to display
        context: Context description
        show_details: Whether to show error details
    """
    st.error(f"❌ {context} failed: {str(error)}")
    
    if show_details:
        with st.expander("Error Details", expanded=False):
            st.code(str(error))
            st.code(traceback.format_exc())

def st_success_toast(message: str, duration: float = 3.0):
    """
    Show a success toast notification.
    
    Args:
        message: Success message
        duration: Display duration in seconds
    """
    placeholder = st.empty()
    placeholder.success(f"✅ {message}")
    time.sleep(duration)
    placeholder.empty()