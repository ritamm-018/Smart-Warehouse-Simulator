#!/usr/bin/env python3
"""
Test script to demonstrate layout metadata extraction functionality.
"""

def create_grid_layout(grid_width, grid_height):
    """Create a grid layout for testing."""
    layout_data = []
    for i in range(grid_height):
        for j in range(grid_width):
            cell_type = "Empty"
            if (i + j) % 3 == 0 and 0 < i < grid_height-1 and 0 < j < grid_width-1:
                cell_type = "Shelf"
            elif i == 0 and j in [2, grid_width-3]:
                cell_type = "Packing Station"
            elif i == grid_height-1 and j == grid_width//2:
                cell_type = "Entry/Exit"
            layout_data.append({
                'x': j, 'y': i, 'type': cell_type
            })
    return layout_data

def create_l_shape_layout(grid_width, grid_height):
    """Create an L-shape layout for testing."""
    layout_data = []
    for i in range(grid_height):
        for j in range(grid_width):
            cell_type = "Empty"
            if j == 1 and 1 <= i < grid_height-1:
                cell_type = "Shelf"
            elif i == grid_height-2 and 1 <= j < grid_width-2:
                cell_type = "Shelf"
            elif i == 0 and j == 1:
                cell_type = "Packing Station"
            elif i == grid_height-1 and j == grid_width-2:
                cell_type = "Entry/Exit"
            layout_data.append({
                'x': j, 'y': i, 'type': cell_type
            })
    return layout_data

def create_u_shape_layout(grid_width, grid_height):
    """Create a U-shape layout for testing."""
    layout_data = []
    for i in range(grid_height):
        for j in range(grid_width):
            cell_type = "Empty"
            if j == 1 and 1 <= i < grid_height-1:
                cell_type = "Shelf"
            elif j == grid_width-2 and 1 <= i < grid_height-1:
                cell_type = "Shelf"
            elif i == grid_height-2 and 1 < j < grid_width-2:
                cell_type = "Shelf"
            elif i == 0 and j == grid_width//2:
                cell_type = "Packing Station"
            elif i == grid_height-1 and j == grid_width//2:
                cell_type = "Entry/Exit"
            layout_data.append({
                'x': j, 'y': i, 'type': cell_type
            })
    return layout_data

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

def test_layout_metadata_extraction():
    """Test the layout metadata extraction with different layout types."""
    
    print("🧪 Testing Layout Metadata Extraction")
    print("=" * 50)
    
    # Test Grid Layout
    print("\n📦 Grid Layout (12x8):")
    grid_layout = create_grid_layout(12, 8)
    grid_metadata = extract_layout_metadata(grid_layout)
    print(f"Shelves: {grid_metadata['shelves']}")
    print(f"Packing Stations: {grid_metadata['packing_stations']}")
    print(f"Entry Points: {grid_metadata['entry_points']}")
    
    # Test L-Shape Layout
    print("\n📦 L-Shape Layout (12x8):")
    l_shape_layout = create_l_shape_layout(12, 8)
    l_shape_metadata = extract_layout_metadata(l_shape_layout)
    print(f"Shelves: {l_shape_metadata['shelves']}")
    print(f"Packing Stations: {l_shape_metadata['packing_stations']}")
    print(f"Entry Points: {l_shape_metadata['entry_points']}")
    
    # Test U-Shape Layout
    print("\n📦 U-Shape Layout (12x8):")
    u_shape_layout = create_u_shape_layout(12, 8)
    u_shape_metadata = extract_layout_metadata(u_shape_layout)
    print(f"Shelves: {u_shape_metadata['shelves']}")
    print(f"Packing Stations: {u_shape_metadata['packing_stations']}")
    print(f"Entry Points: {u_shape_metadata['entry_points']}")
    
    print("\n✅ Layout metadata extraction test completed!")

if __name__ == "__main__":
    test_layout_metadata_extraction() 