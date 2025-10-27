import streamlit as st
import time

def run_quick_demo():
    """Runs a quick demo of the dashboard."""
    st.info("🚀 Starting Quick Demo! This will automatically navigate through the key features of the dashboard.")
    time.sleep(3)

    # 1. Overview Tab
    st.experimental_set_query_params(tab="Overview")
    st.success("📍 Now showing the **Overview** tab. Here you can see a high-level summary of the port's key performance indicators.")
    time.sleep(5)

    # 2. Berth Planning Tab
    st.experimental_set_query_params(tab="Berth Planning")
    st.success("📍 Next, the **Berth Planning** tab. This provides a real-time view of berth assignments and availability.")
    time.sleep(5)

    # 3. Vessel Analytics Tab
    st.experimental_set_query_params(tab="Vessel Analytics")
    st.success("📍 Now, the **Vessel Analytics** tab. This tab offers deep insights into vessel traffic patterns and performance.")
    time.sleep(5)

    # 4. Cargo Statistics Tab
    st.experimental_set_query_params(tab="Cargo Statistics")
    st.success("📍 Here is the **Cargo Statistics** tab. This tab provides a detailed breakdown of cargo volume and types.")
    time.sleep(5)

    # 5. Scenarios Tab
    st.experimental_set_query_params(tab="Scenarios")
    st.success("📍 Finally, the **Scenarios** tab. This powerful tool allows you to simulate different operational scenarios and compare their outcomes.")
    time.sleep(5)

    st.info("🎉 Quick Demo Complete! Feel free to explore the dashboard on your own.")