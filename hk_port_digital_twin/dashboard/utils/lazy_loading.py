"""
Lazy loading utilities for dashboard sections and components.

This module provides lazy loading decorators and components to improve initial page load times
by deferring the rendering of heavy sections until they are actually needed.
"""

import functools
import time
import logging
from typing import Any, Dict, Optional, Callable, Union
import streamlit as st
import threading
from concurrent.futures import ThreadPoolExecutor, Future

logger = logging.getLogger(__name__)

class LazyLoadManager:
    """Manages lazy loading state and execution for dashboard components."""
    
    def __init__(self):
        self._loaded_sections = set()
        self._loading_sections = set()
        self._section_futures = {}
        self._executor = ThreadPoolExecutor(max_workers=3)
        self._section_data_cache = {}
        
    def is_section_loaded(self, section_id: str) -> bool:
        """Check if a section has been loaded."""
        return section_id in self._loaded_sections
    
    def is_section_loading(self, section_id: str) -> bool:
        """Check if a section is currently loading."""
        return section_id in self._loading_sections
    
    def mark_section_loaded(self, section_id: str) -> None:
        """Mark a section as loaded."""
        self._loaded_sections.add(section_id)
        self._loading_sections.discard(section_id)
        
    def mark_section_loading(self, section_id: str) -> None:
        """Mark a section as currently loading."""
        self._loading_sections.add(section_id)
    
    def get_section_data(self, section_id: str) -> Optional[Any]:
        """Get cached data for a section."""
        return self._section_data_cache.get(section_id)
    
    def set_section_data(self, section_id: str, data: Any) -> None:
        """Cache data for a section."""
        self._section_data_cache[section_id] = data
    
    def submit_async_load(self, section_id: str, load_func: Callable, *args, **kwargs) -> Future:
        """Submit an async loading task for a section."""
        if section_id in self._section_futures:
            return self._section_futures[section_id]
        
        future = self._executor.submit(load_func, *args, **kwargs)
        self._section_futures[section_id] = future
        self.mark_section_loading(section_id)
        
        return future
    
    def get_async_result(self, section_id: str) -> Optional[Any]:
        """Get the result of an async loading task if completed."""
        if section_id not in self._section_futures:
            return None
        
        future = self._section_futures[section_id]
        if future.done():
            try:
                result = future.result()
                self.mark_section_loaded(section_id)
                self.set_section_data(section_id, result)
                return result
            except Exception as e:
                logger.error(f"Error in async loading for section {section_id}: {e}")
                self._loading_sections.discard(section_id)
                return None
        
        return None
    
    def clear_section(self, section_id: str) -> None:
        """Clear all data and state for a section."""
        self._loaded_sections.discard(section_id)
        self._loading_sections.discard(section_id)
        self._section_data_cache.pop(section_id, None)
        if section_id in self._section_futures:
            future = self._section_futures.pop(section_id)
            future.cancel()

# Global lazy load manager
_lazy_manager = LazyLoadManager()

def get_lazy_manager() -> LazyLoadManager:
    """Get the global lazy load manager."""
    return _lazy_manager

