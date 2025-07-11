#!/usr/bin/env python3
"""
Simple test for layout repair functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.layout_repair import LayoutRepair
from utils.layout_validator import LayoutValidator

def test_layout_repair():
    """Test layout repair functionality"""
    print("🧪 Testing Layout Repair...")
    
    # Create an invalid layout (shelves blocking entry and stations)
    invalid_shelves = [(0, 0), (1, 0), (2, 0), (3, 0)]  # Block entry and stations
    packing_stations = [(2, 0), (8, 0)]
    
    # Create repair instance
    repair = LayoutRepair(grid_width=12, grid_height=10)
    validator = LayoutValidator(grid_width=12, grid_height=10)
    
    # Validate that the layout is indeed invalid
    validation = validator.validate_reachability(invalid_shelves, packing_stations)
    print(f"📊 Initial layout valid: {validation['valid']}")
    print(f"📊 Unreachable shelves: {len(validation['unreachable_shelves'])}")
    
    # Try to repair the layout
    repair_result = repair.repair_layout(invalid_shelves, packing_stations)
    
    print(f"🔧 Repair success: {repair_result['success']}")
    print(f"🔧 Repair message: {repair_result['message']}")
    
    if repair_result['success']:
        # Validate the repaired layout
        final_validation = validator.validate_reachability(repair_result['repaired_shelves'], packing_stations)
        print(f"📊 Repaired layout valid: {final_validation['valid']}")
        print(f"📊 Shelves moved: {len(repair_result['moved_shelves'])}")
        
        if final_validation['valid']:
            print("✅ Layout repair test passed!")
            return True
        else:
            print("❌ Repaired layout is still invalid")
            return False
    else:
        print("❌ Layout repair failed")
        return False

def test_create_valid_layout():
    """Test creating a new valid layout from scratch"""
    print("\n🧪 Testing Create Valid Layout...")
    
    packing_stations = [(2, 0), (8, 0)]
    repair = LayoutRepair(grid_width=12, grid_height=10)
    validator = LayoutValidator(grid_width=12, grid_height=10)
    
    # Try to create a valid layout with 5 shelves (smaller number)
    result = repair.create_valid_layout(5, packing_stations)
    
    print(f"🔧 Create success: {result['success']}")
    print(f"🔧 Create message: {result['message']}")
    
    if result['success']:
        # Validate the new layout
        validation = validator.validate_reachability(result['shelves'], packing_stations)
        print(f"📊 New layout valid: {validation['valid']}")
        print(f"📊 Shelves created: {len(result['shelves'])}")
        
        if validation['valid']:
            print("✅ Create valid layout test passed!")
            return True
        else:
            print("❌ Created layout is invalid")
            return False
    else:
        print("❌ Create valid layout failed")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Layout Repair Tests")
    print("=" * 50)
    
    try:
        test1 = test_layout_repair()
        test2 = test_create_valid_layout()
        
        if test1 and test2:
            print("\n" + "=" * 50)
            print("🎉 All layout repair tests passed!")
            print("✅ Layout repair works correctly")
            print("✅ Valid layout creation works")
            return True
        else:
            print("\n❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 