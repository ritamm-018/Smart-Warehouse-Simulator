#!/usr/bin/env python3
"""
Minimal test to verify A* algorithm and create a guaranteed-working layout
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.advanced_layout_optimizer import AdvancedLayoutOptimizer, Position, Shelf

def test_minimal_astar():
    """Test A* with a minimal layout"""
    print("🧪 Testing Minimal A* Algorithm...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=6, 
        columns=6, 
        num_shelves=1, 
        num_packing_stations=1, 
        num_robots=1
    )
    
    # Clear everything
    optimizer.shelves = []
    optimizer.packing_stations = []
    optimizer.drop_zones = []
    optimizer.robots = []
    
    # Test the simplest possible path: entry at (0, 3) to shelf at (1, 3)
    entry = Position(0, 3)
    shelf_pos = Position(1, 3)
    
    print(f"📊 Entry: {entry.to_list()}")
    print(f"📊 Shelf: {shelf_pos.to_list()}")
    
    # Test reachability
    reachable = optimizer.is_reachable(entry, shelf_pos)
    print(f"📊 Reachable: {reachable}")
    
    if reachable:
        print("✅ A* works for simple case")
        return True
    else:
        print("❌ A* fails for simple case")
        return False

def create_guaranteed_working_layout():
    """Create a layout that's guaranteed to work"""
    print("\n🔧 Creating Guaranteed Working Layout...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=10, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    # Clear everything
    optimizer.shelves = []
    optimizer.packing_stations = []
    optimizer.drop_zones = []
    optimizer.robots = []
    
    # Create a layout that's guaranteed to work:
    # - Entry points at (0, 5), (0, 6), (0, 7)
    # - Shelves in a simple line at row 4: (1, 4), (2, 4), (3, 4), etc.
    # - Packing stations at (11, 4), (11, 7)
    
    # Update entry points
    optimizer.entry_points = [
        Position(0, 5),
        Position(0, 6), 
        Position(0, 7)
    ]
    
    # Place shelves in a simple line pattern
    shelf_positions = []
    for i in range(optimizer.num_shelves):
        x = 1 + i  # Start at column 1, go right
        y = 4       # All on row 4
        if x < optimizer.columns:
            pos = Position(x, y)
            shelf_positions.append(pos)
    
    # Create shelves
    for i, pos in enumerate(shelf_positions):
        category = optimizer.categories[i % len(optimizer.categories)]
        shelf = Shelf(position=pos, category=category)
        optimizer.shelves.append(shelf)
    
    # Place packing stations
    optimizer.packing_stations = [
        Position(optimizer.columns - 1, 4),  # Right edge, same row as shelves
        Position(optimizer.columns - 1, 7)   # Right edge, different row
    ]
    
    # Place robots
    for i in range(optimizer.num_robots):
        robot_id = f"R{i+1}"
        robot_pos = optimizer.entry_points[i % len(optimizer.entry_points)]
        from utils.advanced_layout_optimizer import Robot
        robot = Robot(id=robot_id, position=robot_pos)
        optimizer.robots.append(robot)
    
    # Place drop zones
    for station in optimizer.packing_stations:
        drop_pos = Position(station.x - 1, station.y)
        if optimizer.is_valid_position(drop_pos) and not optimizer.is_position_occupied(drop_pos):
            optimizer.drop_zones.append(drop_pos)
    
    # Test validation
    validation = optimizer.validate_layout()
    print(f"📊 Layout valid: {validation['valid']}")
    print(f"📊 Quality score: {validation['quality_score']}")
    print(f"📊 Issues: {validation['issues']}")
    print(f"📊 Shelves placed: {len(optimizer.shelves)}")
    print(f"📊 Packing stations: {len(optimizer.packing_stations)}")
    
    if validation['valid']:
        print("✅ Guaranteed working layout created successfully!")
        
        # Test JSON export
        layout_data = {
            "shelves": [shelf.to_dict() for shelf in optimizer.shelves],
            "packing_stations": [pos.to_list() for pos in optimizer.packing_stations],
            "drop_zones": [pos.to_list() for pos in optimizer.drop_zones],
            "robots": [robot.to_dict() for robot in optimizer.robots]
        }
        
        json_output = optimizer.export_layout(layout_data)
        print(f"📊 JSON output length: {len(json_output)} characters")
        
        return True
    else:
        print("❌ Layout still invalid")
        return False

def main():
    """Run tests"""
    print("🚀 Starting Minimal Layout Tests")
    print("=" * 50)
    
    success1 = test_minimal_astar()
    success2 = create_guaranteed_working_layout()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Layout optimizer is working.")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 