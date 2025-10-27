"""
Progress Tracking Utility for Streamlit Dashboard

This module provides real-time progress tracking capabilities for long-running
operations in the Streamlit dashboard. It integrates with the async processor
to provide visual feedback to users during background tasks.

Key Features:
- Real-time progress bars and status updates
- Integration with Streamlit components
- Support for nested progress tracking
- Automatic UI updates and refresh handling
- Error state visualization
- Cancellation support
"""

import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import uuid

from .async_processor import (
    AsyncProcessor, TaskResult, TaskStatus, TaskPriority,
    get_async_processor, submit_async_task, get_task_result, is_task_complete
)


class ProgressStyle(Enum):
    """Different styles for progress visualization."""
    BAR = "bar"
    SPINNER = "spinner"
    METRIC = "metric"
    STATUS = "status"


@dataclass
class ProgressConfig:
    """Configuration for progress tracking."""
    show_percentage: bool = True
    show_time_remaining: bool = True
    show_elapsed_time: bool = True
    auto_refresh_interval: float = 1.0
    style: ProgressStyle = ProgressStyle.BAR
    color_scheme: str = "default"  # default, success, warning, error
    show_cancel_button: bool = True
    show_details: bool = False


class ProgressTracker:
    """
    Main progress tracking class for Streamlit applications.
    
    This class provides a comprehensive progress tracking interface that
    integrates seamlessly with Streamlit's UI components and the async
    processing framework.
    """

    def __init__(self, config: Optional[ProgressConfig] = None):
        """
        Initialize the progress tracker.
        
        Args:
            config: Progress configuration options
        """
        self.config = config or ProgressConfig()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_containers: Dict[str, Any] = {}
        self.lock = threading.RLock()
        
        # Auto-refresh management
        self.last_refresh = datetime.now()
        self.refresh_needed = False

    def track_async_task(
        self,
        task_id: str,
        title: str = "Processing...",
        description: str = "",
        container: Optional[Any] = None,
        config: Optional[ProgressConfig] = None
    ) -> None:
        """
        Start tracking an async task with visual progress indicators.
        
        Args:
            task_id: ID of the task to track
            title: Display title for the progress
            description: Optional description text
            container: Streamlit container to render progress in
            config: Optional progress configuration override
        """
        task_config = config or self.config
        
        if container is None:
            container = st.container()
        
        with self.lock:
            self.active_tasks[task_id] = {
                'title': title,
                'description': description,
                'config': task_config,
                'start_time': datetime.now(),
                'last_update': datetime.now()
            }
            self.task_containers[task_id] = container
        
        # Initial render
        self._render_task_progress(task_id)

    def track_function_with_progress(
        self,
        func: Callable,
        *args,
        title: str = "Processing...",
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        config: Optional[ProgressConfig] = None,
        container: Optional[Any] = None,
        **kwargs
    ) -> str:
        """
        Submit a function for async execution with automatic progress tracking.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            title: Display title for the progress
            description: Optional description text
            priority: Task priority
            timeout: Task timeout in seconds
            config: Optional progress configuration
            container: Streamlit container to render progress in
            **kwargs: Keyword arguments for the function
            
        Returns:
            str: Task ID for tracking
        """
        # Submit the task
        task_id = submit_async_task(
            func, *args,
            priority=priority,
            timeout=timeout,
            **kwargs
        )
        
        # Start tracking
        self.track_async_task(
            task_id=task_id,
            title=title,
            description=description,
            container=container,
            config=config
        )
        
        return task_id

    def _render_task_progress(self, task_id: str) -> None:
        """
        Render progress for a specific task.
        
        Args:
            task_id: Task ID to render progress for
        """
        if task_id not in self.active_tasks or task_id not in self.task_containers:
            return
        
        task_info = self.active_tasks[task_id]
        container = self.task_containers[task_id]
        config = task_info['config']
        
        # Get current task result
        result = get_task_result(task_id)
        if not result:
            return
        
        with container:
            # Clear container and rebuild
            container.empty()
            
            # Title and description
            st.markdown(f"**{task_info['title']}**")
            if task_info['description']:
                st.markdown(task_info['description'])
            
            # Progress visualization based on style
            if config.style == ProgressStyle.BAR:
                self._render_progress_bar(task_id, result, config)
            elif config.style == ProgressStyle.SPINNER:
                self._render_spinner(task_id, result, config)
            elif config.style == ProgressStyle.METRIC:
                self._render_metric(task_id, result, config)
            elif config.style == ProgressStyle.STATUS:
                self._render_status(task_id, result, config)
            
            # Additional information
            if config.show_details:
                self._render_task_details(task_id, result, config)
            
            # Cancel button
            if config.show_cancel_button and result.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                if st.button(f"Cancel", key=f"cancel_{task_id}"):
                    self._cancel_task(task_id)

    def _render_progress_bar(self, task_id: str, result: TaskResult, config: ProgressConfig) -> None:
        """Render a progress bar for the task."""
        progress_value = result.progress
        
        # Color based on status
        if result.status == TaskStatus.FAILED:
            st.error(f"❌ {result.progress_message}")
        elif result.status == TaskStatus.COMPLETED:
            st.success(f"✅ {result.progress_message}")
        elif result.status == TaskStatus.CANCELLED:
            st.warning(f"⚠️ {result.progress_message}")
        else:
            # Show progress bar
            st.progress(progress_value)
            
            # Progress text
            progress_text = result.progress_message
            if config.show_percentage:
                progress_text += f" ({progress_value:.1%})"
            
            st.text(progress_text)
        
        # Time information
        self._render_time_info(task_id, result, config)

    def _render_spinner(self, task_id: str, result: TaskResult, config: ProgressConfig) -> None:
        """Render a spinner for the task."""
        if result.status == TaskStatus.RUNNING:
            with st.spinner(result.progress_message):
                time.sleep(0.1)  # Brief pause for visual effect
        elif result.status == TaskStatus.COMPLETED:
            st.success(f"✅ {result.progress_message}")
        elif result.status == TaskStatus.FAILED:
            st.error(f"❌ {result.progress_message}")
        elif result.status == TaskStatus.CANCELLED:
            st.warning(f"⚠️ {result.progress_message}")
        else:
            st.info(f"⏳ {result.progress_message}")

    def _render_metric(self, task_id: str, result: TaskResult, config: ProgressConfig) -> None:
        """Render metrics for the task."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_emoji = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.RUNNING: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.CANCELLED: "⚠️"
            }
            st.metric("Status", f"{status_emoji.get(result.status, '❓')} {result.status.value.title()}")
        
        with col2:
            if config.show_percentage:
                st.metric("Progress", f"{result.progress:.1%}")
        
        with col3:
            if result.duration:
                st.metric("Duration", f"{result.duration.total_seconds():.1f}s")
            elif result.start_time:
                elapsed = datetime.now() - result.start_time
                st.metric("Elapsed", f"{elapsed.total_seconds():.1f}s")

    def _render_status(self, task_id: str, result: TaskResult, config: ProgressConfig) -> None:
        """Render simple status for the task."""
        status_colors = {
            TaskStatus.PENDING: "🔵",
            TaskStatus.RUNNING: "🟡",
            TaskStatus.COMPLETED: "🟢",
            TaskStatus.FAILED: "🔴",
            TaskStatus.CANCELLED: "🟠"
        }
        
        status_color = status_colors.get(result.status, "⚪")
        st.markdown(f"{status_color} **{result.status.value.title()}**: {result.progress_message}")

    def _render_time_info(self, task_id: str, result: TaskResult, config: ProgressConfig) -> None:
        """Render time information for the task."""
        if not (config.show_elapsed_time or config.show_time_remaining):
            return
        
        time_cols = st.columns(2)
        
        if config.show_elapsed_time:
            with time_cols[0]:
                if result.start_time:
                    if result.end_time:
                        elapsed = result.end_time - result.start_time
                    else:
                        elapsed = datetime.now() - result.start_time
                    st.text(f"Elapsed: {elapsed.total_seconds():.1f}s")
        
        if config.show_time_remaining and result.status == TaskStatus.RUNNING:
            with time_cols[1]:
                if result.progress > 0 and result.start_time:
                    elapsed = datetime.now() - result.start_time
                    estimated_total = elapsed.total_seconds() / result.progress
                    remaining = estimated_total - elapsed.total_seconds()
                    if remaining > 0:
                        st.text(f"Remaining: ~{remaining:.1f}s")

    def _render_task_details(self, task_id: str, result: TaskResult, config: ProgressConfig) -> None:
        """Render detailed task information."""
        with st.expander("Task Details", expanded=False):
            st.text(f"Task ID: {task_id}")
            st.text(f"Status: {result.status.value}")
            st.text(f"Progress: {result.progress:.1%}")
            
            if result.start_time:
                st.text(f"Started: {result.start_time.strftime('%H:%M:%S')}")
            
            if result.end_time:
                st.text(f"Ended: {result.end_time.strftime('%H:%M:%S')}")
            
            if result.error:
                st.error(f"Error: {result.error}")
            
            if result.metadata:
                st.json(result.metadata)

    def _cancel_task(self, task_id: str) -> None:
        """Cancel a task and update the UI."""
        processor = get_async_processor()
        if processor.cancel_task(task_id):
            st.warning(f"Task {task_id} has been cancelled")
            st.rerun()

    def update_all_tracked_tasks(self) -> None:
        """Update all currently tracked tasks."""
        current_time = datetime.now()
        
        # Check if refresh is needed
        if current_time - self.last_refresh < timedelta(seconds=self.config.auto_refresh_interval):
            return
        
        with self.lock:
            tasks_to_remove = []
            
            for task_id in list(self.active_tasks.keys()):
                result = get_task_result(task_id)
                
                if result and result.is_complete:
                    # Task is complete, render final state and mark for removal
                    self._render_task_progress(task_id)
                    
                    # Remove after a delay to show final state
                    task_info = self.active_tasks[task_id]
                    if current_time - task_info['last_update'] > timedelta(seconds=3):
                        tasks_to_remove.append(task_id)
                else:
                    # Task is still running, update progress
                    self._render_task_progress(task_id)
                    if task_id in self.active_tasks:
                        self.active_tasks[task_id]['last_update'] = current_time
            
            # Clean up completed tasks
            for task_id in tasks_to_remove:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                if task_id in self.task_containers:
                    del self.task_containers[task_id]
        
        self.last_refresh = current_time

    def get_active_task_count(self) -> int:
        """Get the number of currently tracked tasks."""
        with self.lock:
            return len(self.active_tasks)

    def clear_completed_tasks(self) -> None:
        """Clear all completed tasks from tracking."""
        with self.lock:
            tasks_to_remove = []
            
            for task_id in self.active_tasks.keys():
                if is_task_complete(task_id):
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                if task_id in self.task_containers:
                    del self.task_containers[task_id]


# Global progress tracker instance
_global_tracker: Optional[ProgressTracker] = None


def get_progress_tracker() -> ProgressTracker:
    """
    Get the global progress tracker instance.
    
    Returns:
        ProgressTracker instance
    """
    global _global_tracker
    
    if _global_tracker is None:
        _global_tracker = ProgressTracker()
    
    return _global_tracker


def track_async_task(
    task_id: str,
    title: str = "Processing...",
    description: str = "",
    container: Optional[Any] = None,
    config: Optional[ProgressConfig] = None
) -> None:
    """
    Convenience function to track an async task with the global tracker.
    
    Args:
        task_id: ID of the task to track
        title: Display title for the progress
        description: Optional description text
        container: Streamlit container to render progress in
        config: Optional progress configuration override
    """
    tracker = get_progress_tracker()
    tracker.track_async_task(task_id, title, description, container, config)


def track_function_with_progress(
    func: Callable,
    *args,
    title: str = "Processing...",
    description: str = "",
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = None,
    config: Optional[ProgressConfig] = None,
    container: Optional[Any] = None,
    **kwargs
) -> str:
    """
    Convenience function to submit and track a function with the global tracker.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        title: Display title for the progress
        description: Optional description text
        priority: Task priority
        timeout: Task timeout in seconds
        config: Optional progress configuration
        container: Streamlit container to render progress in
        **kwargs: Keyword arguments for the function
        
    Returns:
        str: Task ID for tracking
    """
    tracker = get_progress_tracker()
    return tracker.track_function_with_progress(
        func, *args,
        title=title,
        description=description,
        priority=priority,
        timeout=timeout,
        config=config,
        container=container,
        **kwargs
    )


def update_all_progress() -> None:
    """
    Convenience function to update all tracked progress with the global tracker.
    """
    tracker = get_progress_tracker()
    tracker.update_all_tracked_tasks()


# Streamlit component integration
def st_progress_container(key: Optional[str] = None) -> Any:
    """
    Create a Streamlit container specifically for progress tracking.
    
    Args:
        key: Optional key for the container
        
    Returns:
        Streamlit container
    """
    if key:
        return st.container(key=key)
    else:
        return st.container()


def st_async_button(
    label: str,
    func: Callable,
    *args,
    key: Optional[str] = None,
    help: Optional[str] = None,
    disabled: bool = False,
    progress_title: Optional[str] = None,
    progress_description: str = "",
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = None,
    config: Optional[ProgressConfig] = None,
    **kwargs
) -> Optional[str]:
    """
    Create a Streamlit button that executes a function asynchronously with progress tracking.
    
    Args:
        label: Button label
        func: Function to execute when clicked
        *args: Positional arguments for the function
        key: Optional button key
        help: Optional help text
        disabled: Whether button is disabled
        progress_title: Title for progress tracking (defaults to button label)
        progress_description: Description for progress tracking
        priority: Task priority
        timeout: Task timeout in seconds
        config: Optional progress configuration
        **kwargs: Keyword arguments for the function
        
    Returns:
        Task ID if button was clicked and task submitted, None otherwise
    """
    if st.button(label, key=key, help=help, disabled=disabled):
        title = progress_title or f"Executing: {label}"
        
        # Create progress container
        progress_container = st.container()
        
        # Submit and track the task
        task_id = track_function_with_progress(
            func, *args,
            title=title,
            description=progress_description,
            priority=priority,
            timeout=timeout,
            config=config,
            container=progress_container,
            **kwargs
        )
        
        return task_id
    
    return None