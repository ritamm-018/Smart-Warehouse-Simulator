import streamlit as st
import numpy as np
import time
import random
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.sim_engine import run_simulation
from utils.data_persistence import persistence
import threading

try:
    from warehouse_state import warehouse_state
except ImportError:
    warehouse_state = {}

def format_time(seconds):
    """Convert seconds to minutes and seconds format"""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    if minutes > 0:
        return f"{minutes} min {remaining_seconds} seconds"
    else:
        return f"{remaining_seconds} seconds"

def calculate_efficiency_score(actual_pick_time, actual_distance, orders_completed, total_orders):
    """Calculate efficiency score based on the given formula"""
    ideal_pick_time = 10  # seconds
    ideal_distance = 1000  # meters
    
    # Calculate efficiency components
    pick_time_efficiency = ideal_pick_time / actual_pick_time if actual_pick_time > 0 else 0
    distance_efficiency = ideal_distance / actual_distance if actual_distance > 0 else 0
    completion_efficiency = orders_completed / total_orders if total_orders > 0 else 0
    
    # Calculate overall efficiency score
    efficiency_score = pick_time_efficiency * distance_efficiency * completion_efficiency * 100
    
    # Cap at 100%
    return min(efficiency_score, 100.0)

def metrics_section():
    # Check if we have order simulation results from the layout
    order_simulation_results = st.session_state.get('order_simulation_results', None)
    
    # Initialize metrics if not present - only on first load
    if 'realtime_metrics' not in st.session_state:
        st.session_state.realtime_metrics = {
            'average_pick_time': 60.0,
            'total_pickup_time': 0.0,
            'orders_completed': 0,
            'total_distance': 0.0
        }
        st.session_state.metrics_start_time = time.time()
        st.session_state.simulation_completed = False
        st.session_state.metrics_update_time = time.time()
        st.session_state.metrics_initialized = True
    elif 'metrics_initialized' not in st.session_state:
        # If metrics exist but not initialized flag, preserve existing values
        st.session_state.metrics_initialized = True
    
    # Update metrics with simulation results if available
    if order_simulation_results:
        st.session_state.realtime_metrics = {
            'average_pick_time': order_simulation_results.get('average_time', 60.0),
            'total_pickup_time': order_simulation_results.get('total_time', 0.0),
            'orders_completed': order_simulation_results.get('completed_orders', 0),
            'total_distance': order_simulation_results.get('total_distance', 0.0)
        }
        # Mark simulation as completed since we have results
        st.session_state.simulation_completed = True
    
    # Ensure metrics_update_time exists
    if 'metrics_update_time' not in st.session_state:
        st.session_state.metrics_update_time = time.time()
    
    # Add a flag to prevent resetting metrics on page refresh
    if 'metrics_initialized' not in st.session_state:
        st.session_state.metrics_initialized = True
    
    # Update metrics every 1 second for real-time updates
    current_time = time.time()
    last_update_time = st.session_state.get('metrics_update_time', current_time)
    
    if current_time - last_update_time >= 1.0:
        st.session_state.metrics_update_time = current_time
        
        # Check for updated simulation results
        order_simulation_results = st.session_state.get('order_simulation_results', None)
        if order_simulation_results:
            # Update metrics with latest simulation results
            st.session_state.realtime_metrics = {
                'average_pick_time': order_simulation_results.get('average_time', 60.0),
                'total_pickup_time': order_simulation_results.get('total_time', 0.0),
                'orders_completed': order_simulation_results.get('completed_orders', 0),
                'total_distance': order_simulation_results.get('total_distance', 0.0)
            }
            
            # Check if simulation is completed
            progress_info = order_simulation_results.get('simulation_progress', {})
            total_orders = progress_info.get('total_orders', 50)
            completed_orders = order_simulation_results.get('completed_orders', 0)
            
            if completed_orders >= total_orders:
                    st.session_state.simulation_completed = True
            else:
                st.session_state.simulation_completed = False

    metrics = st.session_state.realtime_metrics
    elapsed = int(time.time() - st.session_state.get('metrics_start_time', time.time()))

    # Check if simulation is completed
    total_orders = st.session_state.get('num_orders', 50)

    # Show data source and update time
    simulation_running = st.session_state.get('simulation_running', False)
    
    # Simulation status messages removed from left side
    pass
    
    # Simulation completion status and restart button removed from left side
    pass

# Remove warehouse_metrics function to prevent duplicate metric boxes
# def warehouse_metrics():
#     st.header('Warehouse Simulation Metrics')
#     sim_results = warehouse_state.get('simulation_results')
#     if not sim_results:
#         st.info('Run a simulation to view metrics.')
#         return
#     # Throughput
#     throughput = sim_results.get('orders_completed')
#     avg_pick_time = sim_results.get('average_pick_time') or sim_results.get('average_pick_time') or sim_results.get('average_pick_time', sim_results.get('average_pick_time', 0))
#     if avg_pick_time is None:
#         avg_pick_time = sim_results.get('average_pick_time', 0)
#     st.metric('Throughput (Orders Completed)', throughput)
#     st.metric('Average Pick Time (s)', f"{avg_pick_time:.2f}")
#     # Bottleneck locations (if available)
#     activity_map = sim_results.get('activity_map')
#     if activity_map is not None:
#         arr = np.array(activity_map)
#         max_val = arr.max()
#         if max_val > 0:
#             bottlenecks = np.argwhere(arr == max_val)
#             st.write(f"Bottleneck location(s) (most congested): {bottlenecks.tolist()} (activity={max_val})")
#         else:
#             st.write('No bottlenecks detected.')
#     else:
#         st.write('Bottleneck data not available.')
