import numpy as np
import random
from .layout_validator import LayoutValidator

class LayoutRepair:
    """Repairs invalid warehouse layouts by moving unreachable shelves"""
    
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.validator = LayoutValidator(grid_width, grid_height)
    
    def find_valid_positions(self, current_shelves, packing_stations, entry_point=(0, 0)):
        """Find valid positions for shelves that don't block paths"""
        valid_positions = []
        
        # Create a grid with current shelves
        grid = self.validator.build_grid(current_shelves)
        
        # Check each position in the grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Skip if position is already occupied
                if grid[y][x] == 1:
                    continue
                
                # Skip if it's the entry point or a packing station
                if (x, y) == entry_point or (x, y) in packing_stations:
                    continue
                
                # Test if this position would create a valid layout
                test_shelves = current_shelves + [(x, y)]
                test_grid = self.validator.build_grid(test_shelves)
                
                # Check if entry point is still accessible
                if test_grid[entry_point[1]][entry_point[0]] == 1:
                    continue
                
                # Check if this position is reachable from entry
                path = self.validator.a_star(entry_point, (x, y), test_grid)
                if path is not None:
                    valid_positions.append((x, y))
        
        return valid_positions
    
    def repair_layout(self, shelf_positions, packing_stations, entry_point=(0, 0)):
        """
        Repair an invalid layout by moving unreachable shelves to valid positions
        
        Returns:
            dict: {
                'success': bool,
                'repaired_shelves': list,
                'moved_shelves': list,
                'message': str
            }
        """
        # First validate the current layout
        validation = self.validator.validate_reachability(shelf_positions, packing_stations, entry_point)
        
        if validation['valid']:
            return {
                'success': True,
                'repaired_shelves': shelf_positions,
                'moved_shelves': [],
                'message': "Layout is already valid"
            }
        
        # Get unreachable shelves
        unreachable_shelves = validation['unreachable_shelves']
        reachable_shelves = [s for s in shelf_positions if s not in unreachable_shelves]
        
        if not unreachable_shelves:
            return {
                'success': False,
                'repaired_shelves': shelf_positions,
                'moved_shelves': [],
                'message': "No unreachable shelves to repair"
            }
        
        # Try to find valid positions for unreachable shelves
        repaired_shelves = reachable_shelves.copy()
        moved_shelves = []
        
        for unreachable_shelf in unreachable_shelves:
            # Find valid positions considering current repaired layout
            valid_positions = self.find_valid_positions(repaired_shelves, packing_stations, entry_point)
            
            if valid_positions:
                # Choose the best position (closest to original or most central)
                best_position = self._choose_best_position(unreachable_shelf, valid_positions)
                repaired_shelves.append(best_position)
                moved_shelves.append((unreachable_shelf, best_position))
            else:
                # If no valid position found, skip this shelf
                continue
        
        # Validate the repaired layout
        final_validation = self.validator.validate_reachability(repaired_shelves, packing_stations, entry_point)
        
        if final_validation['valid']:
            return {
                'success': True,
                'repaired_shelves': repaired_shelves,
                'moved_shelves': moved_shelves,
                'message': f"Successfully repaired layout. Moved {len(moved_shelves)} shelves."
            }
        else:
            return {
                'success': False,
                'repaired_shelves': shelf_positions,  # Return original if repair failed
                'moved_shelves': moved_shelves,
                'message': f"Partial repair completed but layout still invalid. {len(final_validation['unreachable_shelves'])} shelves still unreachable."
            }
    
    def _choose_best_position(self, original_shelf, valid_positions):
        """Choose the best position from valid positions"""
        if not valid_positions:
            return None
        
        # Calculate distances to original position
        distances = []
        for pos in valid_positions:
            distance = abs(pos[0] - original_shelf[0]) + abs(pos[1] - original_shelf[1])
            distances.append((distance, pos))
        
        # Sort by distance and choose the closest
        distances.sort()
        return distances[0][1]
    
    def create_valid_layout(self, num_shelves, packing_stations, entry_point=(0, 0)):
        """
        Create a completely new valid layout from scratch
        
        Returns:
            dict: {
                'success': bool,
                'shelves': list,
                'message': str
            }
        """
        shelves = []
        attempts = 0
        max_attempts = 2000  # Increased attempts
        
        # Start with a simple pattern that's guaranteed to work
        # Place shelves in a grid pattern, avoiding entry and stations
        base_positions = []
        for y in range(2, self.grid_height - 1):  # Start from row 2 to avoid entry row
            for x in range(1, self.grid_width - 1):
                if (x, y) not in packing_stations and (x, y) != entry_point:
                    base_positions.append((x, y))
        
        # Shuffle the positions
        random.shuffle(base_positions)
        
        # Take the first num_shelves positions
        for pos in base_positions[:num_shelves]:
            shelves.append(pos)
        
        # Validate the created layout
        if shelves:
            validation = self.validator.validate_reachability(shelves, packing_stations, entry_point)
            if validation['valid']:
                return {
                    'success': True,
                    'shelves': shelves,
                    'message': f"Successfully created valid layout with {len(shelves)} shelves"
                }
        
        # If the simple approach failed, try random placement
        shelves = []
        while len(shelves) < num_shelves and attempts < max_attempts:
            attempts += 1
            
            # Generate random position
            x = random.randint(1, self.grid_width - 2)  # Avoid edges
            y = random.randint(1, self.grid_height - 2)
            
            # Skip if position is already occupied
            if (x, y) in shelves:
                continue
            
            # Skip if it's the entry point or a packing station
            if (x, y) == entry_point or (x, y) in packing_stations:
                continue
            
            # Test if this position creates a valid layout
            test_shelves = shelves + [(x, y)]
            validation = self.validator.validate_reachability(test_shelves, packing_stations, entry_point)
            
            if validation['valid']:
                shelves.append((x, y))
        
        if len(shelves) == num_shelves:
            return {
                'success': True,
                'shelves': shelves,
                'message': f"Successfully created valid layout with {num_shelves} shelves"
            }
        else:
            return {
                'success': False,
                'shelves': shelves,
                'message': f"Could only place {len(shelves)} out of {num_shelves} shelves"
            } 