#!/usr/bin/env python3
"""
Debug script to understand layout generation issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.advanced_layout_optimizer import AdvancedLayoutOptimizer, Position, Shelf

def debug_layout_generation():
    """Debug the layout generation process"""
    print("🔍 Debugging Layout Generation...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=10, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    print(f"📊 Grid size: {optimizer.rows}x{optimizer.columns}")
    print(f"📊 Target shelves: {optimizer.num_shelves}")
    print(f"📊 Target packing stations: {optimizer.num_packing_stations}")
    print(f"📊 Entry points: {[pos.to_list() for pos in optimizer.entry_points]}")
    
    # Test finding valid positions
    print("\n🔍 Testing valid position finding...")
    
    valid_shelf_positions = optimizer.find_valid_shelf_positions()
    print(f"📊 Valid shelf positions found: {len(valid_shelf_positions)}")
    
    valid_station_positions = optimizer.find_valid_packing_station_positions()
    print(f"📊 Valid packing station positions found: {len(valid_station_positions)}")
    
    if len(valid_shelf_positions) < optimizer.num_shelves:
        print(f"❌ Not enough valid shelf positions! Need {optimizer.num_shelves}, found {len(valid_shelf_positions)}")
        
        # Show some valid positions
        print("📊 Sample valid shelf positions:")
        for i, pos in enumerate(valid_shelf_positions[:10]):
            print(f"  {i+1}. ({pos.x}, {pos.y})")
    
    if len(valid_station_positions) < optimizer.num_packing_stations:
        print(f"❌ Not enough valid packing station positions! Need {optimizer.num_packing_stations}, found {len(valid_station_positions)}")
    
    # Test aisle spacing
    print("\n🔍 Testing aisle spacing...")
    aisle_violations = 0
    for pos in valid_shelf_positions:
        if optimizer.is_aisle_position(pos):
            aisle_violations += 1
            print(f"❌ Position ({pos.x}, {pos.y}) is in aisle but marked as valid")
    
    print(f"📊 Aisle violations in valid positions: {aisle_violations}")
    
    # Test a simple layout generation
    print("\n🔍 Testing simple layout generation...")
    
    # Clear current layout
    optimizer.shelves = []
    optimizer.packing_stations = []
    optimizer.drop_zones = []
    optimizer.robots = []
    
    # Try to place packing stations
    if len(valid_station_positions) >= optimizer.num_packing_stations:
        selected_stations = valid_station_positions[:optimizer.num_packing_stations]
        optimizer.packing_stations = selected_stations
        print(f"✅ Placed {len(selected_stations)} packing stations")
        
        # Try to place shelves
        if len(valid_shelf_positions) >= optimizer.num_shelves:
            selected_positions = valid_shelf_positions[:optimizer.num_shelves]
            
            # Assign categories
            for i, pos in enumerate(selected_positions):
                category = optimizer.categories[i % len(optimizer.categories)]
                shelf = Shelf(position=pos, category=category)
                optimizer.shelves.append(shelf)
            
            print(f"✅ Placed {len(optimizer.shelves)} shelves")
            
            # Test validation
            validation = optimizer.validate_layout()
            print(f"📊 Layout valid: {validation['valid']}")
            print(f"📊 Quality score: {validation['quality_score']}")
            print(f"📊 Issues: {validation['issues']}")
            print(f"📊 Warnings: {validation['warnings']}")
            
            if not validation['valid']:
                print("❌ Layout validation failed!")
                return False
            else:
                print("✅ Layout generation successful!")
                return True
        else:
            print("❌ Not enough valid shelf positions")
            return False
    else:
        print("❌ Not enough valid packing station positions")
        return False

def test_smaller_grid():
    """Test with a smaller grid to see if the issue is grid size"""
    print("\n🔍 Testing with smaller grid...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=8, 
        columns=8, 
        num_shelves=6, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    valid_shelf_positions = optimizer.find_valid_shelf_positions()
    valid_station_positions = optimizer.find_valid_packing_station_positions()
    
    print(f"📊 8x8 grid - Valid shelf positions: {len(valid_shelf_positions)}")
    print(f"📊 8x8 grid - Valid station positions: {len(valid_station_positions)}")
    
    if len(valid_shelf_positions) >= optimizer.num_shelves and len(valid_station_positions) >= optimizer.num_packing_stations:
        print("✅ Smaller grid has enough positions")
        return True
    else:
        print("❌ Smaller grid also has insufficient positions")
        return False

def test_reachability_simple():
    """Test simple reachability between two points"""
    print("\n🔍 Testing Simple Reachability...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=8, 
        columns=8, 
        num_shelves=4, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    # Test reachability between two empty positions
    start = Position(0, 4)  # Entry point
    goal = Position(2, 4)   # A position 2 steps away
    
    print(f"📊 Testing reachability from {start.to_list()} to {goal.to_list()}")
    
    # Should be reachable since no obstacles
    reachable = optimizer.is_reachable(start, goal)
    print(f"📊 Reachable: {reachable}")
    
    if reachable:
        print("✅ Simple reachability test passed")
        return True
    else:
        print("❌ Simple reachability test failed")
        return False

def test_fallback_layout_debug():
    """Test the fallback layout specifically to see what's wrong"""
    print("\n🔍 Testing Fallback Layout Debug...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=10, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    result = optimizer.create_fallback_layout()
    
    print(f"📊 Fallback success: {result['success']}")
    if result['success']:
        validation = result['validation']
        print(f"📊 Fallback layout valid: {validation['valid']}")
        print(f"📊 Quality score: {validation['quality_score']}")
        print(f"📊 Issues: {validation['issues']}")
        print(f"📊 Warnings: {validation['warnings']}")
        print(f"📊 Unreachable shelves: {validation['unreachable_shelves']}")
        print(f"📊 Unreachable stations: {validation['unreachable_stations']}")
        print(f"📊 Aisle violations: {validation['aisle_violations']}")
        
        # Show the layout structure
        layout = result['layout']
        print(f"📊 Shelves placed: {len(layout['shelves'])}")
        print(f"📊 Packing stations: {layout['packing_stations']}")
        print(f"📊 Entry points: {[pos.to_list() for pos in optimizer.entry_points]}")
        
        # Test reachability manually for first few shelves
        print("\n🔍 Testing reachability manually...")
        for i, shelf in enumerate(layout['shelves'][:3]):
            shelf_pos = Position(shelf['position'][0], shelf['position'][1])
            reachable = False
            for entry in optimizer.entry_points:
                if optimizer.is_reachable(entry, shelf_pos):
                    reachable = True
                    break
            print(f"📊 Shelf {i+1} at {shelf['position']}: reachable = {reachable}")
        
        return validation['valid']
    else:
        print(f"❌ Fallback creation failed: {result['message']}")
        return False

def test_simple_pathfinding():
    """Test pathfinding with a very simple layout"""
    print("\n🔍 Testing Simple Pathfinding...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=8, 
        columns=8, 
        num_shelves=1, 
        num_packing_stations=1, 
        num_robots=1
    )
    
    # Clear everything
    optimizer.shelves = []
    optimizer.packing_stations = []
    optimizer.drop_zones = []
    optimizer.robots = []
    
    # Place one shelf at a simple position
    shelf = Shelf(position=Position(2, 2), category='a')
    optimizer.shelves.append(shelf)
    
    # Place one packing station
    optimizer.packing_stations.append(Position(6, 2))
    
    # Test reachability
    entry = optimizer.entry_points[0]
    shelf_pos = shelf.position
    
    print(f"📊 Entry point: {entry.to_list()}")
    print(f"📊 Shelf position: {shelf_pos.to_list()}")
    print(f"📊 Packing station: {optimizer.packing_stations[0].to_list()}")
    
    # Test reachability from entry to shelf
    reachable = optimizer.is_reachable(entry, shelf_pos)
    print(f"📊 Entry to shelf reachable: {reachable}")
    
    # Test reachability from shelf to packing station
    shelf_to_station = optimizer.is_reachable(shelf_pos, optimizer.packing_stations[0])
    print(f"📊 Shelf to station reachable: {shelf_to_station}")
    
    # Validate the layout
    validation = optimizer.validate_layout()
    print(f"📊 Layout valid: {validation['valid']}")
    print(f"📊 Issues: {validation['issues']}")
    
    return validation['valid']

def test_astar_debug():
    """Test A* algorithm with a completely empty grid"""
    print("\n🔍 Testing A* Algorithm Debug...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=5, 
        columns=5, 
        num_shelves=0, 
        num_packing_stations=0, 
        num_robots=0
    )
    
    # Clear everything
    optimizer.shelves = []
    optimizer.packing_stations = []
    optimizer.drop_zones = []
    optimizer.robots = []
    
    # Test simple pathfinding
    start = Position(0, 2)  # Entry point
    goal = Position(2, 2)   # Goal position
    
    print(f"📊 Start: {start.to_list()}")
    print(f"📊 Goal: {goal.to_list()}")
    print(f"📊 Grid size: {optimizer.rows}x{optimizer.columns}")
    
    # Test if positions are valid
    print(f"📊 Start valid: {optimizer.is_valid_position(start)}")
    print(f"📊 Goal valid: {optimizer.is_valid_position(goal)}")
    
    # Test if positions are occupied
    print(f"📊 Start occupied: {optimizer.is_position_occupied(start)}")
    print(f"📊 Goal occupied: {optimizer.is_position_occupied(goal)}")
    
    # Test neighbors
    neighbors = optimizer.get_neighbors(start)
    print(f"📊 Start neighbors: {[pos.to_list() for pos in neighbors]}")
    
    # Test reachability
    reachable = optimizer.is_reachable(start, goal)
    print(f"📊 Reachable: {reachable}")
    
    # Test Manhattan distance
    distance = optimizer.get_manhattan_distance(start, goal)
    print(f"📊 Manhattan distance: {distance}")
    
    return reachable

def main():
    """Run debug tests"""
    print("🚀 Starting Layout Generation Debug")
    print("=" * 50)
    
    success1 = debug_layout_generation()
    success2 = test_smaller_grid()
    success3 = test_reachability_simple()
    success4 = test_fallback_layout_debug()
    success5 = test_simple_pathfinding()
    success6 = test_astar_debug()
    
    if success1 or success2 or success3 or success4 or success5 or success6:
        print("\n✅ Debug completed - found the issue!")
    else:
        print("\n❌ Debug completed - need to investigate further")

if __name__ == "__main__":
    main() 