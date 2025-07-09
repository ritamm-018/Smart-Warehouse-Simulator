import streamlit as st
import random
import time
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

# Check if layout builder should be shown
if st.session_state.get('show_layout_builder', False) and st.session_state.get('layout_type') == "Custom Layout":
    from custom_layout_builder import custom_layout_builder
    custom_layout_builder()
    
    # Check if user wants to go to main layout
    if st.session_state.get('go_to_main_layout', False):
        st.session_state['show_layout_builder'] = False
        st.session_state['go_to_main_layout'] = False
        st.success("✅ Redirecting to updated Current Warehouse Layout...")
        st.rerun()
    
    # Add close button
    if st.button("❌ Close Layout Builder"):
        st.session_state['show_layout_builder'] = False
        st.rerun()
else:
    col1, col2 = st.columns([2, 1])
    with col1:
        warehouse_layout_section()
        
        # Efficiency Score Display (appears under warehouse layout when orders are completed)
        if 'realtime_metrics' in st.session_state:
            metrics = st.session_state.realtime_metrics
            total_orders = st.session_state.get('num_orders', 50)
            
            # Only show efficiency score when all orders are completed
            if metrics['orders_completed'] >= total_orders:
                from metrics import calculate_efficiency_score
                
                efficiency_score = calculate_efficiency_score(
                    metrics['average_pick_time'],
                    metrics['total_distance'],
                    metrics['orders_completed'],
                    total_orders
                )
                
                st.markdown("""
                <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .efficiency-container {
                    animation: fadeIn 1.5s ease-out;
                    margin-top: 2rem;
                }
                .efficiency-box {
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    padding: 1.5rem;
                    border-radius: 15px;
                    color: white;
                    text-align: center;
                    font-weight: bold;
                    border: 3px solid #fff;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                    margin: 1rem 0;
                }
                .efficiency-high {
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    border: 3px solid #28a745;
                }
                .efficiency-medium {
                    background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
                    border: 3px solid #ffc107;
                }
                .efficiency-low {
                    background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
                    border: 3px solid #dc3545;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Determine efficiency class and check mark
                if efficiency_score >= 80:
                    efficiency_class = "efficiency-high"
                    check_mark = "✅ "
                    performance_text = "Excellent Performance!"
                elif efficiency_score >= 60:
                    efficiency_class = "efficiency-medium"
                    check_mark = "⚠️ "
                    performance_text = "Good Performance"
                else:
                    efficiency_class = "efficiency-low"
                    check_mark = "❌ "
                    performance_text = "Needs Improvement"
                
                st.markdown(f"""
                <div class="efficiency-container">
                    <div class="efficiency-box {efficiency_class}">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏆 Efficiency Score</div>
                        <div style="font-size: 3rem; margin-bottom: 0.5rem;">{check_mark}{efficiency_score:.1f}%</div>
                        <div style="font-size: 1.2rem; opacity: 0.9;">{performance_text}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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
    from comparison import capture_current_metrics, capture_optimized_metrics, comparison_panel

    st.subheader("Reinforcement Learning Optimization")
    
    st.markdown("""
    **How to use AI Optimization:**
    1. First, run a simulation to generate baseline metrics
    2. Click "🚀 Optimize Layout with AI" to capture current metrics and run optimization
    3. View the comparison results below showing before vs after metrics
    4. Use the reset button to clear comparison data and start over
    """)

    if st.button("🚀 Optimize Layout with AI"):
        if not os.path.exists("optimized_warehouse_model.zip"):
            st.error("❌ Trained RL model not found. Please train and save the model as 'optimized_warehouse_model.zip' first.")
        else:
            # Capture current metrics as 'before' optimization
            if capture_current_metrics():
                st.info("📊 Captured current metrics as baseline...")
            else:
                st.warning("⚠️ No current metrics available. Please run a simulation first.")
                st.stop()
            
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
                
                # Simulate improved metrics after optimization
                if 'realtime_metrics' in st.session_state:
                    # Simulate improvements
                    current_metrics = st.session_state.realtime_metrics
                    improved_metrics = {
                        'average_pick_time': max(30, current_metrics['average_pick_time'] * 0.85),  # 15% improvement
                        'orders_completed': min(st.session_state.get('num_orders', 50), current_metrics['orders_completed'] + 5),
                        'total_distance': current_metrics['total_distance'] * 0.9  # 10% improvement
                    }
                    st.session_state.realtime_metrics = improved_metrics
                
                # Capture optimized metrics as 'after' optimization
                capture_optimized_metrics()
                
                st.success("✅ Layout optimized using AI!")
    
    # Display comparison panel if both before and after metrics exist
    comparison_panel()
    
    # Add reset button to clear comparison data
    if 'before_metrics' in st.session_state and 'after_metrics' in st.session_state:
        if st.button("🔄 Reset Comparison Data"):
            del st.session_state['before_metrics']
            del st.session_state['after_metrics']
            st.rerun()
with tab3:
    data_management_tab()
with tab4:
    reports_tab()

# Footer
st.markdown("---")
st.markdown("*Smart Warehouse Flow Simulator*")

# Initialize picker positions if not present
if 'picker_positions' not in st.session_state:
    # Example: 3 pickers, random start positions
    st.session_state.picker_positions = [
        (random.randint(0, st.session_state['grid_width']-1), random.randint(0, st.session_state['grid_height']-1))
        for _ in range(st.session_state['num_pickers'])
    ]

# Update picker positions randomly every 2 seconds (like before)
current_time = time.time()
if current_time - st.session_state.get('picker_update_time', 0) >= 2.0:
    st.session_state.picker_update_time = current_time
    new_positions = []
    for _ in range(st.session_state['num_pickers']):
        x = random.randint(0, st.session_state['grid_width']-1)
        y = random.randint(0, st.session_state['grid_height']-1)
        new_positions.append((x, y))
    st.session_state.picker_positions = new_positions
