import streamlit as st
import numpy as np
import time
import random
import pandas as pd
from sim_engine import run_simulation
import threading

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
    # Initialize metrics if not present
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
    
    # Update metrics every 2 seconds without page refresh
    current_time = time.time()
    if current_time - st.session_state.get('metrics_update_time', 0) >= 2.0:
        st.session_state.metrics_update_time = current_time
        
        # Only update if simulation is not completed
        if not st.session_state.get('simulation_completed', False):
            metrics = st.session_state.realtime_metrics
            total_orders = st.session_state.get('num_orders', 50)
            
            # Simulate smooth metric changes
            prev_avg = metrics['average_pick_time']
            prev_total = metrics['total_pickup_time']
            prev_orders = metrics['orders_completed']
            prev_dist = metrics['total_distance']

            # Simulate new values
            new_avg = max(30, prev_avg + random.uniform(-2, 2))
            new_total = prev_total + random.uniform(5, 15)  # Add time for each order
            new_orders = min(total_orders, prev_orders + random.randint(0, 3))
            new_dist = prev_dist + random.uniform(10, 30)

            # Update metrics
            metrics['average_pick_time'] = new_avg
            metrics['total_pickup_time'] = new_total
            metrics['orders_completed'] = new_orders
            metrics['total_distance'] = new_dist
            
            # Check if simulation is completed
            if metrics['orders_completed'] >= total_orders:
                st.session_state.simulation_completed = True

    metrics = st.session_state.realtime_metrics
    elapsed = int(time.time() - st.session_state.get('metrics_start_time', time.time()))

    # Check if simulation is completed
    total_orders = st.session_state.get('num_orders', 50)

    st.subheader("📈 Real-time Metrics (Live)")
    
    # Trigger rerun every 2 seconds for live updates (without blinking)
    if not st.session_state.get('simulation_completed', False):
        # Force rerun after 2 seconds
        if time.time() - st.session_state.get('metrics_update_time', 0) >= 2.0:
            st.rerun()
    
    # Show completion status if simulation is done
    if st.session_state.get('simulation_completed', False):
        st.success("✅ Simulation Completed")
        
        # Restart button
        if st.button("🔄 Restart Simulation"):
            st.session_state.realtime_metrics = {
                'average_pick_time': 60.0,
                'orders_completed': 0,
                'total_distance': 0.0
            }
            st.session_state.metrics_start_time = time.time()
            st.session_state.simulation_completed = False
            st.rerun()
    
    # Stacked metrics boxes with full text
    st.markdown("""
    <style>
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Average Pick Time
    st.markdown(f"""
    <div class="metric-box">
        <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">Average Pick Time</div>
        <div style="font-size: 2rem;">{metrics['average_pick_time']:.1f} seconds</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Orders Completed
    st.markdown(f"""
    <div class="metric-box">
        <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">Orders Completed</div>
        <div style="font-size: 2rem;">{metrics['orders_completed']} / {total_orders}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Total Distance
    st.markdown(f"""
    <div class="metric-box">
        <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">Total Distance</div>
        <div style="font-size: 2rem;">{metrics['total_distance']:.0f} meters</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎮 Simulation Status")
    status_placeholder = st.empty()
    status_placeholder.markdown('<div class="status-idle">Idle</div>', unsafe_allow_html=True)
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("Run Simulation", type="primary"):
            st.session_state.simulation_running = True
            status_placeholder.markdown('<div class="status-running">Running</div>', unsafe_allow_html=True)
            progress_bar = st.progress(0)
            # --- Prepare simulation input ---
            grid_width = st.session_state['grid_width']
            grid_height = st.session_state['grid_height']
            layout_data = None
            if 'layout_config' in st.session_state and st.session_state['layout_config']:
                layout_data = st.session_state['layout_config']
            else:
                layout_data = None
            shelf_positions = []
            packing_stations = []
            if layout_data and isinstance(layout_data, dict):
                shelf_positions = [(s['x'], s['y']) for s in layout_data.get('shelves', [])]
                packing_stations = [(s['x'], s['y']) for s in layout_data.get('stations', [])]
            else:
                shelf_positions = [(3, 3), (5, 3)]
                packing_stations = [(2, 0), (8, 0)]
            num_pickers = st.session_state['num_pickers']
            # --- Orders: uploaded or mock ---
            orders = []
            if 'orders_data' in st.session_state and st.session_state['orders_data'] is not None:
                # Uploaded CSV: parse orders
                df_orders = st.session_state['orders_data']
                # Group by order_id, collect shelf_location as (x, y)
                grouped = df_orders.groupby('order_id')['shelf_location'].apply(list)
                for item_list in grouped:
                    order_items = []
                    for loc in item_list:
                        try:
                            x_str, y_str = str(loc).split(',')
                            order_items.append((int(x_str), int(y_str)))
                        except Exception:
                            continue
                    if order_items:
                        orders.append(order_items)
            else:
                # Generate mock orders
                num_orders = st.session_state['num_orders']
                items_per_order = st.session_state['items_per_order']
                for _ in range(num_orders):
                    if shelf_positions:
                        order_items = random.sample(shelf_positions, min(items_per_order, len(shelf_positions)))
                    else:
                        order_items = []
                    orders.append(order_items)
            # --- Simulate progress bar ---
            for i in range(50):
                progress_bar.progress(int((i+1)*2))
                time.sleep(0.01)
            # --- Call simulation engine ---
            config = {
                'grid_width': grid_width,
                'grid_height': grid_height,
                'shelf_positions': shelf_positions,
                'packing_stations': packing_stations,
                'num_workers': num_pickers,
                'orders': orders
            }
            sim_results = run_simulation(config)
            st.session_state.simulation_results = sim_results
            st.session_state.simulation_running = False
            status_placeholder.markdown('<div class="status-idle">Completed</div>', unsafe_allow_html=True)
            st.rerun()
    with col_b2:
        if st.button("Stop Simulation"):
            st.session_state.simulation_running = False
            status_placeholder.markdown('<div class="status-idle">Stopped</div>', unsafe_allow_html=True)
