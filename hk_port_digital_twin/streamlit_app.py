import streamlit as st
from src.dashboard.main_app import PortDashboardApp

def main():
    """Main function to run the Streamlit app."""
    app = PortDashboardApp()
    app.configure_page()
    app.run()

if __name__ == "__main__":
    main()