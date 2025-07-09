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
        heatmap_data = np.random.rand(grid_height, grid_width)
        fig_heatmap = px.imshow(
            heatmap_data,
            title="Warehouse Activity Heatmap",
            labels=dict(x="X Position", y="Y Position", color="Activity Level"),
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
