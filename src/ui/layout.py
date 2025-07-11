import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import random
import time

def manhattan_distance(p1, p2):
    """
    Calculate the Manhattan distance between two points on the grid.
    
    Args:
        p1: Tuple (x1, y1) representing the first point
        p2: Tuple (x2, y2) representing the second point
        
    Returns:
        int: Manhattan distance between the two points
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_picker_speed(label: str):
    """
    Map picker speed labels to numeric values.
    
    Args:
        label: String representing the speed ("Slow", "Medium", "Fast")
        
    Returns:
        int: Numeric speed value (1, 2, or 3)
    """
    speed_mapping = {
        "Slow": 1,
        "Medium": 2,
        "Fast": 3
    }
    return speed_mapping.get(label, 2)  # Default to Medium (2) if label not found

def calculate_order_distance(order_items, layout_metadata):
    """
    Calculate the total path distance for an order through the warehouse.
    
    Args:
        order_items: List of item coordinates [(x1, y1), (x2, y2), ...] representing shelf locations
        layout_metadata: Dictionary containing coordinates of layout elements
        
    Returns:
        dict: Order path information including total distance and path details
    """
    if not order_items:
        return {
            "total_distance": 0,
            "path": [],
            "entry_point": None,
            "packing_station": None,
            "item_sequence": []
        }
    
    entry_points = layout_metadata["entry_points"]
    packing_stations = layout_metadata["packing_stations"]
    
    # Step 1: Choose the nearest entry point to the first item
    first_item = order_items[0]
    nearest_entry = min(entry_points, key=lambda ep: manhattan_distance(first_item, ep))
    entry_distance = manhattan_distance(first_item, nearest_entry)
    
    # Step 2: Choose the nearest packing station from the last item
    last_item = order_items[-1]
    nearest_packing = min(packing_stations, key=lambda ps: manhattan_distance(last_item, ps))
    packing_distance = manhattan_distance(last_item, nearest_packing)
    
    # Step 3: Calculate total path distance
    # Path: Entry -> Item1 -> Item2 -> ... -> ItemN -> Packing Station
    total_distance = entry_distance
    
    # Add distances between consecutive items
    for i in range(len(order_items) - 1):
        item_distance = manhattan_distance(order_items[i], order_items[i + 1])
        total_distance += item_distance
    
    # Add distance from last item to packing station
    total_distance += packing_distance
    
    # Create path sequence
    path_sequence = [nearest_entry] + order_items + [nearest_packing]
    
    return {
        "total_distance": total_distance,
        "path": path_sequence,
        "entry_point": nearest_entry,
        "packing_station": nearest_packing,
        "item_sequence": order_items,
        "entry_distance": entry_distance,
        "packing_distance": packing_distance,
        "inter_item_distances": [
            manhattan_distance(order_items[i], order_items[i + 1])
            for i in range(len(order_items) - 1)
        ]
    }

def extract_layout_metadata(layout_data):
    """
    Extract layout metadata from warehouse layout grid data.
    
    Args:
        layout_data: List of dictionaries containing cell information with 'x', 'y', 'type' keys
        
    Returns:
        dict: Layout metadata with coordinates of shelves, packing stations, and entry points
    """
    layout_metadata = {
        "shelves": [],
        "packing_stations": [],
        "entry_points": []
    }
    
    for cell in layout_data:
        x, y = cell['x'], cell['y']
        cell_type = cell['type']
        
        if cell_type == "Shelf":
            layout_metadata["shelves"].append((x, y))
        elif cell_type == "Packing Station":
            layout_metadata["packing_stations"].append((x, y))
        elif cell_type == "Entry/Exit":
            layout_metadata["entry_points"].append((x, y))
    
    return layout_metadata

def calculate_distances(layout_metadata):
    """
    Calculate Manhattan distances between different layout elements.
    
    Args:
        layout_metadata: Dictionary containing coordinates of layout elements
        
    Returns:
        dict: Distance calculations between various layout elements
    """
    distances = {
        "shelf_to_packing_station": [],
        "entry_to_packing_station": [],
        "shelf_to_entry": [],
        "shelf_to_shelf": []
    }
    
    shelves = layout_metadata["shelves"]
    packing_stations = layout_metadata["packing_stations"]
    entry_points = layout_metadata["entry_points"]
    
    # Calculate distances from shelves to packing stations
    for shelf in shelves:
        for station in packing_stations:
            dist = manhattan_distance(shelf, station)
            distances["shelf_to_packing_station"].append({
                "from": shelf,
                "to": station,
                "distance": dist
            })
    
    # Calculate distances from entry points to packing stations
    for entry in entry_points:
        for station in packing_stations:
            dist = manhattan_distance(entry, station)
            distances["entry_to_packing_station"].append({
                "from": entry,
                "to": station,
                "distance": dist
            })
    
    # Calculate distances from shelves to entry points
    for shelf in shelves:
        for entry in entry_points:
            dist = manhattan_distance(shelf, entry)
            distances["shelf_to_entry"].append({
                "from": shelf,
                "to": entry,
                "distance": dist
            })
    
    # Calculate distances between shelves
    for i, shelf1 in enumerate(shelves):
        for j, shelf2 in enumerate(shelves):
            if i < j:  # Avoid duplicate pairs
                dist = manhattan_distance(shelf1, shelf2)
                distances["shelf_to_shelf"].append({
                    "from": shelf1,
                    "to": shelf2,
                    "distance": dist
                })
    
    return distances

def run_order_simulation(layout_data, num_orders=50, items_per_order=5):
    """
    Run a complete order simulation using the current warehouse layout.
    
    Args:
        layout_data: List of layout cells with coordinates and types
        num_orders: Number of orders to simulate
        items_per_order: Number of items per order
        
    Returns:
        dict: Simulation results with total distance, total time, and completed orders
    """
    # Extract layout metadata
    layout_metadata = extract_layout_metadata(layout_data)
    
    # Get picker speed
    picker_speed_label = st.session_state.get('picker_speed', 'Medium')
    picker_speed_numeric = get_picker_speed(picker_speed_label)
    
    # Get shelf positions for order generation
    shelf_positions = layout_metadata["shelves"]
    
    # Initialize simulation results
    total_distance = 0
    total_time = 0
    completed_orders = 0
    order_details = []
    
    # Generate and process orders
    for order_id in range(num_orders):
        # Generate random order items from available shelves
        if shelf_positions:
            order_items = random.sample(shelf_positions, min(items_per_order, len(shelf_positions)))
        else:
            order_items = []
        
        if order_items:
            # Calculate order distance using the existing function
            order_analysis = calculate_order_distance(order_items, layout_metadata)
            
            # Calculate time based on distance and picker speed
            order_distance = order_analysis["total_distance"]
            order_time = order_distance / picker_speed_numeric if picker_speed_numeric > 0 else 0
            
            # Accumulate totals
            total_distance += order_distance
            total_time += order_time
            completed_orders += 1
            
            # Store order details
            order_details.append({
                "order_id": f"ORD_{order_id:04d}",
                "items": order_items,
                "distance": order_distance,
                "time": order_time,
                "path_analysis": order_analysis
            })
    
    # Calculate averages
    avg_distance = total_distance / completed_orders if completed_orders > 0 else 0
    avg_time = total_time / completed_orders if completed_orders > 0 else 0
    
    simulation_results = {
        "total_distance": total_distance,
        "total_time": total_time,
        "completed_orders": completed_orders,
        "average_distance": avg_distance,
        "average_time": avg_time,
        "picker_speed": {
            "label": picker_speed_label,
            "numeric_value": picker_speed_numeric
        },
        "order_details": order_details,
        "layout_metadata": layout_metadata,
        "simulation_timestamp": time.time()
    }
    
    return simulation_results

def run_realtime_order_simulation(layout_data, num_orders=50, items_per_order=5):
    """
    Run a real-time order simulation that progresses over time.
    
    Args:
        layout_data: List of layout cells with coordinates and types
        num_orders: Number of orders to simulate
        items_per_order: Number of items per order
        
    Returns:
        dict: Current simulation state with progressive results
    """
    # Check if simulation is running
    if not st.session_state.get('simulation_running', False):
        # Return empty results if simulation is not running
        return {
            "total_distance": 0,
            "total_time": 0,
            "completed_orders": 0,
            "average_distance": 0,
            "average_time": 0,
            "picker_speed": {
                "label": st.session_state.get('picker_speed', 'Medium'),
                "numeric_value": get_picker_speed(st.session_state.get('picker_speed', 'Medium'))
            },
            "order_details": [],
            "layout_metadata": extract_layout_metadata(layout_data),
            "simulation_timestamp": time.time(),
            "simulation_progress": {
                "total_orders": num_orders,
                "remaining_orders": num_orders,
                "elapsed_time": 0
            }
        }
    
    # Extract layout metadata
    layout_metadata = extract_layout_metadata(layout_data)
    
    # Get picker speed
    picker_speed_label = st.session_state.get('picker_speed', 'Medium')
    picker_speed_numeric = get_picker_speed(picker_speed_label)
    
    # Get shelf positions for order generation
    shelf_positions = layout_metadata["shelves"]
    
    # Initialize or get current simulation state
    if 'realtime_simulation_state' not in st.session_state:
        st.session_state.realtime_simulation_state = {
            "total_distance": 0,
            "total_time": 0,
            "completed_orders": 0,
            "current_order_index": 0,
            "order_queue": [],
            "simulation_start_time": time.time(),
            "last_update_time": time.time()
        }
        # Pre-generate all orders
        for order_id in range(num_orders):
            if shelf_positions:
                order_items = random.sample(shelf_positions, min(items_per_order, len(shelf_positions)))
            else:
                order_items = []
            if order_items:
                order_analysis = calculate_order_distance(order_items, layout_metadata)
                order_distance = order_analysis["total_distance"]
                order_time = order_distance / picker_speed_numeric if picker_speed_numeric > 0 else 0
                st.session_state.realtime_simulation_state["order_queue"].append({
                    "order_id": f"ORD_{order_id:04d}",
                    "items": order_items,
                    "distance": order_distance,
                    "time": order_time,
                    "path_analysis": order_analysis
                })
        # Debug: Show order queue generation
        st.session_state['debug_order_queue_generated'] = len(st.session_state.realtime_simulation_state["order_queue"])
    # Do NOT reset state just because simulation_running is False
    
    # Get current state
    state = st.session_state.realtime_simulation_state
    current_time = time.time()

    # Process all remaining orders immediately (no 1 second rule)
    while state["current_order_index"] < len(state["order_queue"]):
        current_order = state["order_queue"][state["current_order_index"]]
        state["total_distance"] += current_order["distance"]
        state["total_time"] += current_order["time"]
        state["completed_orders"] += 1
        state["current_order_index"] += 1
        state["last_update_time"] = current_time
        st.session_state['last_simulation_update'] = current_time

    # Calculate current averages
    avg_distance = state["total_distance"] / state["completed_orders"] if state["completed_orders"] > 0 else 0
    avg_time = state["total_time"] / state["completed_orders"] if state["completed_orders"] > 0 else 0
    
    # Return current simulation state
    simulation_results = {
        "total_distance": state["total_distance"],
        "total_time": state["total_time"],
        "completed_orders": state["completed_orders"],
        "average_distance": avg_distance,
        "average_time": avg_time,
        "picker_speed": {
            "label": picker_speed_label,
            "numeric_value": picker_speed_numeric
        },
        "order_details": state["order_queue"][:state["completed_orders"]],  # Only completed orders
        "layout_metadata": layout_metadata,
        "simulation_timestamp": current_time,
        "simulation_progress": {
            "total_orders": num_orders,
            "remaining_orders": num_orders - state["completed_orders"],
            "elapsed_time": current_time - state["simulation_start_time"]
        }
    }
    
    return simulation_results

def create_grid_layout(grid_width, grid_height):
    layout_data = []
    for i in range(grid_height):
        for j in range(grid_width):
            cell_type = "Empty"
            color = "white"
            symbol = "square"
            if (i + j) % 3 == 0 and 0 < i < grid_height-1 and 0 < j < grid_width-1:
                cell_type = "Shelf"
                color = "brown"
                symbol = "square"
            elif i == 0 and j in [2, grid_width-3]:
                cell_type = "Packing Station"
                color = "green"
                symbol = "diamond"
            elif i == grid_height-1 and j == grid_width//2:
                cell_type = "Entry/Exit"
                color = "blue"
                symbol = "circle"
            layout_data.append({
                'x': j, 'y': i, 'type': cell_type, 'color': color, 'symbol': symbol
            })
    return layout_data

def create_l_shape_layout(grid_width, grid_height):
    layout_data = []
    for i in range(grid_height):
        for j in range(grid_width):
            cell_type = "Empty"
            color = "white"
            symbol = "square"
            
            if j == 1 and 1 <= i < grid_height-1:
                cell_type = "Shelf"
                color = "brown"
                symbol = "square"
            
            elif i == grid_height-2 and 1 <= j < grid_width-2:
                cell_type = "Shelf"
                color = "brown"
                symbol = "square"
            elif i == 0 and j == 1:
                cell_type = "Packing Station"
                color = "green"
                symbol = "diamond"
            elif i == grid_height-1 and j == grid_width-2:
                cell_type = "Entry/Exit"
                color = "blue"
                symbol = "circle"
            layout_data.append({
                'x': j, 'y': i, 'type': cell_type, 'color': color, 'symbol': symbol
            })
    return layout_data

def create_u_shape_layout(grid_width, grid_height):
    layout_data = []
    for i in range(grid_height):
        for j in range(grid_width):
            cell_type = "Empty"
            color = "white"
            symbol = "square"
            
            if j == 1 and 1 <= i < grid_height-1:
                cell_type = "Shelf"
                color = "brown"
                symbol = "square"
            
            elif j == grid_width-2 and 1 <= i < grid_height-1:
                cell_type = "Shelf"
                color = "brown"
                symbol = "square"
            
            elif i == grid_height-2 and 1 < j < grid_width-2:
                cell_type = "Shelf"
                color = "brown"
                symbol = "square"
            elif i == 0 and j == grid_width//2:
                cell_type = "Packing Station"
                color = "green"
                symbol = "diamond"
            elif i == grid_height-1 and j == grid_width//2:
                cell_type = "Entry/Exit"
                color = "blue"
                symbol = "circle"
            layout_data.append({
                'x': j, 'y': i, 'type': cell_type, 'color': color, 'symbol': symbol
            })
    return layout_data

def create_custom_layout(uploaded_layout, grid_width, grid_height):
    # Check if we have a custom layout from the builder
    if 'layout_config' in st.session_state and st.session_state['layout_config']:
        layout_config = st.session_state['layout_config']
        if layout_config.get('layout_type') == 'Custom Layout':
            layout_data = []
            
            # Create empty grid
            for i in range(grid_height):
                for j in range(grid_width):
                    layout_data.append({
                        'x': j, 'y': i, 'type': "Empty", 'color': "white", 'symbol': "square"
                    })
            
            # Add shelves
            for shelf in layout_config.get('shelves', []):
                idx = shelf['y'] * grid_width + shelf['x']
                if 0 <= idx < len(layout_data):
                    layout_data[idx].update({'type': "Shelf", 'color': "brown", 'symbol': "square"})
            
            # Add packing stations
            for station in layout_config.get('stations', []):
                idx = station['y'] * grid_width + station['x']
                if 0 <= idx < len(layout_data):
                    layout_data[idx].update({'type': "Packing Station", 'color': "green", 'symbol': "diamond"})
            
            # Add entry/exit point
            for entry in layout_config.get('entry_exit', []):
                idx = entry['y'] * grid_width + entry['x']
                if 0 <= idx < len(layout_data):
                    layout_data[idx].update({'type': "Entry/Exit", 'color': "blue", 'symbol': "circle"})
            
            return layout_data
    
    # Fallback to uploaded JSON file
    if uploaded_layout is not None:
        try:
            layout_json = json.load(uploaded_layout)
            layout_data = []
            
            for i in range(grid_height):
                for j in range(grid_width):
                    layout_data.append({
                        'x': j, 'y': i, 'type': "Empty", 'color': "white", 'symbol': "square"
                    })
            
            for shelf in layout_json.get('shelves', []):
                idx = shelf['y'] * grid_width + shelf['x']
                if 0 <= idx < len(layout_data):
                    layout_data[idx].update({'type': "Shelf", 'color': "brown", 'symbol': "square"})
            
            for station in layout_json.get('stations', []):
                idx = station['y'] * grid_width + station['x']
                if 0 <= idx < len(layout_data):
                    layout_data[idx].update({'type': "Packing Station", 'color': "green", 'symbol': "diamond"})
            
            for entry in layout_json.get('entry_exit', []):
                idx = entry['y'] * grid_width + entry['x']
                if 0 <= idx < len(layout_data):
                    layout_data[idx].update({'type': "Entry/Exit", 'color': "blue", 'symbol': "circle"})
            return layout_data
        except Exception as e:
            st.warning(f"Invalid custom layout file: {e}")
    
    return create_grid_layout(grid_width, grid_height)

def warehouse_layout_section():
    import json
    import random
    import time
    
    # Remove all auto-refresh logic: do not inject any auto-refresh scripts or meta tags
    # (No code here for auto-refresh)

    st.markdown('<div class="section-title">Warehouse Layout Visualization</div>', unsafe_allow_html=True)
    # Ensure layout_data is assigned before visualization
    grid_width = st.session_state['grid_width']
    grid_height = st.session_state['grid_height']
    layout_type = st.session_state['layout_type']
    uploaded_layout = st.session_state.get('uploaded_layout', None)
    num_pickers = st.session_state.get('num_pickers', 3)

    if 'custom_layout_state' in st.session_state and st.session_state.custom_layout_state.get('grid_data'):
        layout_data = st.session_state.custom_layout_state['grid_data']
        if layout_type == "Sample Layouts":
            st.info(f"📦 Loaded Sample Layout: {st.session_state.custom_layout_state.get('layout_name', 'Unknown')}")
        elif layout_type == "Custom Layout":
            st.info(f"🛠️ Using Custom Layout Builder Grid")
    elif layout_type == "Grid Layout":
        layout_data = create_grid_layout(grid_width, grid_height)
    elif layout_type == "L-Shape Layout":
        layout_data = create_l_shape_layout(grid_width, grid_height)
    elif layout_type == "U-Shape Layout":
        layout_data = create_u_shape_layout(grid_width, grid_height)
    elif layout_type == "Custom Layout":
        layout_data = create_custom_layout(uploaded_layout, grid_width, grid_height)
    else:
        layout_data = create_grid_layout(grid_width, grid_height)

    # --- Warehouse Layout Grid Visualization (moved up) ---
    df_layout = pd.DataFrame(layout_data)
    grid_height = st.session_state['grid_height']
    df_layout['y_flipped'] = grid_height - 1 - df_layout['y']
    fig_layout = go.Figure()
    for element_type in df_layout['type'].unique():
        element_data = df_layout[df_layout['type'] == element_type]
        first_color = list(element_data['color'])[0] if 'color' in element_data else 'white'
        first_symbol = list(element_data['symbol'])[0] if 'symbol' in element_data else 'square'
        fig_layout.add_trace(go.Scatter(
            x=element_data['x'],
            y=element_data['y_flipped'],
            mode='markers',
            marker=dict(
                size=20,
                color=first_color,
                symbol=first_symbol,
                line=dict(width=2, color='black')
            ),
            name=element_type,
            hovertemplate=f"<b>{element_type}</b><br>Position: (%{{x}}, %{{y}})<extra></extra>"
        ))
    shelf_elements = df_layout[df_layout['type'] == 'Shelf']
    if not shelf_elements.empty:
        if 'shelf_type' in shelf_elements.columns:
            shelf_text = shelf_elements['shelf_type'].tolist()
        else:
            shelf_text = [''] * len(shelf_elements)
        shelf_text = [str(t).lower() if t and t != 'nan' else '' for t in shelf_text]
        fig_layout.add_trace(go.Scatter(
            x=shelf_elements['x'].tolist(),
            y=shelf_elements['y_flipped'].tolist(),
            mode='text',
            text=list(shelf_text),
            textfont=dict(color='white', size=12, family='Arial'),
            textposition='middle center',
            showlegend=False,
            hoverinfo='skip'
        ))
    fig_layout.update_layout(
        title="Current Warehouse Layout",
        xaxis_title="X Position",
        yaxis_title="Y Position",
        width=800,
        height=500,
        showlegend=True,
        plot_bgcolor='lightgray',
        xaxis=dict(showgrid=True, gridcolor='white'),
        yaxis=dict(showgrid=True, gridcolor='white')
    )
    st.plotly_chart(fig_layout, use_container_width=True)
    # --- End Warehouse Layout Grid Visualization ---
    # Extract layout metadata and store in session state
    layout_metadata = extract_layout_metadata(layout_data)
    st.session_state['layout_metadata'] = layout_metadata

    # Picker functionality removed from main warehouse layout

    # Calculate distances between layout elements
    distances = calculate_distances(layout_metadata)
    
    # Get picker speed information
    picker_speed_label = st.session_state.get('picker_speed', 'Medium')
    picker_speed_numeric = get_picker_speed(picker_speed_label)
    
    # Calculate sample order distance (using first few shelves as example)
    sample_order_items = layout_metadata["shelves"][:3] if layout_metadata["shelves"] else []
    sample_order_distance = calculate_order_distance(sample_order_items, layout_metadata)
    
    # Run real-time order simulation using current warehouse layout
    num_orders = st.session_state.get('num_orders', 50)
    items_per_order = st.session_state.get('items_per_order', 5)
    
    simulation_results = run_realtime_order_simulation(layout_data, num_orders, items_per_order)
    
    # Store simulation results in session state for global access
    st.session_state['order_simulation_results'] = simulation_results
    
    # Auto-refresh when simulation is running
    if st.session_state.get('simulation_running', False):
        progress_info = simulation_results.get('simulation_progress', {})
        total_orders = progress_info.get('total_orders', num_orders)
        completed_orders = simulation_results['completed_orders']
        
        if completed_orders < total_orders:
            # Auto-refresh every 1 second using JavaScript
            st.markdown("🔄 **Simulation is running! Auto-updating every second...**")
            
            # Track last refresh time to prevent multiple refreshes
            current_time = time.time()
            last_refresh = st.session_state.get('last_auto_refresh', 0)
            
            if current_time - last_refresh >= 1.0:
                st.session_state.last_auto_refresh = current_time
                
                # Create auto-refresh using JavaScript
                auto_refresh_script = f"""
                <script>
                // Auto-refresh every 1 second when simulation is running
                setTimeout(function() {{
                    window.location.reload();
                }}, 1000);
                </script>
                """
                st.markdown(auto_refresh_script, unsafe_allow_html=True)
        elif completed_orders >= total_orders:
            # Explicitly override any previous auto-refresh after completion
            st.markdown("""<script>// No auto-refresh after completion</script>""", unsafe_allow_html=True)
    
    # Combine layout metadata with distance calculations, picker speed, and sample order
    complete_metadata = {
        "layout_coordinates": layout_metadata,
        "distance_calculations": distances,
        "picker_speed": {
            "label": picker_speed_label,
            "numeric_value": picker_speed_numeric
        },
        "sample_order_analysis": {
            "order_items": sample_order_items,
            "path_analysis": sample_order_distance
        },
        "order_simulation_results": {
            "total_distance": simulation_results["total_distance"],
            "total_time": simulation_results["total_time"],
            "completed_orders": simulation_results["completed_orders"],
            "average_distance": simulation_results["average_distance"],
            "average_time": simulation_results["average_time"],
            "picker_speed_used": simulation_results["picker_speed"],
            "simulation_parameters": {
                "num_orders": num_orders,
                "items_per_order": items_per_order
            },
            "order_details": simulation_results["order_details"][:5]  # Include first 5 orders for reference
        },
        "efficient_path_algorithm": {
            "description": "Most Efficient Path Calculation Algorithm",
            "methodology": "The algorithm calculates the optimal path through the warehouse using the following steps:",
            "steps": [
                "1. Identify the nearest entry point to the first item in the order",
                "2. Calculate Manhattan distances between consecutive items in the order sequence",
                "3. Identify the nearest packing station to the last item in the order",
                "4. Sum all path segments: Entry → Item1 → Item2 → ... → ItemN → Packing Station",
                "5. Return the total distance and complete path sequence"
            ],
            "distance_metric": "Manhattan Distance (|x1-x2| + |y1-y2|)",
            "optimization_criteria": [
                "Minimize entry point distance to first item",
                "Minimize distance between consecutive items",
                "Minimize distance from last item to packing station",
                "Use grid-based movement (horizontal and vertical only)"
            ],
            "path_structure": "Entry Point → Item1 → Item2 → ... → ItemN → Packing Station",
            "total_distance_formula": "Entry Distance + Sum(Inter-item Distances) + Packing Distance"
        }
    }

    # Display simulation results
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Real-Time Order Simulation Results</div>", unsafe_allow_html=True)
    
    # Remove all metrics, progress bar, simulation status, and debug info from below the warehouse layout grid
    # Only keep the download button for layout metadata
    metadata_json = json.dumps(complete_metadata, indent=2)
    st.download_button(
        label="⬇️ Download Layout Metadata with Simulation Results (JSON)",
        data=metadata_json,
        file_name="layout_metadata_with_simulation.json",
        mime="application/json"
    )