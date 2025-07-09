import streamlit as st
from layout import warehouse_layout_section
from metrics import metrics_section
from analytics import analytics_tabs
from data_management import data_management_tab
from reports import reports_tab
import os


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
    import os
    from stable_baselines3 import DQN
    from warehouse_env import WarehouseEnv

    st.subheader("Reinforcement Learning Optimization")

    if st.button("🚀 Optimize Layout with AI"):
        if not os.path.exists("optimized_warehouse_model.zip"):
            st.error("❌ Trained RL model not found. Please train and save the model as 'optimized_warehouse_model.zip' first.")
        else:
            with st.spinner("Running RL Optimization..."):
                # Init environment with fixed config to match trained model
                env = WarehouseEnv(
                    grid_width=12,  # Fixed to match trained model
                    grid_height=10,  # Fixed to match trained model
                    num_orders=st.session_state['num_orders'],
                    items_per_order=st.session_state['items_per_order']
                )
                model = DQN.load("optimized_warehouse_model", env=env)

                obs = env.reset()[0]
                for _ in range(10):  # 10 steps of improvement
                    action, _ = model.predict(obs, deterministic=True)
                    obs, reward, terminated, truncated, info = env.step(action)
                    if terminated or truncated:
                        break

                # Extract optimized layout from environment
                optimized_layout = {
                    'grid_width': st.session_state['grid_width'],
                    'grid_height': st.session_state['grid_height'],
                    'num_pickers': st.session_state['num_pickers'],
                    'layout_type': st.session_state.get('layout_type', 'Grid Layout'),
                    'shelves': [{'x': x, 'y': y} for (x, y) in env.shelves],
                    'stations': [{'x': 2, 'y': 0}, {'x': 8, 'y': 0}]  # Default stations
                }

                st.session_state['layout_config'] = optimized_layout
                st.success("✅ Layout optimized using AI!")
with tab3:
    data_management_tab()
with tab4:
    reports_tab()

# Footer
st.markdown("---")
st.markdown("*Smart Warehouse Flow Simulator*")
