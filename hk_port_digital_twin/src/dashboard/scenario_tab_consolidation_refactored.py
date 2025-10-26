"""
Refactored version of the consolidated scenarios tab.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, List
import asyncio

from hk_port_digital_twin.src.dashboard.utils.performance_monitor import timing_decorator
from hk_port_digital_twin.src.dashboard.utils.ux_metrics import track_time_on_page, get_user_feedback

# Fallback for missing modules
try:
    from src.core.scenario_simulation import ScenarioAwareCalculator
    SCENARIO_AWARE_CALCULATOR_AVAILABLE = True
except ImportError:
    SCENARIO_AWARE_CALCULATOR_AVAILABLE = False

class ScenarioData:
    """
    Handles data generation and caching for the scenarios tab.
    """

    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        self.params = self._get_scenario_performance_params(scenario_name)

    @st.cache_data
    def get_all_scenario_values(_self) -> Dict[str, Any]:
        """
        Retrieves all scenario values, using caching to avoid re-computation.
        """
        return _self._generate_all_scenario_values()

    @st.cache_data
    async def get_all_scenario_values_async(_self) -> Dict[str, Any]:
        """
        Retrieves all scenario values asynchronously.
        """
        return await _self._generate_all_scenario_values_async()

    def _generate_all_scenario_values(self) -> Dict[str, Any]:
        """
        Generates a dictionary of all scenario values based on the current scenario.
        """
        return self._generate_scenario_values(self.scenario_name, list(self.params.keys()))

    async def _generate_all_scenario_values_async(self) -> Dict[str, Any]:
        """
        Generates a dictionary of all scenario values asynchronously.
        """
        # Simulate an async operation
        await asyncio.sleep(0.1)
        return self._generate_scenario_values(self.scenario_name, list(self.params.keys()))

    def _get_scenario_performance_params(self, scenario_key: str) -> Dict[str, Any]:
        """Returns a dictionary of performance parameters for a given scenario."""
        all_params = {
            "Peak Season": {
                "throughput": (1.2, 1.5),
                "utilization": (0.8, 0.95),
                "revenue": (1.5, 2.0),
                "handling_time": (0.8, 1.0),
                "queue_length": (1.2, 1.6),
                "waiting_time": (20, 40),
            },
            "Low Season": {
                "throughput": (0.8, 1.0),
                "utilization": (0.6, 0.7),
                "revenue": (0.7, 0.9),
                "handling_time": (1.1, 1.3),
                "queue_length": (0.7, 0.9),
                "waiting_time": (5, 15),
            },
            "Normal Operations": {
                "throughput": (1.0, 1.2),
                "utilization": (0.7, 0.8),
                "revenue": (1.0, 1.2),
                "handling_time": (1.0, 1.1),
                "queue_length": (0.9, 1.1),
                "waiting_time": (10, 25),
            }
        }
        return all_params.get(scenario_key, all_params["Normal Operations"])

    def _generate_scenario_values(
        self, 
        scenario: str, 
        value_types: List[str], 
        count: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generates a dictionary of scenario values for the given value types.
        """
        values = {}
        for value_type in value_types:
            if value_type in self.params:
                min_val, max_val = self.params[value_type]
                if count == 1:
                    values[value_type] = np.random.uniform(min_val, max_val)
                else:
                    values[value_type] = np.random.uniform(min_val, max_val, count)
        return values


class ScenarioRenderer:
    """
    Handles the rendering of UI components for the scenarios tab.
    """

    def __init__(self, scenario_data: ScenarioData):
        self.scenario_data = scenario_data

    async def render(self) -> None:
        """
        Renders the entire consolidated scenarios tab.
        """
        scenario_values = await self.scenario_data.get_all_scenario_values_async()

        with st.expander("Key Metrics", expanded=True):
            self._render_key_metrics(scenario_values)
        with st.expander("Throughput Analysis"):
            self._render_throughput_analysis(scenario_values)
        with st.expander("Waiting Time Analysis"):
            self._render_waiting_time_analysis(scenario_values)
        with st.expander("Performance Metrics"):
            self._render_performance_metrics(scenario_values)

    @timing_decorator
    def _render_key_metrics(self, scenario_values: Dict[str, Any]) -> None:
        """
        Renders the key metrics section.
        """
        st.markdown("#### Key Metrics")

        col1, col2 = st.columns(2)
        col1.metric("Throughput", f"{scenario_values.get('throughput', 0):.2f}")
        col2.metric("Utilization", f"{scenario_values.get('utilization', 0):.2f}")

    @timing_decorator
    def _render_throughput_analysis(self, scenario_values: Dict[str, Any]) -> None:
        """
        Renders the throughput analysis section.
        """
        st.markdown("#### Throughput Analysis")
        throughput_data = scenario_values.get("throughput", np.random.rand(30) * 1.2)

        df = pd.DataFrame({"Day": range(30), "Throughput": throughput_data})

        fig = px.line(df, x="Day", y="Throughput", title="Throughput Over Time")
        st.plotly_chart(fig, use_container_width=True)

    @timing_decorator
    def _render_waiting_time_analysis(self, scenario_values: Dict[str, Any]) -> None:
        """
        Renders the waiting time analysis section.
        """
        st.markdown("#### Waiting Time Analysis")
        waiting_time_data = scenario_values.get("waiting_time", np.random.rand(100) * 30)

        fig = px.histogram(waiting_time_data, nbins=20, title="Waiting Time Distribution")
        st.plotly_chart(fig, use_container_width=True)

    @timing_decorator
    def _render_performance_metrics(self, scenario_values: Dict[str, Any]):
        """Renders a radar chart for consolidated performance indicators."""
        st.subheader("Consolidated Performance Indicators")

        fig = self._create_performance_radar_chart(scenario_values)
        st.plotly_chart(fig, use_container_width=True)

    @st.cache_data
    def _create_performance_radar_chart(_self, scenario_values: Dict[str, Any]) -> go.Figure:
        """Creates a radar chart for consolidated performance indicators."""
        # Define the categories for the radar chart
        categories = [
            'throughput', 'utilization', 'revenue', 'handling_time', 'queue_length'
        ]

        # Extract the values for the categories
        values = [scenario_values.get(cat, 0) for cat in categories]

        # Create the radar chart
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Performance'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]  # Adjust range for better visualization
                )
            ),
            showlegend=False
        )

        return fig


class ConsolidatedScenariosTab:
    """
    A refactored version of the tab that consolidates all scenario-related analytics.
    """

    def __init__(self):
        pass

    async def render(self, scenario_data: Optional[Dict[str, Any]] = None) -> None:
        st.markdown("### 📊 Consolidated Scenarios Dashboard")
        scenario_name = st.selectbox("Select Scenario", ["Normal Operations", "Peak Season", "Low Season"])

        if scenario_name:
            data_provider = ScenarioData(scenario_name)
            renderer = ScenarioRenderer(data_provider)
            await renderer.render()

        track_time_on_page()
        get_user_feedback()

def render_consolidated_scenarios_tab(scenario_data: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to render the consolidated scenarios tab."""
    tab = ConsolidatedScenariosTab()
    asyncio.run(tab.render(scenario_data))