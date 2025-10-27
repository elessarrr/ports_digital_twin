import streamlit as st

def show_tour(kpi_summary_placeholder, key_metrics_placeholder, roi_calculator_placeholder):
    """
    Displays the guided tour, highlighting different sections of the dashboard.
    """
    tour_step = st.session_state.get('tour_step', 0)

    if tour_step == 0:
        welcome_step()
    elif tour_step == 1:
        with kpi_summary_placeholder.container():
            kpi_summary_step()
    elif tour_step == 2:
        with key_metrics_placeholder.container():
            key_metrics_step()
    elif tour_step == 3:
        with roi_calculator_placeholder.container():
            roi_calculator_step()
    elif tour_step == 4:
        end_tour_step()

def welcome_step():
    """
    The first step of the guided tour, welcoming the user.
    """
    st.balloons()
    st.info("""
    ### Welcome to the Port Digital Twin Demo! 🚢

    This guided tour will walk you through the key features of the **Overview** tab.
    """)
    if st.button("Start Tour", key="start_tour"):
        st.session_state.tour_step = 1
        st.rerun()

def kpi_summary_step():
    """
    Explains the KPI Summary section.
    """
    st.info("""
    ### 📈 KPI Summary

    This section provides a high-level overview of the port's performance. 
    The chart visualizes historical trends and future forecasts for critical metrics.
    """)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Next: Key Metrics", key="next_kpi"):
            st.session_state.tour_step = 2
            st.rerun()
    with col2:
        if st.button("End Tour", key="end_tour_kpi"):
            st.session_state.show_tour = False
            st.rerun()

def key_metrics_step():
    """
    Explains the Key Metrics section.
    """
    st.info("""
    ### 📊 Key Metrics

    Here you can see a real-time snapshot of vessel activity and port status, including arrivals, departures, and berth availability.
    """)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Next: ROI Calculator", key="next_metrics"):
            st.session_state.tour_step = 3
            st.rerun()
    with col2:
        if st.button("End Tour", key="end_tour_metrics"):
            st.session_state.show_tour = False
            st.rerun()

def roi_calculator_step():
    """
    Explains the ROI Calculator section.
    """
    st.info("""
    ### 💰 ROI Calculator

    This tool helps you quantify the financial benefits of operational improvements. 
    Input cost factors and simulate different scenarios to estimate potential savings.
    """)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Finish Tour", key="next_roi"):
            st.session_state.tour_step = 4
            st.rerun()
    with col2:
        if st.button("End Tour", key="end_tour_roi"):
            st.session_state.show_tour = False
            st.rerun()

def end_tour_step():
    """
    The final step of the guided tour.
    """
    st.info("""
    ### You have completed the tour!

    Feel free to explore the dashboard. You can restart the tour at any time from the **Settings** tab.
    """)
    if st.button("Close", key="close_tour"):
        st.session_state.show_tour = False
        st.rerun()