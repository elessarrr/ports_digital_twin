import streamlit as st
import pandas as pd
import plotly.express as px

def render_weather_impact_analysis():
    """
    Renders the weather impact analysis component.
    
    This component will display a chart showing the impact of weather on port operations.
    """
    st.subheader("Weather Impact Analysis")
    
    # Create a sample dataframe for weather impact
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
        'Vessel_Arrivals': [20, 15, 25, 22, 18],
        'Wind_Speed_kmh': [10, 35, 8, 12, 40],
        'Weather_Condition': ['Clear', 'Stormy', 'Clear', 'Cloudy', 'Stormy']
    }
    df = pd.DataFrame(data)
    
    # Create a scatter plot to show the impact of wind speed on vessel arrivals
    fig = px.scatter(df, x='Wind_Speed_kmh', y='Vessel_Arrivals', color='Weather_Condition',
                     title='Impact of Wind Speed on Vessel Arrivals',
                     labels={'Wind_Speed_kmh': 'Wind Speed (km/h)', 'Vessel_Arrivals': 'Number of Vessel Arrivals'},
                     hover_data=['Date'])
    
    st.plotly_chart(fig, use_container_width=True)