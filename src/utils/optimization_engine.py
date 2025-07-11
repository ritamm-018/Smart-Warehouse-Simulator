import numpy as np
import random
from stable_baselines3 import DQN
from .warehouse_env import WarehouseEnv
from .layout_validator import LayoutValidator
from .layout_repair import LayoutRepair
from .advanced_layout_optimizer import AdvancedLayoutOptimizer
import copy

class OptimizationEngine:
    """Improved optimization engine with validation and fallback mechanisms"""
    
    def __init__(self, grid_width, grid_height, num_orders, items_per_order):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.num_orders = num_orders
        self.items_per_order = items_per_order
        self.validator = LayoutValidator(grid_width, grid_height)
        self.repair = LayoutRepair(grid_width, grid_height)
        self.advanced_optimizer = AdvancedLayoutOptimizer(rows=grid_height, columns=grid_width)
        
    def validate_layout(self, shelf_positions, packing_stations):
        """Validate layout and return detailed results"""
        reachability = self.validator.validate_reachability(shelf_positions, packing_stations)
        quality = self.validator.validate_layout_quality(shelf_positions, packing_stations)
        
        return {
            'reachability': reachability,
            'quality': quality,
            'overall_valid': reachability['valid'] and quality['score'] > 30
        }
    
    def run_rl_optimization(self, initial_shelves, packing_stations, model_path):
        """
        Run RL optimization with validation and fallback
        
        Returns:
            dict: {
                'success': bool,
                'optimized_shelves': list,
                'validation_results': dict,
                'improvement_score': float,
                'fallback_used': bool,
                'message': str
            }
        """
        try:
            # Use advanced layout optimizer instead of old RL logic
            optimization_result = self.advanced_optimizer.optimize_layout_with_interface(
                initial_shelves, 
                packing_stations, 
                model_path
            )
            
            if optimization_result['success']:
                return {
                    'success': True,
                    'optimized_shelves': optimization_result['optimized_shelves'],
                    'validation_results': optimization_result['validation_results'],
                    'improvement_score': optimization_result['improvement_score'],
                    'fallback_used': optimization_result['fallback_used'],
                    'message': optimization_result['message']
                }
            else:
                return {
                    'success': False,
                    'optimized_shelves': initial_shelves,
                    'validation_results': optimization_result['validation_results'],
                    'improvement_score': 0,
                    'fallback_used': True,
                    'message': optimization_result['message']
                }
                
        except Exception as e:
            return {
                'success': False,
                'optimized_shelves': initial_shelves,
                'validation_results': None,
                'improvement_score': 0,
                'fallback_used': True,
                'message': f"RL optimization error: {str(e)}"
            }
    
    def run_heuristic_optimization(self, initial_shelves, packing_stations):
        """
        Fallback heuristic optimization when RL fails
        
        Returns:
            dict: Same format as run_rl_optimization
        """
        try:
            # Use advanced layout optimizer for heuristic optimization too
            optimization_result = self.advanced_optimizer.optimize_layout_with_interface(
                initial_shelves, 
                packing_stations, 
                None  # No model path for heuristic
            )
            
            if optimization_result['success']:
                return {
                    'success': True,
                    'optimized_shelves': optimization_result['optimized_shelves'],
                    'validation_results': optimization_result['validation_results'],
                    'improvement_score': optimization_result['improvement_score'],
                    'fallback_used': True,
                    'message': f"Heuristic optimization: {optimization_result['message']}"
                }
            else:
                return {
                    'success': False,
                    'optimized_shelves': initial_shelves,
                    'validation_results': optimization_result['validation_results'],
                    'improvement_score': 0,
                    'fallback_used': True,
                    'message': f"Heuristic optimization failed: {optimization_result['message']}"
                }
            
        except Exception as e:
            return {
                'success': False,
                'optimized_shelves': initial_shelves,
                'validation_results': None,
                'improvement_score': 0,
                'fallback_used': True,
                'message': f"Heuristic optimization error: {str(e)}"
            }
    
    def optimize_with_fallback(self, initial_shelves, packing_stations, model_path):
        """
        Main optimization method with comprehensive fallback and layout repair
        
        Returns:
            dict: Optimization results with validation
        """
        # Use the advanced layout optimizer directly
        optimization_result = self.advanced_optimizer.optimize_layout_with_interface(
            initial_shelves, 
            packing_stations, 
            model_path
        )
        
        return optimization_result 