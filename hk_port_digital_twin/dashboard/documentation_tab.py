import streamlit as st

def render_documentation_tab():
    """Renders the documentation tab."""
    st.title("Documentation and User Guide")

    st.header("Welcome to the Hong Kong Port Digital Twin!")
    st.write("""
        This application provides a real-time simulation and analytics platform for the Hong Kong Port. 
        You can use this tool to monitor port operations, analyze performance, and explore the impact of different scenarios.
    """)

    st.header("Features")
    st.subheader("Overview Tab")
    st.write("The Overview tab provides a high-level summary of the port's key performance indicators (KPIs).")

    st.subheader("Berth Planning Tab")
    st.write("The Berth Planning tab allows you to visualize and manage berth assignments for vessels.")

    st.subheader("Vessel Analytics Tab")
    st.write("The Vessel Analytics tab provides detailed insights into vessel traffic, turnaround times, and other metrics.")

    st.subheader("Cargo Statistics Tab")
    st.write("The Cargo Statistics tab displays information about cargo throughput, types, and trends.")

    st.subheader("Scenarios Tab")
    st.write("""
        The Scenarios tab enables you to explore the impact of different operational scenarios on port performance. 
        You can select from a list of predefined scenarios or create your own custom scenario by adjusting the parameters in the sidebar.
    """)

    st.header("How to Use the Scenarios Tab")
    st.write("""
        1. **Select a Scenario:** Choose a scenario from the dropdown menu. You can select 'Normal Operations', 'Peak Season', 'Low Season', or 'Custom Scenario'.
        2. **Custom Scenario:** If you select 'Custom Scenario', you can adjust the 'Throughput Multiplier', 'Utilization Multiplier', and 'Revenue Multiplier' using the sliders in the sidebar.
        3. **Analyze the Results:** The application will display a side-by-side comparison of the selected scenario and the 'Normal Operations' baseline. You can analyze the key metrics, throughput analysis, waiting time analysis, and performance metrics for each scenario.
    """)