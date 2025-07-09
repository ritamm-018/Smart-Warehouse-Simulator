import streamlit as st
import pandas as pd
import json
from datetime import datetime
import numpy as np

def data_management_tab():
    st.subheader("Data Management")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.write("**Export Data**")
        if st.button("Export Simulation Results"):
            results_df = pd.DataFrame({
                'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
                'pick_time': np.random.uniform(40, 80, 100),
                'distance': np.random.uniform(50, 150, 100),
                'orders_completed': np.random.randint(10, 30, 100)
            })
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"warehouse_simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        if st.button("Export Layout Configuration"):
            layout_config = {
                'grid_width': st.session_state['grid_width'],
                'grid_height': st.session_state['grid_height'],
                'num_pickers': st.session_state['num_pickers'],
                'layout_type': st.session_state['layout_type'],
                'shelves': [{'x': 3, 'y': 3}, {'x': 5, 'y': 3}],
                'stations': [{'x': 2, 'y': 0}, {'x': 8, 'y': 0}]
            }
            json_str = json.dumps(layout_config, indent=2)
            st.download_button(
                label="Download",
                data=json_str,
                file_name=f"warehouse_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    with col_d2:
        st.write("**Import Data**")
        uploaded_orders = st.session_state['uploaded_orders']
        uploaded_layout = st.session_state['uploaded_layout']
        if uploaded_orders:
            df_orders = pd.read_csv(uploaded_orders)
            st.write("📋 **Orders Data Preview:**")
            st.dataframe(df_orders.head())
            if st.button("✅ Use This Orders Data"):
                st.session_state.orders_data = df_orders
                st.success("Orders data loaded successfully!")
        if uploaded_layout:
            layout_json = json.load(uploaded_layout)
            st.write("🗺️ **Layout Configuration:**")
            st.json(layout_json)
            if st.button("✅ Use This Layout"):
                st.session_state.layout_config = layout_json
                st.success("Layout configuration loaded successfully!")
