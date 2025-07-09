import streamlit as st

def sidebar_config():
    st.sidebar.header("Configuration")
    st.sidebar.subheader("Warehouse Layout")
    st.session_state['layout_type'] = st.sidebar.selectbox(
        "Select Layout Type",
        ["Grid Layout", "L-Shape Layout", "U-Shape Layout", "Custom Layout"]
    )
    st.session_state['grid_width'] = st.sidebar.slider("Grid Width", 5, 20, 12)
    st.session_state['grid_height'] = st.sidebar.slider("Grid Height", 5, 20, 8)
    st.session_state['uploaded_layout'] = st.sidebar.file_uploader(
        "Upload Custom Layout (JSON)",
        type=['json'],
        help="Upload a JSON file with shelf and station positions"
    )
    st.sidebar.subheader("Agent Settings")
    st.session_state['num_pickers'] = st.sidebar.slider("Number of Pickers", 1, 10, 3)
    st.session_state['picker_speed'] = st.sidebar.select_slider(
        "Picker Speed",
        options=['Slow', 'Medium', 'Fast'],
        value='Medium'
    )
    st.sidebar.subheader(" Order Settings")
    st.session_state['num_orders'] = st.sidebar.slider("Number of Orders", 10, 500, 50)
    st.session_state['items_per_order'] = st.sidebar.slider("Items per Order", 1, 20, 5)
    st.session_state['uploaded_orders'] = st.sidebar.file_uploader(
        "Upload Orders CSV",
        type=['csv'],
        help="CSV should have columns: order_id, item_id, shelf_location"
    )
    st.sidebar.subheader("Simulation Controls")
    st.session_state['simulation_speed'] = st.sidebar.select_slider(
        "Simulation Speed",
        options=['1x', '2x', '5x', '10x'],
        value='5x'
    )