def lazy_section(section_id: str, 
                load_threshold: str = "expanded",
                show_loading_spinner: bool = True,
                loading_message: str = "Loading section..."):
    """
    Decorator for lazy loading of section rendering functions.
    
    Args:
        section_id: Unique identifier for the section
        load_threshold: When to trigger loading ('expanded', 'visible', 'immediate')
        show_loading_spinner: Whether to show a loading spinner
        loading_message: Message to display while loading
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if section should be loaded based on threshold
            should_load = _should_load_section(section_id, load_threshold)
            
            if not should_load:
                # Show placeholder or nothing
                _render_section_placeholder(section_id, load_threshold)
                return None
            
            # Check if already loaded
            if _lazy_manager.is_section_loaded(section_id):
                cached_data = _lazy_manager.get_section_data(section_id)
                if cached_data is not None:
                    return cached_data
            
            # Check if currently loading
            if _lazy_manager.is_section_loading(section_id):
                if show_loading_spinner:
                    with st.spinner(loading_message):
                        # Check for async result
                        result = _lazy_manager.get_async_result(section_id)
                        if result is not None:
                            return result
                        
                        # If still loading, show loading state
                        st.info(f"⏳ {loading_message}")
                        time.sleep(0.1)  # Small delay to prevent excessive rerunning
                        st.rerun()
                return None
            
            # Start loading
            try:
                _lazy_manager.mark_section_loading(section_id)
                
                if show_loading_spinner:
                    with st.spinner(loading_message):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                _lazy_manager.mark_section_loaded(section_id)
                _lazy_manager.set_section_data(section_id, result)
                return result
                
            except Exception as e:
                logger.error(f"Error loading section {section_id}: {e}")
                _lazy_manager._loading_sections.discard(section_id)
                st.error(f"Error loading section: {e}")
                return None
        
        # Add utility methods to the wrapper
        wrapper.clear_cache = lambda: _lazy_manager.clear_section(section_id)
        wrapper.is_loaded = lambda: _lazy_manager.is_section_loaded(section_id)
        wrapper.force_reload = lambda: (
            _lazy_manager.clear_section(section_id),
            wrapper(*args, **kwargs)
        )
        
        return wrapper
    return decorator

def lazy_component(component_id: str, 
                  dependencies: Optional[list] = None,
                  cache_duration: int = 300):
    """
    Decorator for lazy loading of individual components within sections.
    
    Args:
        component_id: Unique identifier for the component
        dependencies: List of dependencies that trigger reload when changed
        cache_duration: How long to cache the component (seconds)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check cache validity
            cached_data = _lazy_manager.get_section_data(component_id)
            if cached_data is not None:
                cache_time = cached_data.get('_cache_time', 0)
                if time.time() - cache_time < cache_duration:
                    # Check dependencies
                    if _dependencies_unchanged(component_id, dependencies):
                        return cached_data.get('data')
            
            # Load component
            try:
                result = func(*args, **kwargs)
                
                # Cache with metadata
                cache_entry = {
                    'data': result,
                    '_cache_time': time.time(),
                    '_dependencies': _get_dependency_hash(dependencies) if dependencies else None
                }
                _lazy_manager.set_section_data(component_id, cache_entry)
                
                return result
                
            except Exception as e:
                logger.error(f"Error loading component {component_id}: {e}")
                st.error(f"Error loading component: {e}")
                return None
        
        return wrapper
    return decorator

def async_section_loader(section_id: str, 
                        load_func: Callable,
                        *args, **kwargs) -> bool:
    """
    Start async loading of a section.
    
    Args:
        section_id: Unique identifier for the section
        load_func: Function to load the section data
        *args, **kwargs: Arguments for the load function
        
    Returns:
        True if loading started, False if already loading/loaded
    """
    if _lazy_manager.is_section_loaded(section_id) or _lazy_manager.is_section_loading(section_id):
        return False
    
    _lazy_manager.submit_async_load(section_id, load_func, *args, **kwargs)
    return True

def check_async_section(section_id: str) -> Optional[Any]:
    """
    Check if an async section has finished loading.
    
    Args:
        section_id: Unique identifier for the section
        
    Returns:
        Section data if loaded, None if still loading or not started
    """
    return _lazy_manager.get_async_result(section_id)

def _should_load_section(section_id: str, threshold: str) -> bool:
    """Determine if a section should be loaded based on the threshold."""
    if threshold == "immediate":
        return True
    elif threshold == "expanded":
        # Check if section is expanded in session state
        section_key = f"{section_id}_expanded"
        return st.session_state.get(section_key, False)
    elif threshold == "visible":
        # For now, treat as expanded (could be enhanced with viewport detection)
        section_key = f"{section_id}_expanded"
        return st.session_state.get(section_key, False)
    
    return False

