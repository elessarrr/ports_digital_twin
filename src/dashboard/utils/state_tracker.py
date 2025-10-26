import streamlit as st

class StateChangeTracker:
    def __init__(self, state_key, initial_value=None):
        self.state_key = state_key
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = initial_value

    def set(self, value):
        if st.session_state[self.state_key] != value:
            st.session_state[self.state_key] = value
            return True
        return False

    def get(self):
        return st.session_state[self.state_key]