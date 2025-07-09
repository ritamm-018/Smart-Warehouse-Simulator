import streamlit as st
import numpy as np
import time
import random
import pandas as pd
from sim_engine import run_simulation

def metrics_section():
    st.subheader("Real-time Metrics")
    if st.session_state.simulation_results:
        results = st.session_state.simulation_results
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Avg Pick Time", f"{results.get('average_pick_time', 0):.1f}s")
            st.metric("Orders Completed", results.get('orders_completed', 0))
        with col_m2:
            st.metric("Total Distance", f"{results.get('total_distance', 0):.1f}m")
            st.metric("Efficiency Score", f"{results.get('efficiency_score', 0):.1f}%")
    else:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Avg Pick Time", "0.0s")
            st.metric("Orders Completed", "0")
        with col_m2:
            st.metric("Total Distance", "0.0m")
            st.metric("Efficiency Score", "0.0%")
    st.subheader("🎮 Simulation Status")
    status_placeholder = st.empty()
    status_placeholder.markdown('<div class="status-idle">Idle</div>', unsafe_allow_html=True)
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("Run Simulation", type="primary"):
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
            status_placeholder.markdown('<div class="status-idle">Completed</div>', unsafe_allow_html=True)
            st.rerun()
    with col_b2:
        if st.button("Stop Simulation"):
            status_placeholder.markdown('<div class="status-idle">Stopped</div>', unsafe_allow_html=True)
