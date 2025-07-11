import numpy as np
from collections import deque
import heapq

class LayoutValidator:
    """Validates warehouse layouts for reachability and feasibility"""
    
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        
    def build_grid(self, shelf_positions):
        """Build grid from shelf positions"""
        grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        for x, y in shelf_positions:
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                grid[y][x] = 1  # 1 = blocked (shelf)
        return grid
    
    def a_star(self, start, goal, grid):
        """A* pathfinding algorithm"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        open_set = []
        heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, [start]))
        closed_set = set()
        
        while open_set:
            est_total, cost, current, path = heapq.heappop(open_set)
            if current == goal:
                return path
            if current in closed_set:
                continue
            closed_set.add(current)
            x, y = current
            
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    if grid[ny][nx] == 1:  # Blocked by shelf
                        continue
                    neighbor = (nx, ny)
                    if neighbor in closed_set:
                        continue
                    heapq.heappush(open_set, (cost+1+heuristic(neighbor, goal), cost+1, neighbor, path+[neighbor]))
        
        return None  # No path found
    
    def validate_reachability(self, shelf_positions, packing_stations, entry_point=(0, 0)):
        """
        Validate that all shelves are reachable from entry point and packing stations
        
        Returns:
            dict: {
                'valid': bool,
                'unreachable_shelves': list,
                'unreachable_stations': list,
                'issues': list
            }
        """
        grid = self.build_grid(shelf_positions)
        issues = []
        unreachable_shelves = []
        unreachable_stations = []
        
        # Check if entry point is blocked
        if grid[entry_point[1]][entry_point[0]] == 1:
            issues.append(f"Entry point {entry_point} is blocked by a shelf")
            return {
                'valid': False,
                'unreachable_shelves': shelf_positions,
                'unreachable_stations': packing_stations,
                'issues': issues
            }
        
        # Check reachability of each shelf from entry point
        for shelf in shelf_positions:
            path = self.a_star(entry_point, shelf, grid)
            if path is None:
                unreachable_shelves.append(shelf)
                issues.append(f"Shelf at {shelf} is unreachable from entry point")
        
        # Check reachability of packing stations from shelves
        for station in packing_stations:
            station_reachable = False
            # First check if station is reachable from entry point directly
            if grid[station[1]][station[0]] != 1:  # Station not blocked
                path_from_entry = self.a_star(entry_point, station, grid)
                if path_from_entry is not None:
                    station_reachable = True
            
            # If not reachable from entry, check from reachable shelves
            if not station_reachable:
                for shelf in shelf_positions:
                    if shelf not in unreachable_shelves:  # Only check from reachable shelves
                        path = self.a_star(shelf, station, grid)
                        if path is not None:
                            station_reachable = True
                            break
            
            if not station_reachable:
                unreachable_stations.append(station)
                issues.append(f"Packing station at {station} is unreachable from any shelf")
        
        # Check if packing stations are blocked
        for station in packing_stations:
            if grid[station[1]][station[0]] == 1:
                unreachable_stations.append(station)
                issues.append(f"Packing station {station} is blocked by a shelf")
        
        valid = len(unreachable_shelves) == 0 and len(unreachable_stations) == 0
        
        return {
            'valid': valid,
            'unreachable_shelves': unreachable_shelves,
            'unreachable_stations': unreachable_stations,
            'issues': issues
        }
    
    def validate_layout_quality(self, shelf_positions, packing_stations, entry_point=(0, 0)):
        """
        Assess layout quality based on various metrics
        
        Returns:
            dict: {
                'score': float (0-100),
                'metrics': dict,
                'recommendations': list
            }
        """
        grid = self.build_grid(shelf_positions)
        recommendations = []
        
        # Calculate shelf distribution
        if shelf_positions:
            x_coords = [pos[0] for pos in shelf_positions]
            y_coords = [pos[1] for pos in shelf_positions]
            x_spread = np.std(x_coords)
            y_spread = np.std(y_coords)
            total_spread = x_spread + y_spread
        else:
            total_spread = 0
        
        # Calculate average distance from entry to shelves
        total_entry_distance = 0
        for shelf in shelf_positions:
            path = self.a_star(entry_point, shelf, grid)
            if path:
                total_entry_distance += len(path) - 1
        
        avg_entry_distance = total_entry_distance / len(shelf_positions) if shelf_positions else 0
        
        # Calculate average distance from shelves to nearest packing station
        total_station_distance = 0
        for shelf in shelf_positions:
            min_distance = float('inf')
            for station in packing_stations:
                path = self.a_star(shelf, station, grid)
                if path:
                    distance = len(path) - 1
                    min_distance = min(min_distance, distance)
            if min_distance != float('inf'):
                total_station_distance += min_distance
        
        avg_station_distance = total_station_distance / len(shelf_positions) if shelf_positions else 0
        
        # Calculate score (higher is better)
        score = 100
        
        # Penalize poor spread (too clustered or too spread out)
        if total_spread < 2:
            score -= 20
            recommendations.append("Shelves are too clustered - consider spreading them out")
        elif total_spread > 8:
            score -= 15
            recommendations.append("Shelves are too spread out - consider clustering them")
        
        # Penalize long distances
        if avg_entry_distance > 5:
            score -= 25
            recommendations.append("Average distance from entry to shelves is too high")
        
        if avg_station_distance > 5:
            score -= 25
            recommendations.append("Average distance from shelves to packing stations is too high")
        
        # Bonus for good distribution
        if 2 <= total_spread <= 8:
            score += 10
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'metrics': {
                'shelf_spread': total_spread,
                'avg_entry_distance': avg_entry_distance,
                'avg_station_distance': avg_station_distance,
                'num_shelves': len(shelf_positions)
            },
            'recommendations': recommendations
        }
    
    def get_optimization_suggestions(self, shelf_positions, packing_stations, entry_point=(0, 0)):
        """
        Get specific suggestions for layout optimization
        
        Returns:
            list: List of optimization suggestions
        """
        suggestions = []
        grid = self.build_grid(shelf_positions)
        
        # Check for isolated shelves
        for shelf in shelf_positions:
            neighbors = 0
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = shelf[0] + dx, shelf[1] + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    if grid[ny][nx] == 1:  # Adjacent shelf
                        neighbors += 1
            
            if neighbors == 0:
                suggestions.append(f"Move isolated shelf at {shelf} closer to other shelves")
        
        # Check for bottlenecks
        bottleneck_points = []
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if grid[y][x] == 0:  # Free space
                    blocked_directions = 0
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and 
                            grid[ny][nx] == 1):
                            blocked_directions += 1
                    
                    if blocked_directions >= 3:
                        bottleneck_points.append((x, y))
        
        if bottleneck_points:
            suggestions.append(f"Consider removing shelves near bottleneck points: {bottleneck_points[:3]}")
        
        return suggestions 