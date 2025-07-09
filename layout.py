import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

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
    st.subheader(" Warehouse Layout Visualization")
    grid_width = st.session_state['grid_width']
    grid_height = st.session_state['grid_height']
    layout_type = st.session_state['layout_type']
    uploaded_layout = st.session_state.get('uploaded_layout', None)

    if layout_type == "Grid Layout":
        layout_data = create_grid_layout(grid_width, grid_height)
    elif layout_type == "L-Shape Layout":
        layout_data = create_l_shape_layout(grid_width, grid_height)
    elif layout_type == "U-Shape Layout":
        layout_data = create_u_shape_layout(grid_width, grid_height)
    elif layout_type == "Custom Layout":
        layout_data = create_custom_layout(uploaded_layout, grid_width, grid_height)
    else:
        layout_data = create_grid_layout(grid_width, grid_height)

    df_layout = pd.DataFrame(layout_data)
    fig_layout = go.Figure()
    for element_type in df_layout['type'].unique():
        element_data = df_layout[df_layout['type'] == element_type]
        fig_layout.add_trace(go.Scatter(
            x=element_data['x'],
            y=element_data['y'],
            mode='markers',
            marker=dict(
                size=20,
                color=element_data['color'].iloc[0],
                symbol=element_data['symbol'].iloc[0],
                line=dict(width=2, color='black')
            ),
            name=element_type,
            hovertemplate=f"<b>{element_type}</b><br>Position: (%{{x}}, %{{y}})<extra></extra>"
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