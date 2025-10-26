"""
Session State Manager for Streamlit Dashboard

This module provides optimized session state management for the dashboard,
reducing redundant checks and improving performance.
"""

import streamlit as st
from typing import Any, Dict, Optional, Set, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import state tracker for performance monitoring
try:
    from .state_tracker import track_state_change
    STATE_TRACKING_ENABLED = True
except ImportError:
    STATE_TRACKING_ENABLED = False
    logger.warning("State tracking not available")


class SessionStateManager:
    """
    Optimized session state manager that reduces redundant operations
    and provides efficient state management for dashboard components.
    """
    
    def __init__(self):
        """Initialize the session state manager."""
        self._initialized_keys: Set[str] = set()
        self._cached_values: Dict[str, Any] = {}
        self._change_callbacks: Dict[str, Callable] = {}
        self._last_check_time = datetime.now()
        
    def initialize_key(self, key: str, default_value: Any, force_reinit: bool = False) -> bool:
        """
        Initialize a session state key with a default value if it doesn't exist.
        
        Args:
            key: Session state key
            default_value: Default value to set
            force_reinit: Force reinitialization even if key exists
            
        Returns:
            True if key was initialized/reinitialized, False if already existed
        """
        if force_reinit or key not in st.session_state:
            st.session_state[key] = default_value
            self._initialized_keys.add(key)
            self._cached_values[key] = default_value
            return True
        
        # Cache the existing value
        if key not in self._cached_values:
            self._cached_values[key] = st.session_state[key]
            
        return False
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from session state with caching for performance.
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
            
        Returns:
            Value from session state or default
        """
        # Use cached value if available and recent
        if key in self._cached_values:
            return self._cached_values[key]
            
        # Get from session state and cache
        value = st.session_state.get(key, default)
        self._cached_values[key] = value
        return value
    
    def set_value(self, key: str, value: Any, trigger_callback: bool = True, component: Optional[str] = None) -> bool:
        """
        Set a value in session state with change detection and performance tracking.
        
        Args:
            key: Session state key
            value: Value to set
            trigger_callback: Whether to trigger change callback
            component: Component name for tracking purposes
            
        Returns:
            True if value changed, False otherwise
        """
        old_value = self.get_value(key)
        
        if old_value != value:
            st.session_state[key] = value
            self._cached_values[key] = value
            
            # Track state change for performance monitoring
            if STATE_TRACKING_ENABLED:
                try:
                    track_state_change(key, old_value, value, component=component)
                except Exception as e:
                    logger.error(f"Error tracking state change for {key}: {e}")
            
            # Trigger callback if registered and requested
            if trigger_callback and key in self._change_callbacks:
                try:
                    self._change_callbacks[key](old_value, value)
                except Exception as e:
                    logger.error(f"Error in change callback for {key}: {e}")
            
            return True
        
        return False
    
    def register_change_callback(self, key: str, callback: Callable[[Any, Any], None]) -> None:
        """
        Register a callback to be called when a session state value changes.
        
        Args:
            key: Session state key to monitor
            callback: Function to call with (old_value, new_value)
        """
        self._change_callbacks[key] = callback
    
    def batch_initialize(self, key_defaults: Dict[str, Any], force_reinit: bool = False) -> Set[str]:
        """
        Initialize multiple session state keys in a batch operation.
        
        Args:
            key_defaults: Dictionary of key -> default_value pairs
            force_reinit: Force reinitialization of all keys
            
        Returns:
            Set of keys that were initialized/reinitialized
        """
        initialized_keys = set()
        
        for key, default_value in key_defaults.items():
            if self.initialize_key(key, default_value, force_reinit):
                initialized_keys.add(key)
                
        return initialized_keys
    
    def clear_cache(self, keys: Optional[Set[str]] = None) -> None:
        """
        Clear cached values for specified keys or all keys.
        
        Args:
            keys: Set of keys to clear, or None to clear all
        """
        if keys is None:
            self._cached_values.clear()
        else:
            for key in keys:
                self._cached_values.pop(key, None)
    
    def get_cached_keys(self) -> Set[str]:
        """Get set of currently cached keys."""
        return set(self._cached_values.keys())
    
    def cleanup_stale_cache(self, max_age_seconds: int = 300) -> None:
        """
        Clean up stale cached values based on age.
        
        Args:
            max_age_seconds: Maximum age for cached values in seconds
        """
        current_time = datetime.now()
        if (current_time - self._last_check_time).seconds > max_age_seconds:
            # Clear cache periodically to prevent memory buildup
            self.clear_cache()
            self._last_check_time = current_time
    
    def has_key(self, key: str) -> bool:
        """
        Check if a key exists in session state.
        
        Args:
            key: Session state key to check
            
        Returns:
            True if key exists, False otherwise
        """
        return key in st.session_state
    
    def has_changed(self, key: str, new_value: Any) -> bool:
        """
        Check if a value has changed from its current session state value.
        
        Args:
            key: Session state key
            new_value: Value to compare against
            
        Returns:
            True if value has changed, False otherwise
        """
        current_value = self.get_value(key)
        return current_value != new_value

    def validate_and_cleanup_session_state(self, schema: Dict[str, type]) -> None:
        """
        Validate session state against a schema and remove invalid keys.

        Args:
            schema: A dictionary where keys are session state keys and
                    values are the expected types.
        """
        keys_to_remove = []
        for key in st.session_state:
            if key not in schema:
                keys_to_remove.append(key)
                logger.warning(f"Removing unexpected key '{key}' from session state.")
            elif not isinstance(st.session_state[key], schema[key]):
                keys_to_remove.append(key)
                logger.warning(
                    f"Removing key '{key}' from session state due to type mismatch. "
                    f"Expected {schema[key].__name__}, found {type(st.session_state[key]).__name__}."
                )

        for key in keys_to_remove:
            del st.session_state[key]
            self._cached_values.pop(key, None)
            self._initialized_keys.discard(key)

    def set(self, key: str, value: Any) -> bool:
        """
        Simplified set method for backward compatibility.
        
        Args:
            key: Session state key
            value: Value to set
            
        Returns:
            True if value changed, False otherwise
        """
        return self.set_value(key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Simplified get method for backward compatibility.
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
            
        Returns:
            Value from session state or default
        """
        return self.get_value(key, default)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current session state management.
        
        Returns:
            Dictionary with state management statistics
        """
        return {
            'initialized_keys_count': len(self._initialized_keys),
            'cached_values_count': len(self._cached_values),
            'registered_callbacks_count': len(self._change_callbacks),
            'initialized_keys': list(self._initialized_keys),
            'cached_keys': list(self._cached_values.keys()),
            'callback_keys': list(self._change_callbacks.keys())
        }


class ScenarioStateManager(SessionStateManager):
    """
    Specialized session state manager for scenario-related state management.
    """
    
    def __init__(self):
        """Initialize the scenario state manager."""
        super().__init__()
        self._scenario_cache: Dict[str, Dict[str, Any]] = {}
        self._current_scenario: Optional[str] = None
        
    def initialize_scenario_state(self) -> None:
        """Initialize scenario-specific session state keys."""
        scenario_defaults = {
            'current_scenario': 'Normal Operations',
            'scenario_changed': False,
            'scenario_change_timestamp': datetime.now(),
            'scenario_cached_values': {},
            'consolidated_sections_state': {},
            'active_section': 'overview',
            'section_anchors': {},
            'section_data_cache': {}
        }
        
        self.batch_initialize(scenario_defaults)
        self._current_scenario = self.get_value('current_scenario')
    
    def detect_scenario_change(self, new_scenario: str) -> bool:
        """
        Efficiently detect scenario changes with minimal session state access.
        
        Args:
            new_scenario: New scenario name
            
        Returns:
            True if scenario changed, False otherwise
        """
        current_scenario = self._current_scenario or self.get_value('current_scenario')
        
        if current_scenario != new_scenario:
            # Scenario changed - update state
            self.set_value('current_scenario', new_scenario)
            self.set_value('scenario_changed', True)
            self.set_value('scenario_change_timestamp', datetime.now())
            
            # Clear scenario-specific cache
            self.clear_scenario_cache()
            self._current_scenario = new_scenario
            
            return True
        
        # No change detected
        if self.get_value('scenario_changed'):
            self.set_value('scenario_changed', False)
            
        return False
    
    def cache_scenario_value(self, key: str, value: Any, scenario: Optional[str] = None) -> None:
        """
        Cache a value for a specific scenario.
        
        Args:
            key: Cache key
            value: Value to cache
            scenario: Scenario name (uses current if None)
        """
        scenario = scenario or self._current_scenario or self.get_value('current_scenario')
        
        if scenario not in self._scenario_cache:
            self._scenario_cache[scenario] = {}
            
        self._scenario_cache[scenario][key] = value
    
    def get_scenario_value(self, key: str, default: Any = None, scenario: Optional[str] = None) -> Any:
        """
        Get a cached value for a specific scenario.
        
        Args:
            key: Cache key
            default: Default value if not found
            scenario: Scenario name (uses current if None)
            
        Returns:
            Cached value or default
        """
        scenario = scenario or self._current_scenario or self.get_value('current_scenario')
        
        if scenario in self._scenario_cache and key in self._scenario_cache[scenario]:
            return self._scenario_cache[scenario][key]
            
        return default
    
    def clear_scenario_cache(self, scenario: Optional[str] = None) -> None:
        """
        Clear cached values for a specific scenario or all scenarios.
        
        Args:
            scenario: Scenario name (clears all if None)
        """
        if scenario is None:
            self._scenario_cache.clear()
            # Also clear session state scenario cache
            self.set_value('scenario_cached_values', {})
        else:
            self._scenario_cache.pop(scenario, None)
    
    def get_section_state(self, section_key: str, default: bool = False) -> bool:
        """
        Get section expansion state efficiently.
        
        Args:
            section_key: Section identifier
            default: Default state if not found
            
        Returns:
            Section expansion state
        """
        sections_state = self.get_value('consolidated_sections_state', {})
        return sections_state.get(section_key, default)
    
    def set_section_state(self, section_key: str, expanded: bool) -> bool:
        """
        Set section expansion state efficiently.
        
        Args:
            section_key: Section identifier
            expanded: Whether section is expanded
            
        Returns:
            True if state changed, False otherwise
        """
        sections_state = self.get_value('consolidated_sections_state', {})
        old_state = sections_state.get(section_key, False)
        
        if old_state != expanded:
            sections_state[section_key] = expanded
            self.set_value('consolidated_sections_state', sections_state)
            return True
            
        return False
    
    def batch_set_section_states(self, states: Dict[str, bool]) -> bool:
        """
        Set multiple section states in a batch operation.
        
        Args:
            states: Dictionary of section_key -> expanded state
            
        Returns:
            True if any state changed, False otherwise
        """
        sections_state = self.get_value('consolidated_sections_state', {})
        changed = False
        
        for section_key, expanded in states.items():
            if sections_state.get(section_key, False) != expanded:
                sections_state[section_key] = expanded
                changed = True
        
        if changed:
            self.set_value('consolidated_sections_state', sections_state)
            
        return any_changed
    
    def initialize_scenario_tracking(self) -> None:
        """Initialize scenario tracking state variables."""
        self.initialize_scenario_state()
    
    def expand_all_sections(self, section_keys: list) -> None:
        """
        Expand all sections efficiently.
        
        Args:
            section_keys: List of section keys to expand
        """
        states = {key: True for key in section_keys}
        self.batch_set_section_states(states)
    
    def collapse_all_sections(self, section_keys: list) -> None:
        """
        Collapse all sections efficiently.
        
        Args:
            section_keys: List of section keys to collapse
        """
        states = {key: False for key in section_keys}
        self.batch_set_section_states(states)


# Global instance for easy access
_session_manager = SessionStateManager()
_scenario_manager = ScenarioStateManager()


def get_session_manager() -> SessionStateManager:
    """Get the global session state manager instance."""
    return _session_manager


def get_scenario_manager() -> ScenarioStateManager:
    """Get the global scenario state manager instance."""
    return _scenario_manager