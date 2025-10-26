import streamlit as st

class CacheManager:
    def __init__(self):
        if 'cache_keys' not in st.session_state:
            st.session_state['cache_keys'] = {}

    def add_key(self, key, dependent_keys=None):
        st.session_state['cache_keys'][key] = dependent_keys or []

    def clear_cache(self, key_to_clear):
        if key_to_clear in st.session_state['cache_keys']:
            st.cache_data.clear()
            # More granular clearing is preferred if possible
            # For now, this is a simple implementation