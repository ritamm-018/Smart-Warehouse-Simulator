import streamlit as st
import pandas as pd
from datetime import datetime

def reports_tab():
    st.subheader(" Simulation Reports")
    st.write("**Simulation Summary Report**")
    if st.session_state.simulation_results:
        results = st.session_state.simulation_results
        report_data = {
            'Simulation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Layout Type': st.session_state['layout_type'],
            'Grid Size': f"{st.session_state['grid_width']}x{st.session_state['grid_height']}",
            'Number of Pickers': st.session_state['num_pickers'],
            'Picker Speed': st.session_state['picker_speed'],
            'Total Orders': st.session_state['num_orders'],
            'Items per Order': st.session_state['items_per_order'],
            'Average Pick Time': f"{results.get('average_pick_time', 0):.2f}s",
            'Total Distance': f"{results.get('total_distance', 0):.2f}m",
            'Efficiency Score': f"{results.get('efficiency_score', 0):.1f}%"
        }
        for key, value in report_data.items():
            st.write(f"**{key}**: {value}")
        if st.button(" Generate Full Report"):
            report_df = pd.DataFrame({
                'Parameter': list(report_data.keys()),
                'Value': list(report_data.values())
            })
            csv_report = report_df.to_csv(index=False)
            st.download_button(
                label=" Download Report",
                data=csv_report,
                file_name=f"warehouse_simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info(" Run a simulation first to generate reports.")
    # --- Full Simulation Report Export ---
    st.write("\n---\n")
    st.write("📄 **Export Full Simulation Report**")
    if st.session_state.get('simulation_results'):
        results = st.session_state['simulation_results']
        layout_config = st.session_state.get('layout_config', {})
        # Layout info
        layout_type = st.session_state.get('layout_type', 'Unknown')
        grid_size = f"{st.session_state.get('grid_width', '?')}x{st.session_state.get('grid_height', '?')}"
        # Simulation config
        num_pickers = st.session_state.get('num_pickers', '?')
        picker_speed = st.session_state.get('picker_speed', '?')
        items_per_order = st.session_state.get('items_per_order', '?')
        num_orders = st.session_state.get('num_orders', '?')
        # Performance metrics
        avg_pick_time = results.get('average_pick_time', 0)
        total_distance = results.get('total_distance', 0)
        efficiency = results.get('efficiency_score', None)
        # RL info
        rl_used = st.session_state.get('rl_used', False)
        reward = results.get('reward', None)
        # Congestion stats
        activity_map = results.get('activity_map', None)
        congestion_threshold = 6
        high_traffic_cells = 0
        avg_congestion = None
        peak_congestion = None
        if activity_map:
            flat = [cell for row in activity_map for cell in row]
            high_traffic_cells = sum(1 for v in flat if v >= congestion_threshold)
            avg_congestion = sum(flat) / len(flat) if flat else 0
            peak_congestion = max(flat) if flat else 0
        report_dict = {
            'Simulation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Layout Type': layout_type,
            'Grid Size': grid_size,
            'Number of Pickers': num_pickers,
            'Picker Speed': picker_speed,
            'Items per Order': items_per_order,
            'Total Orders': num_orders,
            'Average Pick Time (s)': f"{avg_pick_time:.2f}",
            'Total Distance (m)': f"{total_distance:.2f}",
            'Efficiency Score (%)': f"{efficiency:.1f}" if efficiency is not None else 'N/A',
            'High Traffic Cells (congestion >= 6)': high_traffic_cells,
            'Average Congestion': f"{avg_congestion:.2f}" if avg_congestion is not None else 'N/A',
            'Peak Congestion': peak_congestion if peak_congestion is not None else 'N/A',
            'RL Used': 'Yes' if rl_used else 'No',
            'RL Reward': reward if reward is not None else 'N/A',
            'RL Improved Layout': 'Yes' if rl_used else 'No',
        }
        if st.button("📤 Download Full Report (CSV)"):
            report_df = pd.DataFrame({
                'Parameter': list(report_dict.keys()),
                'Value': list(report_dict.values())
            })
            st.download_button(
                label="Download CSV",
                data=report_df.to_csv(index=False),
                file_name=f"warehouse_full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        st.caption("Optional: For PDF export, install pdfkit, reportlab, or fpdf and add PDF export logic.")
