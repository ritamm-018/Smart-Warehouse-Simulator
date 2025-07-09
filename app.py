import streamlit as st
from layout import warehouse_layout_section
from metrics import metrics_section
from analytics import analytics_tabs
from data_management import data_management_tab
from reports import reports_tab


st.set_page_config(
    page_title="Smart Warehouse Flow Simulator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .status-running {
        background-color: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    .status-idle {
        background-color: #6c757d;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'layout_config' not in st.session_state:
    st.session_state.layout_config = None
if 'orders_data' not in st.session_state:
    st.session_state.orders_data = None

st.markdown('<div class="main-header">Warehouse Simulator</div>', unsafe_allow_html=True)


from sidebar import sidebar_config
sidebar_config()


col1, col2 = st.columns([2, 1])
with col1:
    warehouse_layout_section()
with col2:
    metrics_section()


tab1, tab2, tab3, tab4 = st.tabs([
    "Performance Analytics",
    " RL Optimization",
    " Data Management",
    " Reports"
])

with tab1:
    analytics_tabs()
with tab2:
    # This is a demo UI only, no RL logic is run
    st.subheader("Reinforcement Learning Optimization")
    
with tab3:
    data_management_tab()
with tab4:
    reports_tab()

# Footer
st.markdown("---")
st.markdown("*Smart Warehouse Flow Simulator*")