def _render_section_placeholder(section_id: str, threshold: str) -> None:
    """Render a placeholder for a section that hasn't been loaded yet."""
    if threshold == "expanded":
        # Don't render anything if not expanded
        return
    elif threshold == "visible":
        # Show a minimal placeholder
        st.empty()

def _dependencies_unchanged(component_id: str, dependencies: Optional[list]) -> bool:
    """Check if component dependencies have changed."""
    if not dependencies:
        return True
    
    cached_data = _lazy_manager.get_section_data(component_id)
    if not cached_data:
        return False
    
    current_hash = _get_dependency_hash(dependencies)
    cached_hash = cached_data.get('_dependencies')
    
    return current_hash == cached_hash

def _get_dependency_hash(dependencies: list) -> str:
    """Generate a hash for dependency values."""
    import hashlib
    
    dep_values = []
    for dep in dependencies:
        if isinstance(dep, str) and dep.startswith('st.session_state.'):
            # Extract session state value
            key = dep.replace('st.session_state.', '')
            value = st.session_state.get(key, None)
            dep_values.append(str(value))
        else:
            dep_values.append(str(dep))
    
    return hashlib.md5('|'.join(dep_values).encode()).hexdigest()

# Context manager for lazy loading sections
class LazySection:
    """Context manager for lazy loading sections with automatic cleanup."""
    
    def __init__(self, section_id: str, 
                 load_threshold: str = "expanded",
                 auto_cleanup: bool = True):
        self.section_id = section_id
        self.load_threshold = load_threshold
        self.auto_cleanup = auto_cleanup
        self.should_render = False
    
    def __enter__(self):
        self.should_render = _should_load_section(self.section_id, self.load_threshold)
        if self.should_render:
            _lazy_manager.mark_section_loading(self.section_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.should_render:
            if exc_type is None:
                _lazy_manager.mark_section_loaded(self.section_id)
            else:
                _lazy_manager._loading_sections.discard(self.section_id)
                if self.auto_cleanup:
                    _lazy_manager.clear_section(self.section_id)
    
    def render_if_needed(self, render_func: Callable, *args, **kwargs):
        """Render the section content if it should be loaded."""
        if self.should_render:
            return render_func(*args, **kwargs)
        return None

# Utility functions
def clear_all_lazy_cache():
    """Clear all lazy loading cache."""
    global _lazy_manager
    _lazy_manager = LazyLoadManager()

def get_lazy_loading_stats() -> Dict[str, Any]:
    """Get statistics about lazy loading performance."""
    return {
        'loaded_sections': len(_lazy_manager._loaded_sections),
        'loading_sections': len(_lazy_manager._loading_sections),
        'cached_sections': len(_lazy_manager._section_data_cache),
        'active_futures': len(_lazy_manager._section_futures),
        'loaded_section_ids': list(_lazy_manager._loaded_sections),
        'loading_section_ids': list(_lazy_manager._loading_sections)
    }

def preload_sections(section_ids: list, load_functions: Dict[str, Callable]):
    """Preload multiple sections asynchronously."""
    for section_id in section_ids:
        if section_id in load_functions:
            async_section_loader(section_id, load_functions[section_id])

# Streamlit-specific lazy loading components
def lazy_expander(label: str, section_id: str, 
                 expanded: bool = False,
                 lazy_content_func: Optional[Callable] = None):
    """Create a lazy-loading expander that only renders content when expanded."""
    
    # Create expander
    with st.expander(label, expanded=expanded) as expander:
        # Check if expanded
        if expanded or st.session_state.get(f"{section_id}_expanded", False):
            # Update session state
            st.session_state[f"{section_id}_expanded"] = True
            
            # Render content if function provided
            if lazy_content_func:
                with LazySection(section_id, "expanded") as lazy_section:
                    lazy_section.render_if_needed(lazy_content_func)
        else:
            # Mark as not expanded
            st.session_state[f"{section_id}_expanded"] = False
    
    return expander