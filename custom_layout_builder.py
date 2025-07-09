import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np
import time
import threading
from queue import PriorityQueue
import math

def create_empty_grid(grid_width, grid_height):
    """Create an empty grid for custom layout building"""
    layout_data = []
    for i in range(grid_height):
        for j in range(grid_width):
            layout_data.append({
                'x': j, 'y': i, 'type': "Empty", 'color': "white", 'symbol': "square"
            })
    return layout_data

def custom_layout_builder():
    """Interactive click-based custom layout builder"""
    
    # Initialize session state for custom layout building
    if 'custom_layout_state' not in st.session_state:
        st.session_state.custom_layout_state = {
            'phase': 'shelves',  # 'shelves', 'stations', 'entry_exit'
            'grid_data': [],
            'shelves': [],
            'stations': [],
            'entry_exit': None,
            'last_width': 0,
            'last_height': 0
        }
    
    grid_width = st.session_state['grid_width']
    grid_height = st.session_state['grid_height']
    
    # Check if grid dimensions have changed
    custom_state = st.session_state.custom_layout_state
    if (custom_state.get('last_width', 0) != grid_width or 
        custom_state.get('last_height', 0) != grid_height):
        # Reset grid when dimensions change
        st.session_state.custom_layout_state = {
            'phase': 'shelves',
            'grid_data': create_empty_grid(grid_width, grid_height),
            'shelves': [],
            'stations': [],
            'entry_exit': None,
            'last_width': grid_width,
            'last_height': grid_height
        }
        st.info(f"🔄 Grid dimensions changed to {grid_width}x{grid_height}. Grid has been reset.")
    
    # Initialize empty grid if not already done
    if not st.session_state.custom_layout_state['grid_data']:
        st.session_state.custom_layout_state['grid_data'] = create_empty_grid(grid_width, grid_height)
        st.session_state.custom_layout_state['last_width'] = grid_width
        st.session_state.custom_layout_state['last_height'] = grid_height
    
    st.markdown("### 🏗️ Custom Layout Builder")
    
    # Debug: Show current grid dimensions
    st.markdown(f"**Current Grid Size: {grid_width} x {grid_height}**")
    
    # Phase indicator
    phase = st.session_state.custom_layout_state['phase']
    if phase == 'shelves':
        st.info("📦 **Phase 1: Place Shelves** - Click on grid cells to place/remove shelves")
    elif phase == 'stations':
        st.info("📦 **Phase 2: Place Packing Stations** - Click on empty cells to place/remove packing stations")
    elif phase == 'entry_exit':
        st.info("📦 **Phase 3: Place Entry/Exit Point** - Click on an empty cell to set entry/exit point")
    
    # Create the interactive grid
    # Controls panel - moved to top
    st.markdown("### Controls")
    
    if phase == 'shelves':
        st.markdown("**Shelf Component:**")
        st.markdown("""
        <div style="
            background: brown; 
            color: white; 
            padding: 10px; 
            border-radius: 5px; 
            text-align: center;
            margin: 10px 0;
            border: 2px solid #fff;
        ">
            📦 Shelf
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Instructions:**")
        st.markdown("""
        1. Click on any grid cell below
        2. The cell will turn brown and become a shelf
        3. Click again to remove it
        4. Place multiple shelves as needed
        """)
        
        # Show current shelf count
        shelf_count = len(st.session_state.custom_layout_state['shelves'])
        st.metric("Shelves Placed", shelf_count)
    
    elif phase == 'stations':
        st.markdown("**Packing Stations:**")
        st.markdown("""
        <div style="
            background: green; 
            color: white; 
            padding: 10px; 
            border-radius: 5px; 
            text-align: center;
            margin: 10px 0;
        ">
            📋 Packing Station
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Instructions:**")
        st.markdown("""
        1. Click on any empty cell below
        2. It will turn green and become a packing station
        3. Click again to remove it
        4. Place multiple stations as needed
        """)
        
        # Show current station count
        station_count = len(st.session_state.custom_layout_state['stations'])
        st.metric("Stations Placed", station_count)
    
    elif phase == 'entry_exit':
        st.markdown("**Entry/Exit Point:**")
        st.markdown("""
        <div style="
            background: blue; 
            color: white; 
            padding: 10px; 
            border-radius: 50%; 
            text-align: center;
            margin: 10px 0;
            width: 60px;
            height: 60px;
            line-height: 40px;
        ">
            🚪
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Instructions:**")
        st.markdown("""
        1. Click on any empty cell below
        2. It will turn blue and become the entry/exit point
        3. Click another cell to move it there
        4. Only one entry/exit point allowed
        """)
        
        # Show current entry/exit status
        if st.session_state.custom_layout_state['entry_exit']:
            st.success("✅ Entry/Exit point placed")
        else:
            st.warning("⚠️ No entry/exit point placed")
    
    # Create clickable grid with large buttons on top right
    st.markdown("### 🎯 Clickable Grid")
    
    # Add buttons on top of the grid
    if phase == 'shelves':
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("")  # Empty space to align with grid
        with col2:
            if st.button("✅ Done with Shelves", 
                        help="Complete shelf placement and move to next phase",
                        use_container_width=True,
                        key="top_done_shelves"):
                if len(st.session_state.custom_layout_state['shelves']) > 0:
                    st.session_state.custom_layout_state['phase'] = 'stations'
                    st.rerun()
                else:
                    st.warning("Please place at least one shelf before proceeding.")
        with col3:
            if st.button("🔄 Reset Layout", 
                        use_container_width=True,
                        key="top_reset_shelves"):
                st.session_state.custom_layout_state = {
                    'phase': 'shelves',
                    'grid_data': create_empty_grid(grid_width, grid_height),
                    'shelves': [],
                    'stations': [],
                    'entry_exit': None
                }
                st.rerun()
    
    elif phase == 'stations':
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.markdown("")  # Empty space to align with grid
        with col2:
            if st.button("✅ Done with Stations", 
                        help="Complete station placement and move to next phase",
                        use_container_width=True,
                        key="top_done_stations"):
                if len(st.session_state.custom_layout_state['stations']) > 0:
                    st.session_state.custom_layout_state['phase'] = 'entry_exit'
                    st.rerun()
                else:
                    st.warning("Please place at least one packing station before proceeding.")
        with col3:
            if st.button("🔙 Back to Shelves", 
                        use_container_width=True,
                        key="top_back_shelves"):
                st.session_state.custom_layout_state['phase'] = 'shelves'
                st.rerun()
        with col4:
            if st.button("🔄 Reset Layout", 
                        use_container_width=True,
                        key="top_reset_stations"):
                st.session_state.custom_layout_state = {
                    'phase': 'shelves',
                    'grid_data': create_empty_grid(grid_width, grid_height),
                    'shelves': [],
                    'stations': [],
                    'entry_exit': None
                }
                st.rerun()
    
    elif phase == 'entry_exit':
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.markdown("")  # Empty space to align with grid
        with col2:
            if st.button("✅ Done with Entry/Exit", 
                        help="Complete entry/exit placement and save layout",
                        use_container_width=True,
                        key="top_done_entry_exit"):
                if st.session_state.custom_layout_state['entry_exit'] is not None:
                    # Save the custom layout
                    save_custom_layout()
                    st.success("✅ Custom layout saved successfully!")
                    
                    # Automatically redirect to main layout
                    st.session_state['show_layout_builder'] = False
                    st.session_state['go_to_main_layout'] = True
                    st.success("🏠 Redirecting to updated Current Warehouse Layout...")
                    st.rerun()
                else:
                    st.warning("Please place an entry/exit point before proceeding.")
        with col3:
            if st.button("🔙 Back to Stations", 
                        use_container_width=True,
                        key="top_back_stations"):
                st.session_state.custom_layout_state['phase'] = 'stations'
                st.rerun()
        with col4:
            if st.button("🔄 Reset Layout", 
                        use_container_width=True,
                        key="top_reset_entry_exit"):
                st.session_state.custom_layout_state = {
                    'phase': 'shelves',
                    'grid_data': create_empty_grid(grid_width, grid_height),
                    'shelves': [],
                    'stations': [],
                    'entry_exit': None
                }
                st.rerun()
    
    # Create the clickable grid
    create_clickable_grid(grid_width, grid_height)
    
    # Show the visual representation
    st.markdown("### 📊 Grid Visualization")
    fig = create_interactive_grid()
    st.plotly_chart(fig, use_container_width=True)
    
    # Add picker simulation section if layout is complete
    if (st.session_state.custom_layout_state['shelves'] and 
        st.session_state.custom_layout_state['stations'] and 
        st.session_state.custom_layout_state['entry_exit']):
        
        st.markdown("---")
        simulate_picker_movement()

def create_clickable_grid(grid_width, grid_height):
    """Create a grid of clickable buttons"""
    # Add CSS for responsive grid sizing and proper alignment
    max_grid_size = 20
    # Calculate button size based on both width and height to maintain fixed grid dimensions
    button_size = max(15, min(50 - (grid_width * 1.5), 50 - (grid_height * 1.5)))
    
    st.markdown(f"""
    <style>
    .grid-button {{
        width: {button_size}px !important;
        height: {button_size}px !important;
        min-width: {button_size}px !important;
        min-height: {button_size}px !important;
        max-width: {button_size}px !important;
        max-height: {button_size}px !important;
        padding: 2px !important;
        margin: 3px !important;
        font-size: {max(8, button_size // 4)}px !important;
        border: 1px solid #ccc !important;
        border-radius: 3px !important;
        overflow: hidden !important;
        white-space: nowrap !important;
        text-overflow: ellipsis !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        aspect-ratio: 1 !important;
    }}
    .axis-label {{
        font-size: 12px !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 2px !important;
        width: {button_size}px !important;
        height: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 3px !important;
        box-sizing: border-box !important;
        position: relative !important;
        left: 0 !important;
        right: 0 !important;
    }}
    .y-axis-label {{
        font-size: 12px !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 2px !important;
        width: 20px !important;
        height: {button_size}px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 3px !important;
        box-sizing: border-box !important;
    }}
    .grid-container {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        max-width: 800px !important;
        max-height: 600px !important;
        overflow: auto !important;
    }}
    .grid-row {{
        display: flex !important;
        align-items: center !important;
        margin: 1px 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Get current grid state
    grid_data = st.session_state.custom_layout_state['grid_data']
    phase = st.session_state.custom_layout_state['phase']
    
    # Create the grid with proper alignment
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    
    # Create grid of buttons first
    for y in range(grid_height):
        # Create row with Y-axis label and buttons
        cols = st.columns(grid_width + 1)  # +1 for Y-axis label
        
        # Y-axis label - reversed order (bottom to top)
        with cols[0]:
            y_label = grid_height - 1 - y  # Reverse the Y-axis values
            st.markdown(f'<div class="y-axis-label">{y_label}</div>', unsafe_allow_html=True)
        
        # Grid buttons
        for x in range(grid_width):
            with cols[x + 1]:
                # Find the cell data
                cell_idx = y * grid_width + x
                cell_data = grid_data[cell_idx]
                
                # Determine cell type and color
                cell_type = cell_data['type']
                if cell_type == 'Shelf':
                    button_color = "#8B4513"  # Brown
                elif cell_type == 'Packing Station':
                    button_color = "#228B22"  # Green
                elif cell_type == 'Entry/Exit':
                    button_color = "#4169E1"  # Blue
                else:
                    button_color = "#f0f0f0"  # Light gray for empty
                
                # Create unique key for each button
                button_key = f"cell_{x}_{y}"
                
                # Create a container for the cell with emoji inside clickable buttons
                with st.container():
                    # Create clickable button with emoji inside
                    if cell_type == 'Shelf':
                        button_text = "📦"
                    elif cell_type == 'Packing Station':
                        button_text = "📋"
                    elif cell_type == 'Entry/Exit':
                        button_text = "🚪"
                    else:
                        button_text = ""
                    
                    # Clickable button with emoji inside
                    # Calculate correct Y coordinate for display (reversed)
                    display_y = grid_height - 1 - y
                    if st.button(button_text, key=button_key, help=f"Click to toggle element at position ({x}, {display_y})"):
                        # Handle click based on current phase - use correct coordinates
                        handle_grid_click(x, display_y)
                        st.rerun()
    
    # Add X-axis labels (column headers) at the bottom - one row
    x_row = st.columns(grid_width + 1)  # +1 for Y-axis space
    with x_row[0]:  # Empty space for Y-axis alignment
        st.markdown('<div class="y-axis-label"></div>', unsafe_allow_html=True)
    for x in range(grid_width):
        with x_row[x + 1]:
            st.markdown(f"""
            <div style="
                width: {button_size}px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                margin: 3px;
                box-sizing: border-box;
            ">
                {x}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def create_interactive_grid():
    """Create an interactive grid with click handling"""
    grid_data = st.session_state.custom_layout_state['grid_data']
    phase = st.session_state.custom_layout_state['phase']
    
    # Create DataFrame for plotting
    df = pd.DataFrame(grid_data)
    
    fig = go.Figure()
    
    # Add grid cells
    for element_type in df['type'].unique():
        element_data = df[df['type'] == element_type]
        if len(element_data) > 0:
            color_val = element_data['color'].values[0]
            symbol_val = element_data['symbol'].values[0]
            
            fig.add_trace(go.Scatter(
                x=element_data['x'].tolist(),
                y=element_data['y'].tolist(),
                mode='markers',
                marker=dict(
                    size=15,
                    color=color_val,
                    symbol=symbol_val,
                    line=dict(width=1, color='black')
                ),
                name=element_type,
                hovertemplate=f"<b>{element_type}</b><br>Position: (%{{x}}, %{{y}})<extra></extra>"
            ))
    
    fig.update_layout(
        title="Custom Layout Grid - Visual Representation",
        xaxis_title="X Position",
        yaxis_title="Y Position",
        width=600,
        height=400,
        showlegend=True,
        plot_bgcolor='lightgray',
        xaxis=dict(showgrid=True, gridcolor='white', range=[-0.5, 19.5]),  # Fixed range 0-20
        yaxis=dict(showgrid=True, gridcolor='white', range=[-0.5, 19.5])   # Fixed range 0-20
    )
    
    return fig

def handle_grid_click(x, display_y):
    """Handle grid cell clicks based on current phase"""
    phase = st.session_state.custom_layout_state['phase']
    grid_data = st.session_state.custom_layout_state['grid_data']
    grid_height = st.session_state['grid_height']
    
    # Convert display Y back to internal Y for array indexing
    internal_y = grid_height - 1 - display_y
    
    # Find the clicked cell using internal coordinates
    cell_idx = internal_y * st.session_state['grid_width'] + x
    
    if phase == 'shelves':
        # Toggle shelf
        if grid_data[cell_idx]['type'] == 'Empty':
            # Add shelf
            grid_data[cell_idx].update({'type': 'Shelf', 'color': 'brown', 'symbol': 'square'})
            st.session_state.custom_layout_state['shelves'].append({'x': x, 'y': display_y})
        elif grid_data[cell_idx]['type'] == 'Shelf':
            # Remove shelf
            grid_data[cell_idx].update({'type': 'Empty', 'color': 'white', 'symbol': 'square'})
            st.session_state.custom_layout_state['shelves'] = [
                s for s in st.session_state.custom_layout_state['shelves'] 
                if not (s['x'] == x and s['y'] == display_y)
            ]
    
    elif phase == 'stations':
        # Toggle packing station
        if grid_data[cell_idx]['type'] == 'Empty':
            # Add packing station
            grid_data[cell_idx].update({'type': 'Packing Station', 'color': 'green', 'symbol': 'diamond'})
            st.session_state.custom_layout_state['stations'].append({'x': x, 'y': display_y})
        elif grid_data[cell_idx]['type'] == 'Packing Station':
            # Remove packing station
            grid_data[cell_idx].update({'type': 'Empty', 'color': 'white', 'symbol': 'square'})
            st.session_state.custom_layout_state['stations'] = [
                s for s in st.session_state.custom_layout_state['stations'] 
                if not (s['x'] == x and s['y'] == display_y)
            ]
    
    elif phase == 'entry_exit':
        # Set entry/exit point
        if grid_data[cell_idx]['type'] == 'Empty':
            # Remove previous entry/exit if exists
            if st.session_state.custom_layout_state['entry_exit']:
                prev_x = st.session_state.custom_layout_state['entry_exit']['x']
                prev_y = st.session_state.custom_layout_state['entry_exit']['y']
                prev_internal_y = grid_height - 1 - prev_y
                prev_idx = prev_internal_y * st.session_state['grid_width'] + prev_x
                grid_data[prev_idx].update({'type': 'Empty', 'color': 'white', 'symbol': 'square'})
            
            # Add new entry/exit
            grid_data[cell_idx].update({'type': 'Entry/Exit', 'color': 'blue', 'symbol': 'circle'})
            st.session_state.custom_layout_state['entry_exit'] = {'x': x, 'y': display_y}

def save_custom_layout():
    """Save the custom layout to session state"""
    custom_state = st.session_state.custom_layout_state
    
    layout_config = {
        'grid_width': st.session_state['grid_width'],
        'grid_height': st.session_state['grid_height'],
        'layout_type': 'Custom Layout',
        'shelves': custom_state['shelves'],
        'stations': custom_state['stations'],
        'entry_exit': [custom_state['entry_exit']] if custom_state['entry_exit'] else []
    }
    
    st.session_state['layout_config'] = layout_config 

def a_star_pathfinding(start, goal, grid_data, grid_width, grid_height):
    """A* pathfinding algorithm to find shortest path between two points"""
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance
    
    def get_neighbors(pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4-directional movement
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
                # Check if the cell is walkable (not a shelf)
                cell_idx = new_y * grid_width + new_x
                if cell_idx < len(grid_data) and grid_data[cell_idx]['type'] != 'Shelf':
                    neighbors.append((new_x, new_y))
        return neighbors
    
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while not frontier.empty():
        current = frontier.get()[1]
        
        if current == goal:
            break
        
        for next_pos in get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + heuristic(goal, next_pos)
                frontier.put((priority, next_pos))
                came_from[next_pos] = current
    
    # Reconstruct path
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    
    return path if path[0] == start else []

def simulate_picker_movement():
    """Simulate picker movement on the warehouse grid"""
    if 'picker_simulation' not in st.session_state:
        st.session_state.picker_simulation = {
            'is_running': False,
            'pickers': [],
            'current_step': 0,
            'orders': [],
            'animation_speed': 500  # milliseconds
        }
    
    # Display simulation controls
    st.markdown("### 🤖 Picker Movement Simulation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start Simulation", key="start_sim"):
            start_simulation()
    with col2:
        if st.button("⏸️ Pause Simulation", key="pause_sim"):
            pause_simulation()
    with col3:
        if st.button("🔄 Reset Simulation", key="reset_sim"):
            reset_simulation()
    
    # Simulation settings
    st.markdown("#### Simulation Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        num_pickers = st.slider("Number of Pickers", 1, 3, 1, key="num_pickers")
    with col2:
        num_orders = st.slider("Number of Orders", 1, 10, 3, key="num_orders")
    with col3:
        animation_speed = st.slider("Animation Speed (ms)", 100, 1000, 500, key="anim_speed")
    
    # Initialize simulation if not already done
    if not st.session_state.picker_simulation['pickers']:
        initialize_simulation()
    
    # Display current simulation state
    if st.session_state.picker_simulation['is_running']:
        st.success("🟢 Simulation Running")
        display_simulation_status()
    else:
        st.info("⏸️ Simulation Paused")
    
    # Display animated grid
    display_animated_grid()

def initialize_simulation():
    """Initialize the picker simulation with orders and picker positions"""
    custom_state = st.session_state.custom_layout_state
    grid_width = st.session_state['grid_width']
    grid_height = st.session_state['grid_height']
    
    # Get layout elements
    shelves = custom_state['shelves']
    stations = custom_state['stations']
    entry_exit = custom_state['entry_exit']
    
    if not entry_exit or not shelves or not stations:
        st.error("❌ Cannot start simulation: Missing entry/exit point, shelves, or stations")
        return False
    
    # Initialize pickers at entry/exit point
    num_pickers = st.session_state.get('num_pickers', 1)
    pickers = []
    for i in range(num_pickers):
        pickers.append({
            'id': i,
            'position': (entry_exit['x'], entry_exit['y']),
            'path': [],
            'current_order': None,
            'status': 'idle',  # idle, moving, picking, dropping
            'color': f'#{i*50:02x}80ff'  # Different blue shades
        })
    
    # Generate random orders
    orders = generate_random_orders(shelves, stations, entry_exit, st.session_state.get('num_orders', 3))
    
    st.session_state.picker_simulation.update({
        'pickers': pickers,
        'orders': orders,
        'current_step': 0,
        'animation_speed': st.session_state.get('anim_speed', 500)
    })
    
    st.success(f"✅ Initialized {num_pickers} picker(s) at position ({entry_exit['x']}, {entry_exit['y']})")
    return True

def generate_random_orders(shelves, stations, entry_exit, num_orders):
    """Generate random orders with items from different shelves"""
    orders = []
    for i in range(num_orders):
        # Random number of items per order (1-3)
        num_items = np.random.randint(1, 4)
        order_items = np.random.choice(shelves, size=min(num_items, len(shelves)), replace=False)
        
        order = {
            'id': i,
            'items': [{'x': item['x'], 'y': item['y']} for item in order_items],
            'station': np.random.choice(stations),
            'status': 'pending',  # pending, in_progress, completed
            'assigned_picker': None
        }
        orders.append(order)
    
    return orders

def start_simulation():
    """Start the picker movement simulation"""
    if initialize_simulation():
        st.session_state.picker_simulation['is_running'] = True
        st.rerun()

def pause_simulation():
    """Pause the simulation"""
    st.session_state.picker_simulation['is_running'] = False

def reset_simulation():
    """Reset the simulation to initial state"""
    st.session_state.picker_simulation = {
        'is_running': False,
        'pickers': [],
        'current_step': 0,
        'orders': [],
        'animation_speed': 500
    }
    st.rerun()

def display_simulation_status():
    """Display current simulation status"""
    sim = st.session_state.picker_simulation
    
    col1, col2, col3 = st.columns(3)
    with col1:
        active_pickers = sum(1 for p in sim['pickers'] if p['status'] != 'idle')
        st.metric("Active Pickers", active_pickers)
    with col2:
        completed_orders = sum(1 for o in sim['orders'] if o['status'] == 'completed')
        st.metric("Completed Orders", completed_orders)
    with col3:
        pending_orders = sum(1 for o in sim['orders'] if o['status'] == 'pending')
        st.metric("Pending Orders", pending_orders)

def display_animated_grid():
    """Display the warehouse grid with animated picker movement"""
    sim = st.session_state.picker_simulation
    grid_width = st.session_state['grid_width']
    grid_height = st.session_state['grid_height']
    grid_data = st.session_state.custom_layout_state['grid_data']
    
    # Debug information
    st.write(f"Debug: Number of pickers: {len(sim['pickers'])}")
    if sim['pickers']:
        for i, picker in enumerate(sim['pickers']):
            st.write(f"Picker {i}: Position {picker['position']}, Status: {picker['status']}")
    
    # Create animated grid visualization
    fig = go.Figure()
    
    # Add static elements (shelves, stations, entry/exit)
    for element_type in ['Shelf', 'Packing Station', 'Entry/Exit']:
        elements = [cell for cell in grid_data if cell['type'] == element_type]
        if elements:
            x_coords = [cell['x'] for cell in elements]
            y_coords = [cell['y'] for cell in elements]
            
            if element_type == 'Shelf':
                color = 'brown'
                symbol = 'square'
            elif element_type == 'Packing Station':
                color = 'green'
                symbol = 'diamond'
            else:
                color = 'blue'
                symbol = 'circle'
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers',
                marker=dict(size=20, color=color, symbol=symbol, line=dict(width=2, color='black')),
                name=element_type,
                showlegend=True
            ))
    
    # Add pickers with blinking effect
    if sim['pickers']:
        for picker in sim['pickers']:
            x, y = picker['position']
            
            # Create blinking effect
            opacity = 0.3 + 0.7 * (sim['current_step'] % 10 < 5)  # Blink every 5 steps
            
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers',
                marker=dict(
                    size=30,  # Made larger for visibility
                    color=picker['color'],
                    symbol='circle',
                    line=dict(width=3, color='white'),
                    opacity=opacity
                ),
                name=f"Picker {picker['id'] + 1}",
                showlegend=True
            ))
    
    # Add paths for moving pickers
    for picker in sim['pickers']:
        if picker['path'] and len(picker['path']) > 1:
            path_x = [pos[0] for pos in picker['path']]
            path_y = [pos[1] for pos in picker['path']]
            
            fig.add_trace(go.Scatter(
                x=path_x,
                y=path_y,
                mode='lines',
                line=dict(color=picker['color'], width=2, dash='dot'),
                name=f"Picker {picker['id'] + 1} Path",
                showlegend=False
            ))
    
    fig.update_layout(
        title="Warehouse Grid with Picker Movement",
        xaxis_title="X Position",
        yaxis_title="Y Position",
        width=600,
        height=400,
        showlegend=True,
        plot_bgcolor='lightgray',
        xaxis=dict(showgrid=True, gridcolor='white', range=[-0.5, grid_width-0.5]),
        yaxis=dict(showgrid=True, gridcolor='white', range=[-0.5, grid_height-0.5])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Auto-update simulation if running
    if sim['is_running']:
        time.sleep(sim['animation_speed'] / 1000)  # Convert ms to seconds
        update_simulation_step()
        st.rerun()

def update_simulation_step():
    """Update one step of the simulation"""
    sim = st.session_state.picker_simulation
    sim['current_step'] += 1
    
    # Update picker movements
    for picker in sim['pickers']:
        update_picker_movement(picker, sim['orders'])

def update_picker_movement(picker, orders):
    """Update individual picker movement"""
    if picker['status'] == 'idle':
        # Assign new order if available
        pending_orders = [o for o in orders if o['status'] == 'pending']
        if pending_orders:
            order = pending_orders[0]
            order['status'] = 'in_progress'
            order['assigned_picker'] = picker['id']
            picker['current_order'] = order
            picker['status'] = 'moving'
            
            # Calculate path to first item
            if order['items']:
                first_item = order['items'][0]
                path = calculate_picker_path(picker['position'], (first_item['x'], first_item['y']))
                picker['path'] = path
    
    elif picker['status'] == 'moving':
        if picker['path']:
            # Move to next position in path
            next_pos = picker['path'].pop(0)
            picker['position'] = next_pos
            
            if not picker['path']:
                # Reached destination
                if picker['current_order'] and picker['current_order']['items']:
                    picker['status'] = 'picking'
                else:
                    picker['status'] = 'dropping'
    
    elif picker['status'] == 'picking':
        # Simulate picking time
        if picker['current_order'] and picker['current_order']['items']:
            # Remove picked item
            picker['current_order']['items'].pop(0)
            
            if picker['current_order']['items']:
                # Move to next item
                next_item = picker['current_order']['items'][0]
                path = calculate_picker_path(picker['position'], (next_item['x'], next_item['y']))
                picker['path'] = path
                picker['status'] = 'moving'
            else:
                # All items picked, move to station
                station = picker['current_order']['station']
                path = calculate_picker_path(picker['position'], (station['x'], station['y']))
                picker['path'] = path
                picker['status'] = 'moving'
    
    elif picker['status'] == 'dropping':
        # Simulate drop-off time
        if picker['current_order']:
            picker['current_order']['status'] = 'completed'
            picker['current_order'] = None
            picker['status'] = 'idle'
            
            # Return to entry/exit
            entry_exit = st.session_state.custom_layout_state['entry_exit']
            path = calculate_picker_path(picker['position'], (entry_exit['x'], entry_exit['y']))
            picker['path'] = path
            picker['status'] = 'moving'

def calculate_picker_path(start, goal):
    """Calculate path for picker movement"""
    grid_data = st.session_state.custom_layout_state['grid_data']
    grid_width = st.session_state['grid_width']
    grid_height = st.session_state['grid_height']
    
    # Use A* pathfinding
    path = a_star_pathfinding(start, goal, grid_data, grid_width, grid_height)
    
    # If A* fails, use simple direct path
    if not path:
        path = [start, goal]
    
    return path 