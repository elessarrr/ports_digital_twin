"""
State Change Tracking Utility

This module provides comprehensive state change tracking and optimization
for the dashboard, helping identify performance bottlenecks and optimize
state management patterns.
"""

import streamlit as st
from typing import Any, Dict, List, Optional, Set, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class StateChange:
    """Represents a single state change event."""
    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    component: Optional[str] = None
    user_action: Optional[str] = None
    change_type: str = "update"  # update, create, delete
    
    def __post_init__(self):
        """Calculate change hash for deduplication."""
        self.change_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate a hash for this change."""
        content = f"{self.key}:{self.old_value}:{self.new_value}:{self.change_type}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


@dataclass
class StateMetrics:
    """Metrics for state change analysis."""
    total_changes: int = 0
    unique_keys: Set[str] = field(default_factory=set)
    change_frequency: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    component_changes: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    recent_changes: int = 0
    redundant_changes: int = 0
    performance_impact: float = 0.0


class StateChangeTracker:
    """
    Advanced state change tracker for performance optimization.
    
    This class tracks all state changes, identifies patterns, and provides
    optimization recommendations to improve dashboard performance.
    """
    
    def __init__(self, max_history: int = 1000, analysis_window_minutes: int = 5):
        """
        Initialize the state change tracker.
        
        Args:
            max_history: Maximum number of changes to keep in history
            analysis_window_minutes: Time window for recent change analysis
        """
        self.max_history = max_history
        self.analysis_window = timedelta(minutes=analysis_window_minutes)
        
        # Change tracking
        self.change_history: deque = deque(maxlen=max_history)
        self.key_frequencies: Dict[str, int] = defaultdict(int)
        self.component_frequencies: Dict[str, int] = defaultdict(int)
        
        # Performance tracking
        self.redundant_changes: List[StateChange] = []
        self.high_frequency_keys: Set[str] = set()
        self.optimization_suggestions: List[str] = []
        
        # Callbacks for optimization
        self.change_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.threshold_callbacks: Dict[str, Callable] = {}
        
        # State snapshots for comparison
        self.state_snapshots: Dict[str, Any] = {}
        self.last_snapshot_time = datetime.now()
        
    def track_change(self, 
                    key: str, 
                    old_value: Any, 
                    new_value: Any,
                    component: Optional[str] = None,
                    user_action: Optional[str] = None) -> StateChange:
        """
        Track a state change and analyze its impact.
        
        Args:
            key: State key that changed
            old_value: Previous value
            new_value: New value
            component: Component that triggered the change
            user_action: User action that caused the change
            
        Returns:
            StateChange object representing this change
        """
        change = StateChange(
            key=key,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.now(),
            component=component,
            user_action=user_action
        )
        
        # Add to history
        self.change_history.append(change)
        
        # Update frequencies
        self.key_frequencies[key] += 1
        if component:
            self.component_frequencies[component] += 1
        
        # Check for redundant changes
        if self._is_redundant_change(change):
            self.redundant_changes.append(change)
            logger.warning(f"Redundant state change detected for key: {key}")
        
        # Check for high-frequency keys
        if self.key_frequencies[key] > 10:  # Configurable threshold
            self.high_frequency_keys.add(key)
            
        # Trigger callbacks
        self._trigger_callbacks(change)
        
        # Generate optimization suggestions
        self._update_optimization_suggestions()
        
        return change
    
    def _is_redundant_change(self, change: StateChange) -> bool:
        """Check if a change is redundant (same value set multiple times)."""
        recent_changes = [c for c in self.change_history 
                         if c.key == change.key and 
                         c.timestamp > datetime.now() - timedelta(seconds=1)]
        
        if len(recent_changes) > 1:
            # Check if we're setting the same value repeatedly
            last_change = recent_changes[-1]
            return (last_change.new_value == change.new_value and 
                   last_change.old_value == change.old_value)
        
        return False
    
    def _trigger_callbacks(self, change: StateChange) -> None:
        """Trigger registered callbacks for this change."""
        # Key-specific callbacks
        for callback in self.change_callbacks.get(change.key, []):
            try:
                callback(change)
            except Exception as e:
                logger.error(f"Error in change callback for {change.key}: {e}")
        
        # Threshold callbacks
        frequency = self.key_frequencies[change.key]
        threshold_key = f"{change.key}_threshold"
        if threshold_key in self.threshold_callbacks:
            try:
                self.threshold_callbacks[threshold_key](change, frequency)
            except Exception as e:
                logger.error(f"Error in threshold callback for {change.key}: {e}")
    
    def _update_optimization_suggestions(self) -> None:
        """Update optimization suggestions based on current patterns."""
        suggestions = []
        
        # High-frequency key suggestions
        if self.high_frequency_keys:
            suggestions.append(
                f"Consider debouncing or batching updates for keys: {', '.join(self.high_frequency_keys)}"
            )
        
        # Redundant change suggestions
        if len(self.redundant_changes) > 5:
            suggestions.append(
                "Multiple redundant state changes detected. Consider adding change detection."
            )
        
        # Component-specific suggestions
        high_freq_components = [comp for comp, freq in self.component_frequencies.items() 
                               if freq > 20]
        if high_freq_components:
            suggestions.append(
                f"Components with high state change frequency: {', '.join(high_freq_components)}. "
                "Consider state optimization."
            )
        
        self.optimization_suggestions = suggestions
    
    def get_metrics(self) -> StateMetrics:
        """Get comprehensive metrics about state changes."""
        now = datetime.now()
        recent_cutoff = now - self.analysis_window
        
        recent_changes = [c for c in self.change_history if c.timestamp > recent_cutoff]
        
        return StateMetrics(
            total_changes=len(self.change_history),
            unique_keys=set(c.key for c in self.change_history),
            change_frequency=dict(self.key_frequencies),
            component_changes=dict(self.component_frequencies),
            recent_changes=len(recent_changes),
            redundant_changes=len(self.redundant_changes),
            performance_impact=self._calculate_performance_impact()
        )
    
    def _calculate_performance_impact(self) -> float:
        """Calculate estimated performance impact score (0-100)."""
        base_score = 0.0
        
        # Factor in redundant changes
        base_score += len(self.redundant_changes) * 2
        
        # Factor in high-frequency keys
        base_score += len(self.high_frequency_keys) * 5
        
        # Factor in recent change rate
        recent_changes = len([c for c in self.change_history 
                            if c.timestamp > datetime.now() - self.analysis_window])
        if recent_changes > 50:
            base_score += (recent_changes - 50) * 0.5
        
        return min(base_score, 100.0)
    
    def register_change_callback(self, key: str, callback: Callable[[StateChange], None]) -> None:
        """Register a callback for changes to a specific key."""
        self.change_callbacks[key].append(callback)
    
    def register_threshold_callback(self, key: str, callback: Callable[[StateChange, int], None]) -> None:
        """Register a callback for when a key exceeds change frequency threshold."""
        self.threshold_callbacks[f"{key}_threshold"] = callback
    
    def create_state_snapshot(self, name: str) -> None:
        """Create a snapshot of current session state."""
        snapshot = {}
        for key in st.session_state:
            try:
                # Only snapshot serializable values
                json.dumps(st.session_state[key])
                snapshot[key] = st.session_state[key]
            except (TypeError, ValueError):
                # Skip non-serializable values
                snapshot[key] = f"<non-serializable: {type(st.session_state[key]).__name__}>"
        
        self.state_snapshots[name] = {
            'snapshot': snapshot,
            'timestamp': datetime.now(),
            'total_keys': len(snapshot)
        }
        
        self.last_snapshot_time = datetime.now()
    
    def compare_snapshots(self, snapshot1: str, snapshot2: str) -> Dict[str, Any]:
        """Compare two state snapshots to identify changes."""
        if snapshot1 not in self.state_snapshots or snapshot2 not in self.state_snapshots:
            return {'error': 'One or both snapshots not found'}
        
        snap1 = self.state_snapshots[snapshot1]['snapshot']
        snap2 = self.state_snapshots[snapshot2]['snapshot']
        
        added_keys = set(snap2.keys()) - set(snap1.keys())
        removed_keys = set(snap1.keys()) - set(snap2.keys())
        changed_keys = []
        
        for key in set(snap1.keys()) & set(snap2.keys()):
            if snap1[key] != snap2[key]:
                changed_keys.append({
                    'key': key,
                    'old_value': snap1[key],
                    'new_value': snap2[key]
                })
        
        return {
            'added_keys': list(added_keys),
            'removed_keys': list(removed_keys),
            'changed_keys': changed_keys,
            'total_changes': len(added_keys) + len(removed_keys) + len(changed_keys)
        }
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate a comprehensive optimization report."""
        metrics = self.get_metrics()
        
        return {
            'summary': {
                'total_changes': metrics.total_changes,
                'unique_keys': len(metrics.unique_keys),
                'recent_changes': metrics.recent_changes,
                'redundant_changes': metrics.redundant_changes,
                'performance_impact': metrics.performance_impact
            },
            'high_frequency_keys': list(self.high_frequency_keys),
            'top_components': sorted(metrics.component_changes.items(), 
                                   key=lambda x: x[1], reverse=True)[:5],
            'optimization_suggestions': self.optimization_suggestions,
            'recent_redundant_changes': [
                {
                    'key': c.key,
                    'timestamp': c.timestamp.isoformat(),
                    'component': c.component
                }
                for c in self.redundant_changes[-10:]
            ]
        }
    
    def clear_history(self) -> None:
        """Clear change history and reset metrics."""
        self.change_history.clear()
        self.key_frequencies.clear()
        self.component_frequencies.clear()
        self.redundant_changes.clear()
        self.high_frequency_keys.clear()
        self.optimization_suggestions.clear()
        
        logger.info("State change history cleared")


# Global tracker instance
_state_tracker = StateChangeTracker()


def get_state_tracker() -> StateChangeTracker:
    """Get the global state change tracker instance."""
    return _state_tracker


def track_state_change(key: str, 
                      old_value: Any, 
                      new_value: Any,
                      component: Optional[str] = None,
                      user_action: Optional[str] = None) -> StateChange:
    """
    Convenience function to track a state change.
    
    Args:
        key: State key that changed
        old_value: Previous value
        new_value: New value
        component: Component that triggered the change
        user_action: User action that caused the change
        
    Returns:
        StateChange object representing this change
    """
    return _state_tracker.track_change(key, old_value, new_value, component, user_action)


def create_performance_snapshot(name: str) -> None:
    """Create a performance snapshot for later comparison."""
    _state_tracker.create_state_snapshot(name)


def get_performance_metrics() -> StateMetrics:
    """Get current performance metrics."""
    return _state_tracker.get_metrics()


def get_optimization_suggestions() -> List[str]:
    """Get current optimization suggestions."""
    return _state_tracker.optimization_suggestions