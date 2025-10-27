"""
This module provides a background data loader to prevent UI blocking.
"""
import threading
import time
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

class BackgroundLoader(threading.Thread):
    """A thread-based loader to run data loading tasks in the background."""
    def __init__(self, loader_func: Callable[[], Any]):
        super().__init__()
        self.loader_func = loader_func
        self.result = None
        self.error = None

    def run(self):
        """Executes the loader function and stores the result or error."""
        try:
            self.result = self.loader_func()
        except Exception as e:
            logger.error(f"Background loading failed: {e}")
            self.error = e