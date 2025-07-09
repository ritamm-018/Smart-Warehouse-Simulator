import streamlit as st
import pandas as pd
from datetime import datetime

def reports_tab():
    st.subheader(" Simulation Reports")
    st.write("**Simulation Summary Report**")
    if st.session_state.simulation_results:
        report_data = {
            'Simulation Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Layout Type': st.session_state['layout_type'],
            'Grid Size': f"{st.session_state['grid_width']}x{st.session_state['grid_height']}",
            'Number of Pickers': st.session_state['num_pickers'],
            'Picker Speed': st.session_state['picker_speed'],
            'Total Orders': st.session_state['num_orders'],
            'Items per Order': st.session_state['items_per_order'],
            'Average Pick Time': f"{st.session_state.simulation_results['avg_pick_time']:.2f}s",
            'Total Distance': f"{st.session_state.simulation_results['total_distance']:.2f}m",
            'Efficiency Score': f"{st.session_state.simulation_results['efficiency_score']:.1f}%"
        }
        for key, value in report_data.items():
            st.write(f"**{key}**: {value}")
        if st.button(" Generate Full Report"):
            report_df = pd.DataFrame(list(report_data.items()), columns=['Parameter', 'Value'])
            csv_report = report_df.to_csv(index=False)
            st.download_button(
                label=" Download Report",
                data=csv_report,
                file_name=f"warehouse_simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info(" Run a simulation first to generate reports.")
