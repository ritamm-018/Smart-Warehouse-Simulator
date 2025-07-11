#!/usr/bin/env python3
"""
Test script for Advanced Layout Optimizer

This script tests all the constraints and features of the advanced layout optimizer:
1. Aisle spacing validation
2. Reachability validation
3. Category encoding
4. JSON output structure
5. Fallback mechanisms
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.advanced_layout_optimizer import AdvancedLayoutOptimizer

def test_basic_optimization():
    """Test basic layout optimization"""
    print("🧪 Testing Basic Layout Optimization...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=15, 
        num_packing_stations=2, 
        num_robots=3
    )
    
    result = optimizer.optimize_layout(max_attempts=5)
    
    print(f"📊 Optimization success: {result['success']}")
    if result['success']:
        print(f"📊 Quality score: {result['validation']['quality_score']}")
        print(f"📊 Utilization rate: {result['validation']['utilization_rate']:.2%}")
        print(f"📊 Shelves placed: {len(result['layout']['shelves'])}")
        print(f"📊 Packing stations: {len(result['layout']['packing_stations'])}")
        print(f"📊 Robots: {len(result['layout']['robots'])}")
        
        # Test JSON export
        json_output = optimizer.export_layout(result['layout'])
        print(f"📊 JSON output length: {len(json_output)} characters")
        
        return True
    else:
        print(f"❌ Optimization failed: {result['message']}")
        return False

def test_aisle_spacing():
    """Test that aisle spacing constraints are respected"""
    print("\n🧪 Testing Aisle Spacing Constraints...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=10, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    result = optimizer.optimize_layout(max_attempts=3)
    
    if result['success']:
        # Check that no shelves are in aisle positions
        aisle_violations = result['validation']['aisle_violations']
        if len(aisle_violations) == 0:
            print("✅ No aisle spacing violations found")
            
            # Verify manually that shelves are not in aisle positions
            for shelf in result['layout']['shelves']:
                x, y = shelf['position']
                # Every 3rd row/column should be aisles
                if y % 3 == 2 or x % 3 == 2:
                    print(f"❌ Shelf found in aisle position: ({x}, {y})")
                    return False
            
            print("✅ All shelves respect aisle spacing rules")
            return True
        else:
            print(f"❌ Found {len(aisle_violations)} aisle violations")
            return False
    else:
        print(f"❌ Optimization failed: {result['message']}")
        return False

def test_reachability():
    """Test that all shelves and packing stations are reachable"""
    print("\n🧪 Testing Reachability Validation...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=12, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    result = optimizer.optimize_layout(max_attempts=3)
    
    if result['success']:
        unreachable_shelves = result['validation']['unreachable_shelves']
        unreachable_stations = result['validation']['unreachable_stations']
        
        if len(unreachable_shelves) == 0 and len(unreachable_stations) == 0:
            print("✅ All shelves and packing stations are reachable")
            return True
        else:
            print(f"❌ Found {len(unreachable_shelves)} unreachable shelves")
            print(f"❌ Found {len(unreachable_stations)} unreachable stations")
            return False
    else:
        print(f"❌ Optimization failed: {result['message']}")
        return False

def test_category_encoding():
    """Test that shelves have proper category encoding"""
    print("\n🧪 Testing Category Encoding...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=10, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    result = optimizer.optimize_layout(max_attempts=3)
    
    if result['success']:
        category_distribution = result['validation']['category_distribution']
        print(f"📊 Category distribution: {category_distribution}")
        
        # Check that all shelves have categories
        for shelf in result['layout']['shelves']:
            if 'category' not in shelf:
                print(f"❌ Shelf missing category: {shelf}")
                return False
        
        # Check that categories are valid
        valid_categories = ['a', 'b', 'c', 'd', 'e']
        for shelf in result['layout']['shelves']:
            if shelf['category'] not in valid_categories:
                print(f"❌ Invalid category: {shelf['category']}")
                return False
        
        print("✅ All shelves have valid category encoding")
        return True
    else:
        print(f"❌ Optimization failed: {result['message']}")
        return False

def test_json_structure():
    """Test that the JSON output has the correct structure"""
    print("\n🧪 Testing JSON Output Structure...")
    
    optimizer = AdvancedLayoutOptimizer(
        rows=12, 
        columns=12, 
        num_shelves=8, 
        num_packing_stations=2, 
        num_robots=2
    )
    
    result = optimizer.optimize_layout(max_attempts=3)
    
    if result['success']:
        json_output = optimizer.export_layout(result['layout'])
        
        try:
            # Parse JSON to verify structure
            layout_data = json.loads(json_output)
            
            # Check required fields
            required_fields = ['rows', 'columns', 'entry_points', 'shelves', 
                             'packing_stations', 'drop_zones', 'robots']
            
            for field in required_fields:
                if field not in layout_data:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Check data types and structure
            if not isinstance(layout_data['rows'], int):
                print("❌ 'rows' should be integer")
                return False
            
            if not isinstance(layout_data['columns'], int):
                print("❌ 'columns' should be integer")
                return False
            
            if not isinstance(layout_data['entry_points'], list):
                print("❌ 'entry_points' should be list")
                return False
            
            if not isinstance(layout_data['shelves'], list):
                print("❌ 'shelves' should be list")
                return False
            
            # Check shelf structure
            for shelf in layout_data['shelves']:
                if 'position' not in shelf or 'category' not in shelf:
                    print(f"❌ Shelf missing required fields: {shelf}")
                    return False
                
                if not isinstance(shelf['position'], list) or len(shelf['position']) != 2:
                    print(f"❌ Shelf position should be [x, y]: {shelf['position']}")
                    return False
            
            # Check robot structure
            for robot in layout_data['robots']:
                if 'id' not in robot or 'position' not in robot:
                    print(f"❌ Robot missing required fields: {robot}")
                    return False
            
            print("✅ JSON structure is valid")
            print(f"📊 Sample JSON output:\n{json.dumps(layout_data, indent=2)[:500]}...")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False
    else:
        print(f"❌ Optimization failed: {result['message']}")
        return False

def test_fallback_layout():
    """Test the fallback layout creation"""
    print("\n🧪 Testing Fallback Layout Creation...")
    
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
        print(f"📊 Shelves in fallback: {len(result['layout']['shelves'])}")
        
        if validation['valid']:
            print("✅ Fallback layout is valid")
            return True
        else:
            print("❌ Fallback layout is invalid")
            return False
    else:
        print(f"❌ Fallback creation failed: {result['message']}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Advanced Layout Optimizer Tests")
    print("=" * 60)
    
    tests = [
        test_basic_optimization,
        test_aisle_spacing,
        test_reachability,
        test_category_encoding,
        test_json_structure,
        test_fallback_layout
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"🎉 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Advanced layout optimizer is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 