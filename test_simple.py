#!/usr/bin/env python3
"""
Very simple test to understand the reachability issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.advanced_layout_optimizer import AdvancedLayoutOptimizer, Position, Shelf

def test_simple_reachability():
    """Test reachability with just one shelf next to entry point"""
    print("🧪 Testing Simple Reachability...")
    
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
    
    # Set entry points
    optimizer.entry_points = [Position(0, 3)]
    
    # Place one shelf right next to entry point
    shelf_pos = Position(1, 3)  # Right next to entry at (0, 3)
    shelf = Shelf(position=shelf_pos, category='a')
    optimizer.shelves.append(shelf)
    
    # Place one packing station
    station_pos = Position(5, 3)  # Right edge, same row
    optimizer.packing_stations.append(station_pos)
    
    print(f"📊 Entry point: {optimizer.entry_points[0].to_list()}")
    print(f"📊 Shelf position: {shelf_pos.to_list()}")
    print(f"📊 Packing station: {station_pos.to_list()}")
    
    # Test reachability
    entry_to_shelf = optimizer.is_reachable(optimizer.entry_points[0], shelf_pos)
    shelf_to_station = optimizer.is_reachable(shelf_pos, station_pos)
    
    print(f"📊 Entry to shelf reachable: {entry_to_shelf}")
    print(f"📊 Shelf to station reachable: {shelf_to_station}")
    
    # Debug: Check if positions are occupied
    print(f"📊 Entry occupied: {optimizer.is_position_occupied(optimizer.entry_points[0])}")
    print(f"📊 Shelf occupied: {optimizer.is_position_occupied(shelf_pos)}")
    print(f"📊 Station occupied: {optimizer.is_position_occupied(station_pos)}")
    
    # Debug: Check neighbors of entry point
    entry_neighbors = optimizer.get_neighbors(optimizer.entry_points[0])
    print(f"📊 Entry neighbors: {[pos.to_list() for pos in entry_neighbors]}")
    
    # Debug: Check if shelf position is in entry neighbors
    shelf_in_neighbors = shelf_pos in entry_neighbors
    print(f"📊 Shelf in entry neighbors: {shelf_in_neighbors}")
    
    # Debug: Test A* with empty grid
    print("\n🔍 Testing A* with empty grid...")
    optimizer.shelves = []
    optimizer.packing_stations = []
    empty_reachable = optimizer.is_reachable(optimizer.entry_points[0], shelf_pos)
    print(f"📊 Empty grid reachable: {empty_reachable}")
    
    # Restore shelf and station
    optimizer.shelves.append(shelf)
    optimizer.packing_stations.append(station_pos)
    
    # Validate layout
    validation = optimizer.validate_layout()
    print(f"📊 Layout valid: {validation['valid']}")
    print(f"📊 Issues: {validation['issues']}")
    
    return validation['valid']

if __name__ == "__main__":
    success = test_simple_reachability()
    print(f"\n🎉 Test {'passed' if success else 'failed'}!")
    sys.exit(0 if success else 1) 