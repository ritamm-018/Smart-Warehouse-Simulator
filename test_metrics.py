#!/usr/bin/env python3
"""
Test script to verify metrics are updating properly
"""

import time
import random
from datetime import datetime

def test_metrics_update():
    """Test the metrics update logic"""
    print("🧪 Testing Metrics Update Logic...")
    
    # Simulate session state
    session_state = {
        'realtime_metrics': {
            'average_pick_time': 60.0,
            'total_pickup_time': 0.0,
            'orders_completed': 0,
            'total_distance': 0.0
        },
        'metrics_start_time': time.time(),
        'simulation_completed': False,
        'metrics_update_time': time.time(),
        'num_orders': 50
    }
    
    print(f"Initial metrics: {session_state['realtime_metrics']}")
    
    # Simulate 10 updates
    for i in range(10):
        current_time = time.time()
        
        # Update logic from metrics.py
        if current_time - session_state.get('metrics_update_time', 0) >= 2.0:
            session_state['metrics_update_time'] = current_time
            
            if not session_state.get('simulation_completed', False):
                metrics = session_state['realtime_metrics']
                total_orders = session_state.get('num_orders', 50)
                
                prev_avg = metrics['average_pick_time']
                prev_total = metrics['total_pickup_time']
                prev_orders = metrics['orders_completed']
                prev_dist = metrics['total_distance']

                if prev_orders < total_orders:
                    new_avg = max(30, prev_avg + random.uniform(-2, 2))
                    new_total = prev_total + random.uniform(5, 15)
                    new_orders = min(total_orders, prev_orders + random.randint(0, 3))
                    new_dist = prev_dist + random.uniform(10, 30)

                    metrics['average_pick_time'] = new_avg
                    metrics['total_pickup_time'] = new_total
                    metrics['orders_completed'] = new_orders
                    metrics['total_distance'] = new_dist
                    
                    if metrics['orders_completed'] >= total_orders:
                        session_state['simulation_completed'] = True
                
                print(f"Update {i+1}: {metrics}")
        
        # Simulate time passing
        time.sleep(0.1)
    
    print(f"Final metrics: {session_state['realtime_metrics']}")
    print(f"Simulation completed: {session_state['simulation_completed']}")
    print("✅ Metrics update test completed!")

if __name__ == "__main__":
    test_metrics_update() 