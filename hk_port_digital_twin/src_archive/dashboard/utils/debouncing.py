import streamlit as st
import time
from functools import wraps

class DebounceManager:
    def __init__(self, delay):
        self.delay = delay
        if "last_call" not in st.session_state:
            st.session_state.last_call = 0

    def debounced_callback(self, callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - st.session_state.last_call > self.delay:
                st.session_state.last_call = current_time
                return callback(*args, **kwargs)
        return wrapper