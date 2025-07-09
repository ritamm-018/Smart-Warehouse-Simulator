import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def analytics_tabs():
    st.subheader("Performance Analytics Dashboard")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        time_data = pd.DataFrame({
            'Time': range(1, 21),
            'Pick_Time': np.random.uniform(40, 80, 20),
            'Distance': np.random.uniform(50, 150, 20)
        })
        fig_performance = px.line(
            time_data,
            x='Time',
            y=['Pick_Time', 'Distance'],
            title="Performance Over Time",
            labels={'value': 'Value', 'variable': 'Metric'}
        )
        st.plotly_chart(fig_performance, use_container_width=True)
    with col_p2:
        grid_height = st.session_state['grid_height']
        grid_width = st.session_state['grid_width']
        activity_map = None
        if (
            'simulation_results' in st.session_state and
            st.session_state['simulation_results'] and
            'activity_map' in st.session_state['simulation_results'] and
            st.session_state['simulation_results']['activity_map']
        ):
            activity_map = np.array(st.session_state['simulation_results']['activity_map'])
        if activity_map is not None and activity_map.size > 0:
            fig_heatmap = px.imshow(
                activity_map,
                color_continuous_scale="Viridis",
                title="Warehouse Traffic Heatmap",
                labels={"x": "X Position", "y": "Y Position", "color": "Visit Frequency"}
            )
            fig_heatmap.update_xaxes(title_text="X Position")
            fig_heatmap.update_yaxes(title_text="Y Position")
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("No activity map data available. Run a simulation to see warehouse traffic heatmap.")
            blank_map = np.zeros((grid_height, grid_width))
            fig_blank = px.imshow(
                blank_map,
                color_continuous_scale="Viridis",
                title="Warehouse Traffic Heatmap",
                labels={"x": "X Position", "y": "Y Position", "color": "Visit Frequency"}
            )
            st.plotly_chart(fig_blank, use_container_width=True)
