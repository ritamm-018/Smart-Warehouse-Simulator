import streamlit as st
import numpy as np
import time

def metrics_section():
    st.subheader("Real-time Metrics")
    if st.session_state.simulation_results:
        results = st.session_state.simulation_results
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Avg Pick Time", f"{results.get('avg_pick_time', 0):.1f}s")
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
            for i in range(100):
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            st.session_state.simulation_results = {
                'avg_pick_time': np.random.uniform(45, 85),
                'orders_completed': st.session_state['num_orders'],
                'total_distance': np.random.uniform(1000, 2000),
                'efficiency_score': np.random.uniform(60, 95)
            }
            status_placeholder.markdown('<div class="status-idle">Completed</div>', unsafe_allow_html=True)
            st.rerun()
    with col_b2:
        if st.button("Stop Simulation"):
            status_placeholder.markdown('<div class="status-idle">Stopped</div>', unsafe_allow_html=True)
