import streamlit as st

def get_state(key, default_value=None):
    """Gets a value from the session state."""
    return st.session_state.get(key, default_value)

def set_state(key, value):
    """Sets a value in the session state."""
    st.session_state[key] = value

def delete_state(key):
    """Deletes a value from the session state."""
    if key in st.session_state:
        del st.session_state[key]