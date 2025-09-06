import streamlit as st

def render_simulation_controls():
    """
    Renders the simulation controls component, allowing users to start, stop,
    and configure the simulation.
    """
    with st.container():
        st.markdown("#### Simulation Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Start Simulation", type="primary"):
                st.toast("Simulation started!", icon="🎉")

        with col2:
            if st.button("⏹️ Stop Simulation"):
                st.toast("Simulation stopped.", icon="🛑")

        with col3:
            if st.button("🔄 Reset Simulation"):
                st.toast("Simulation reset.", icon="🔄")

        st.markdown("---")
        
        st.markdown("##### Simulation Parameters")
        
        sim_speed = st.select_slider(
            "Simulation Speed",
            options=["0.5x", "1x", "2x", "5x", "10x"],
            value="1x",
            help="Adjust the speed of the simulation."
        )
        
        time_granularity = st.selectbox(
            "Time Granularity",
            options=["Minute", "Hour", "Day"],
            index=1,
            help="Set the time step for the simulation."
        )