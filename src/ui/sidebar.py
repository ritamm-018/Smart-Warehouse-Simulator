import streamlit as st
import os
from custom_layout_builder import custom_layout_builder
from utils.warehouse_data_loader import load_sample_warehouse_data

def sidebar_config():
    st.sidebar.markdown("""
    <style>
        .sidebar-section-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #2563eb;
            margin-top: 1.2rem;
            margin-bottom: 0.5rem;
            letter-spacing: 0.5px;
        }
        .sidebar-divider {
            border: none;
            border-top: 2px solid #e0e7ef;
            margin: 1.2rem 0 1rem 0;
        }
        .sidebar-metric {
            font-size: 1.05rem;
            color: #1f2937;
            margin-bottom: 0.2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-section-title">Configuration</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-section-title">Warehouse Layout</div>', unsafe_allow_html=True)
    
    # Add sample layouts option - using radio buttons to prevent typing
    layout_options = ["Custom Layout", "Grid Layout", "L-Shape Layout", "U-Shape Layout", "Sample Layouts"]
    st.session_state['layout_type'] = st.sidebar.radio(
        "Select Layout Type",
        layout_options,
        key="layout_type_select",
        help="Choose from predefined layout types"
    )
    
    # Show sample layouts section
    if st.session_state['layout_type'] == "Sample Layouts":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Sample Warehouse Layouts")
        st.sidebar.markdown("Load pre-configured layouts from major retailers")
        
        from utils.warehouse_data_loader import WarehouseDataLoader
        loader = WarehouseDataLoader()
        available_layouts = loader.get_available_layouts()
        
        selected_sample = st.sidebar.selectbox(
            "Choose a warehouse layout:",
            available_layouts,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_sample:
            # Display layout info
            layout_data = loader.load_layout_from_json(loader.sample_layouts[selected_sample])
            if layout_data:
                st.sidebar.markdown(f"**{layout_data['name']}**")
                st.sidebar.markdown(f"Size: {layout_data['grid_width']}x{layout_data['grid_height']}")
                st.sidebar.markdown(f"Shelves: {len(layout_data['shelves'])}")
                st.sidebar.markdown(f"Stations: {len(layout_data['stations'])}")
        
        if st.sidebar.button("Load Sample Layout"):
            grid_data = loader.load_and_convert_layout(selected_sample)
            if grid_data:
                # Update session state with the loaded layout
                st.session_state['grid_width'] = grid_data['grid_width']
                st.session_state['grid_height'] = grid_data['grid_height']
                st.session_state['layout_type'] = grid_data['layout_type']
                
                # Update custom layout state if it exists
                if 'custom_layout_state' not in st.session_state:
                    st.session_state.custom_layout_state = {}
                
                st.session_state.custom_layout_state.update({
                    'grid_data': grid_data['grid_data'],
                    'shelves': [cell for cell in grid_data['grid_data'] if cell['type'] == 'Shelf'],
                    'stations': [cell for cell in grid_data['grid_data'] if cell['type'] == 'Packing Station'],
                    'entry_exit': next((cell for cell in grid_data['grid_data'] if cell['type'] == 'Entry/Exit'), None),
                    'layout_name': grid_data['layout_name'],
                    'layout_description': grid_data['layout_description']
                })
                
                st.sidebar.success(f"Loaded {grid_data['layout_name']} successfully!")
                st.rerun()
    
    # Show custom layout options when Custom Layout is selected
    if st.session_state['layout_type'] == "Custom Layout":
        st.sidebar.markdown("---")
        
        # Option 2: Upload Custom Layout (JSON)
        st.session_state['uploaded_layout'] = st.sidebar.file_uploader(
            "Upload Custom Layout (JSON)",
            type=['json'],
            help="Upload a JSON file with shelf and station positions"
        )
    else:
        st.session_state['uploaded_layout'] = None
    
    # Clear sample layout when switching to other layout types
    if st.session_state['layout_type'] != "Sample Layouts" and 'custom_layout_state' in st.session_state and st.session_state.custom_layout_state.get('grid_data'):
        if st.sidebar.button("Clear Sample Layout"):
            st.session_state.custom_layout_state = {}
            st.sidebar.success("Sample layout cleared!")
            st.rerun()
    
    st.session_state['grid_width'] = st.sidebar.slider("Grid Width", 5, 20, 12)
    st.session_state['grid_height'] = st.sidebar.slider("Grid Height", 5, 20, 8)
    st.sidebar.subheader("Simulation Settings")
    st.session_state['num_pickers'] = st.sidebar.slider("Number of Pickers", 1, 10, 3)
    st.session_state['picker_speed'] = st.sidebar.select_slider(
        "Picker Speed",
        options=['Slow', 'Medium', 'Fast'],
        value='Medium'
    )
    st.sidebar.subheader("Order Settings")
    st.session_state['num_orders'] = st.sidebar.slider("Number of Orders", 10, 500, 50)
    st.session_state['items_per_order'] = st.sidebar.slider("Items per Order", 1, 20, 5)
    
    # Sample orders section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Sample Orders")
    st.sidebar.markdown("Load pre-generated order data")
    
    from utils.warehouse_data_loader import WarehouseDataLoader
    loader = WarehouseDataLoader()
    available_layouts = loader.get_available_layouts()
    
    selected_order_layout = st.sidebar.selectbox(
        "Choose sample orders:",
        available_layouts,
        format_func=lambda x: x.replace('_', ' ').title(),
        key="sample_orders_select"
    )
    
    if st.sidebar.button("Load Sample Orders", key="load_sample_orders"):
        try:
            orders_file = f"sample_data/{selected_order_layout}_orders.csv"
            if os.path.exists(orders_file):
                # Load the CSV file and store it in session state
                import pandas as pd
                orders_df = pd.read_csv(orders_file)
                st.session_state['sample_orders_data'] = orders_df
                st.session_state['current_orders_file'] = orders_file
                st.sidebar.success(f"Loaded {len(orders_df)} orders from {selected_order_layout.replace('_', ' ').title()}")
                st.rerun()
            else:
                st.sidebar.error(f"Orders file not found: {orders_file}")
        except Exception as e:
                            st.sidebar.error(f"Error loading orders: {str(e)}")
    
    # Show current loaded orders info
    if 'sample_orders_data' in st.session_state:
        orders_df = st.session_state['sample_orders_data']
        st.sidebar.markdown(f"**Current Orders:** {len(orders_df)} items")
        st.sidebar.markdown(f"**File:** {st.session_state.get('current_orders_file', 'Unknown')}")
        
        if st.sidebar.button("Clear Sample Orders", key="clear_sample_orders"):
            del st.session_state['sample_orders_data']
            del st.session_state['current_orders_file']
            st.sidebar.success("Sample orders cleared!")
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Upload Custom Orders")
    st.session_state['uploaded_orders'] = st.sidebar.file_uploader(
        "Upload Orders CSV",
        type=['csv'],
        help="CSV should have columns: order_id, item_id, shelf_location_x, shelf_location_y, zone, item_type, priority, quantity"
    )
    st.sidebar.subheader("Simulation Controls")
    st.session_state['simulation_speed'] = st.sidebar.select_slider(
        "Simulation Speed",
        options=['1x', '2x', '5x', '10x'],
        value='5x'
    )
    
    # Data Persistence Controls
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Data Persistence")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.sidebar.button("Save Layout"):
            from utils.data_persistence import save_current_layout
            layout_id = save_current_layout()
            if layout_id:
                st.sidebar.success(f"Layout saved!")
    
    with col2:
        if st.sidebar.button("View Stats"):
            from utils.data_persistence import persistence
            stats = persistence.get_database_stats()
            st.sidebar.json(stats)
    
    # Auto-save toggle
    auto_save = st.sidebar.checkbox("Auto-save enabled", value=st.session_state.get('auto_save_enabled', True))
    if auto_save != st.session_state.get('auto_save_enabled', True):
        st.session_state.auto_save_enabled = auto_save
