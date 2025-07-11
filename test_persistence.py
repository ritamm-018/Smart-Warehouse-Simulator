#!/usr/bin/env python3
"""
Test script for the data persistence system
"""

import sqlite3
import pandas as pd
from datetime import datetime
from data_persistence import WarehouseDataPersistence

def test_data_persistence():
    """Test the data persistence system"""
    print("🧪 Testing Data Persistence System...")
    
    # Initialize persistence
    persistence = WarehouseDataPersistence("test_warehouse_data.db")
    
    # Test 1: Save a sample layout
    print("\n1. Testing layout saving...")
    sample_layout = {
        'layout_name': 'Test Layout',
        'layout_type': 'Grid',
        'grid_width': 12,
        'grid_height': 10,
        'grid_data': [
            {'x': 3, 'y': 3, 'type': 'Shelf'},
            {'x': 5, 'y': 3, 'type': 'Shelf'},
            {'x': 2, 'y': 0, 'type': 'Packing Station'},
            {'x': 8, 'y': 0, 'type': 'Packing Station'}
        ]
    }
    
    layout_id = persistence.save_warehouse_layout(sample_layout)
    print(f"✅ Layout saved with ID: {layout_id}")
    
    # Test 2: Start a simulation run
    print("\n2. Testing simulation run...")
    run_config = {
        'run_name': 'Test Simulation',
        'num_pickers': 3,
        'num_orders': 50,
        'items_per_order': 3,
        'simulation_speed': 'Normal'
    }
    
    run_id = persistence.start_simulation_run(layout_id, run_config)
    print(f"✅ Simulation started with ID: {run_id}")
    
    # Test 3: Save some orders
    print("\n3. Testing order saving...")
    sample_orders = [
        {
            'order_id': 'ORD001',
            'timestamp': datetime.now(),
            'status': 'pending',
            'total_items': 3,
            'estimated_pick_time': 120.5,
            'priority': 1,
            'items': [
                {
                    'item_id': 'ITEM001',
                    'shelf_x': 3,
                    'shelf_y': 3,
                    'zone': 'A',
                    'item_type': 'Electronics',
                    'priority': 1,
                    'quantity': 1
                }
            ]
        },
        {
            'order_id': 'ORD002',
            'timestamp': datetime.now(),
            'status': 'completed',
            'total_items': 2,
            'estimated_pick_time': 85.2,
            'priority': 2,
            'items': [
                {
                    'item_id': 'ITEM002',
                    'shelf_x': 5,
                    'shelf_y': 3,
                    'zone': 'B',
                    'item_type': 'Clothing',
                    'priority': 2,
                    'quantity': 2
                }
            ]
        }
    ]
    
    for order in sample_orders:
        persistence.save_order(run_id, order)
    print(f"✅ Saved {len(sample_orders)} orders")
    
    # Test 4: Save performance metrics
    print("\n4. Testing metrics saving...")
    metrics = {
        'average_pick_time': {'value': 45.2, 'unit': 'seconds'},
        'total_distance': {'value': 1250.5, 'unit': 'meters'},
        'orders_completed': {'value': 48, 'unit': 'orders'},
        'efficiency_score': {'value': 78.5, 'unit': 'percentage'}
    }
    
    persistence.end_simulation_run(run_id, metrics)
    print("✅ Simulation ended and metrics saved")
    
    # Test 5: Retrieve data
    print("\n5. Testing data retrieval...")
    
    # Get simulation runs
    runs = persistence.get_simulation_runs(10)
    print(f"✅ Retrieved {len(runs)} simulation runs")
    
    # Get orders for the run
    orders_df = persistence.get_run_orders(run_id)
    print(f"✅ Retrieved {len(orders_df)} orders for run {run_id}")
    
    # Get metrics for the run
    metrics_df = persistence.get_run_metrics(run_id)
    print(f"✅ Retrieved {len(metrics_df)} metrics for run {run_id}")
    
    # Get layout summary
    layouts_df = persistence.get_layout_summary()
    print(f"✅ Retrieved {len(layouts_df)} layouts")
    
    # Test 6: Database stats
    print("\n6. Testing database statistics...")
    stats = persistence.get_database_stats()
    print(f"✅ Database stats: {stats}")
    
    # Test 7: Export data
    print("\n7. Testing data export...")
    exported_files = persistence.export_all_data()
    print(f"✅ Exported data to: {exported_files}")
    
    print("\n🎉 All tests completed successfully!")
    
    # Clean up test database
    import os
    if os.path.exists("test_warehouse_data.db"):
        os.remove("test_warehouse_data.db")
        print("🧹 Test database cleaned up")

if __name__ == "__main__":
    test_data_persistence() 