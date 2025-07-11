import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

try:
    from warehouse_state import warehouse_state
except ImportError:
    warehouse_state = {}

def run_custom_analytics():
    layout = warehouse_state.get('layout')
    results = warehouse_state.get('simulation_results')
    if not layout or not results:
        return
    analytics = {}
    # Example: Idle picker % (if available)
    # (This is a placeholder; actual idle picker logic depends on simulation details)
    # Example: Congestion zones (most visited cells)
    activity_map = results.get('activity_map')
    if activity_map is not None:
        arr = np.array(activity_map)
        max_val = arr.max()
        if max_val > 0:
            congestion_zones = np.argwhere(arr == max_val)
            analytics['congestion_zones'] = congestion_zones.tolist()
            analytics['max_congestion'] = int(max_val)
        else:
            analytics['congestion_zones'] = []
            analytics['max_congestion'] = 0
    # Store analytics in warehouse_state
    warehouse_state['analytics'] = analytics

def analytics_tabs():
    # Check if simulation is completed - only refresh if not completed
    simulation_completed = st.session_state.get('simulation_completed', False)
    
    # Get current timestamp to force updates
    current_timestamp = time.time()
    
    st.markdown('<div class="section-title">Performance Analytics Dashboard</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        # Get real-time metrics from session state
        realtime_metrics = st.session_state.get('realtime_metrics', {
            'average_pick_time': 60.0,
            'orders_completed': 0,
            'total_distance': 0.0
        })
        
        # Create time series data based on real-time metrics
        if 'analytics_history' not in st.session_state:
            st.session_state.analytics_history = {
                'distance': [],
                'pick_time': []
            }
        
        # Only add current values to history if simulation is not completed
        if not simulation_completed:
            st.session_state.analytics_history['distance'].append(realtime_metrics['total_distance'])
            st.session_state.analytics_history['pick_time'].append(realtime_metrics['average_pick_time'])
            
            # Keep only last 20 data points for better visualization
            if len(st.session_state.analytics_history['distance']) > 20:
                st.session_state.analytics_history['distance'] = st.session_state.analytics_history['distance'][-20:]
                st.session_state.analytics_history['pick_time'] = st.session_state.analytics_history['pick_time'][-20:]
        
        # Create DataFrame for plotting
        time_data = pd.DataFrame({
            'Distance': st.session_state.analytics_history['distance'],
            'Pick_Time': st.session_state.analytics_history['pick_time']
        })
        
        # Create single line graph with distance vs pick time
        fig_performance = px.line(
            time_data,
            x='Distance',
            y='Pick_Time',
            title=f"Pick Time vs Distance (Live) - Updated: {current_timestamp:.0f}",
            labels={'Distance': 'Distance (m)', 'Pick_Time': 'Pick Time (s)'}
        )
        
        # Set maximum y-axis value to 100
        fig_performance.update_layout(
            yaxis=dict(range=[0, 100]),
            xaxis=dict(title="Distance (m)"),
            yaxis_title="Pick Time (s)"
        )
        
        st.plotly_chart(fig_performance, use_container_width=True)
        
        # Show current values for debugging
        if st.checkbox("Show Debug Info"):
            st.write(f"Current Pick Time: {realtime_metrics['average_pick_time']:.1f}")
            st.write(f"Current Distance: {realtime_metrics['total_distance']:.0f}")
            st.write(f"History Length: {len(st.session_state.analytics_history['distance'])}")
            st.write(f"Simulation Completed: {simulation_completed}")
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
