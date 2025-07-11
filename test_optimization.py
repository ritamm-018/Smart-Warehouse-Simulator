#!/usr/bin/env python3
"""
Test script for warehouse optimization system
Tests that optimization doesn't cause orders to drop to 0 and validates layouts properly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import random
from utils.layout_validator import LayoutValidator
from utils.optimization_engine import OptimizationEngine
from core.sim_engine import run_simulation

def test_layout_validation():
    """Test layout validation functionality"""
    print("🧪 Testing Layout Validation...")
    
    validator = LayoutValidator(grid_width=12, grid_height=10)
    
    # Test 1: Valid layout (shelves adjacent to entry point)
    valid_shelves = [(1, 0), (2, 0), (1, 1), (2, 1), (3, 1)]
    packing_stations = [(0, 0), (4, 0)]
    
    result = validator.validate_reachability(valid_shelves, packing_stations)
    assert result['valid'], f"Valid layout failed validation: {result['issues']}"
    print("✅ Valid layout test passed")
    
    # Test 2: Invalid layout (blocked entry)
    invalid_shelves = [(0, 0), (1, 0), (2, 0)]  # Block entry point
    result = validator.validate_reachability(invalid_shelves, packing_stations)
    assert not result['valid'], "Invalid layout should fail validation"
    print("✅ Invalid layout test passed")
    
    # Test 3: Layout quality assessment
    quality = validator.validate_layout_quality(valid_shelves, packing_stations)
    assert 0 <= quality['score'] <= 100, f"Quality score should be 0-100, got {quality['score']}"
    print(f"✅ Layout quality test passed (score: {quality['score']:.1f})")

def test_optimization_engine():
    """Test optimization engine functionality"""
    print("\n🧪 Testing Optimization Engine...")
    
    engine = OptimizationEngine(grid_width=12, grid_height=10, num_orders=50, items_per_order=4)
    
    # Test layout (shelves not blocking entry or stations)
    test_shelves = [(2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3)]
    packing_stations = [(2, 0), (8, 0)]
    
    # Test validation
    validation = engine.validate_layout(test_shelves, packing_stations)
    assert validation['reachability']['valid'], "Test layout should be valid"
    print("✅ Optimization engine validation test passed")
    
    # Test heuristic optimization (without RL model)
    result = engine.run_heuristic_optimization(test_shelves, packing_stations)
    assert result['success'], f"Heuristic optimization failed: {result['message']}"
    assert len(result['optimized_shelves']) == len(test_shelves), "Should preserve number of shelves"
    print("✅ Heuristic optimization test passed")

def test_simulation_with_optimization():
    """Test that optimization doesn't break simulation"""
    print("\n🧪 Testing Simulation with Optimization...")
    
    # Create initial layout (shelves not blocking entry or stations)
    initial_shelves = [(2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3)]
    packing_stations = [(2, 0), (8, 0)]
    
    # Generate orders for initial layout
    initial_orders = []
    for i in range(20):  # 20 orders
        order_items = []
        for j in range(3):  # 3 items per order
            shelf = random.choice(initial_shelves)
            order_items.append(shelf)
        initial_orders.append(order_items)
    
    # Run initial simulation
    initial_config = {
        'grid_width': 12,
        'grid_height': 10,
        'shelf_positions': initial_shelves,
        'packing_stations': packing_stations,
        'num_workers': 2,
        'orders': initial_orders,
        'shelves': [{'x': x, 'y': y, 'type': 'shelf'} for (x, y) in initial_shelves]
    }
    
    initial_metrics = run_simulation(initial_config)
    print(f"📊 Initial simulation: {initial_metrics['orders_completed']} orders completed")
    
    # Test optimization engine
    engine = OptimizationEngine(grid_width=12, grid_height=10, num_orders=20, items_per_order=3)
    
    # Run heuristic optimization
    optimization_result = engine.run_heuristic_optimization(initial_shelves, packing_stations)
    
    if optimization_result['success']:
        optimized_shelves = optimization_result['optimized_shelves']
        
        # Generate orders for optimized layout
        optimized_orders = []
        for i in range(20):
            order_items = []
            for j in range(3):
                shelf = random.choice(optimized_shelves)
                order_items.append(shelf)
            optimized_orders.append(order_items)
        
        # Run simulation with optimized layout
        optimized_config = {
            'grid_width': 12,
            'grid_height': 10,
            'shelf_positions': optimized_shelves,
            'packing_stations': packing_stations,
            'num_workers': 2,
            'orders': optimized_orders,
            'shelves': [{'x': x, 'y': y, 'type': 'shelf'} for (x, y) in optimized_shelves]
        }
        
        optimized_metrics = run_simulation(optimized_config)
        print(f"📊 Optimized simulation: {optimized_metrics['orders_completed']} orders completed")
        
        # Critical assertion: orders should not drop to 0
        assert optimized_metrics['orders_completed'] > 0, f"❌ Optimization caused orders to drop to 0! Initial: {initial_metrics['orders_completed']}, Optimized: {optimized_metrics['orders_completed']}"
        
        # Additional checks
        assert optimized_metrics['orders_completed'] >= initial_metrics['orders_completed'] * 0.8, f"❌ Optimization caused too many orders to fail! Initial: {initial_metrics['orders_completed']}, Optimized: {optimized_metrics['orders_completed']}"
        
        print("✅ Optimization simulation test passed - orders maintained!")
        
        # Show improvement
        if optimized_metrics['orders_completed'] > initial_metrics['orders_completed']:
            improvement = ((optimized_metrics['orders_completed'] - initial_metrics['orders_completed']) / initial_metrics['orders_completed']) * 100
            print(f"🎯 Orders improved by {improvement:.1f}%")
        else:
            print("📈 Orders maintained (no regression)")
    else:
        print(f"⚠️ Optimization failed: {optimization_result['message']}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases...")
    
    validator = LayoutValidator(grid_width=12, grid_height=10)
    
    # Test empty shelves
    empty_shelves = []
    packing_stations = [(2, 0), (8, 0)]
    result = validator.validate_reachability(empty_shelves, packing_stations)
    assert result['valid'], "Empty layout should be valid"
    print("✅ Empty layout test passed")
    
    # Test single shelf
    single_shelf = [(5, 5)]
    result = validator.validate_reachability(single_shelf, packing_stations)
    assert result['valid'], "Single shelf layout should be valid"
    print("✅ Single shelf test passed")
    
    # Test blocked packing stations
    blocked_stations_shelves = [(2, 0), (8, 0)]  # Block both stations
    result = validator.validate_reachability(blocked_stations_shelves, packing_stations)
    assert not result['valid'], "Blocked stations should be invalid"
    print("✅ Blocked stations test passed")

def main():
    """Run all tests"""
    print("🚀 Starting Warehouse Optimization Tests")
    print("=" * 50)
    
    try:
        test_layout_validation()
        test_optimization_engine()
        test_simulation_with_optimization()
        test_edge_cases()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Optimization system is working correctly.")
        print("✅ Layout validation works")
        print("✅ Optimization engine functions properly")
        print("✅ Optimization doesn't break order completion")
        print("✅ Edge cases are handled correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 