import json
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Tuple, Optional
import os

class WarehouseDataLoader:
    """Load and convert warehouse layout data from various file formats"""
    
    def __init__(self):
        self.sample_layouts = {
            'walmart_style': 'sample_data/walmart_style_warehouse.json',
            'amazon_style': 'sample_data/amazon_style_warehouse.json',
            'target_style': 'sample_data/target_style_warehouse.json',
            'costco_style': 'sample_data/costco_style_warehouse.json'
        }
    
    def create_sample_data_directory(self):
        """Create the sample data directory if it doesn't exist"""
        if not os.path.exists('sample_data'):
            os.makedirs('sample_data')
            st.info("📁 Created sample_data directory")
    
    def generate_sample_orders(self, layout_name: str, num_orders: int = 100) -> pd.DataFrame:
        """Generate sample order data for a specific layout"""
        layout_data = self.load_layout_from_json(self.sample_layouts[layout_name])
        if not layout_data:
            return pd.DataFrame()
        
        orders = []
        shelves = layout_data['shelves']
        zones = layout_data.get('zones', {})
        
        # Create item catalog based on zones
        item_catalog = {}
        for zone_name, zone_info in zones.items():
            for item_type in zone_info['items']:
                # Find shelves in this zone
                zone_shelves = [s for s in shelves if s.get('zone') == zone_name]
                if zone_shelves:
                    for shelf in zone_shelves:
                        item_id = f"{zone_name}_{item_type}_{shelf['x']}_{shelf['y']}"
                        item_catalog[item_id] = {
                            'shelf_x': shelf['x'],
                            'shelf_y': shelf['y'],
                            'zone': zone_name,
                            'item_type': item_type,
                            'priority': np.random.randint(1, 4)  # 1=low, 2=medium, 3=high
                        }
        
        # Generate orders
        for order_id in range(1, num_orders + 1):
            # Random number of items per order (1-5)
            num_items = np.random.randint(1, 6)
            
            # Select random items
            selected_items = np.random.choice(list(item_catalog.keys()), 
                                            size=min(num_items, len(item_catalog)), 
                                            replace=False)
            
            for item_id in selected_items:
                item_info = item_catalog[item_id]
                orders.append({
                    'order_id': f"ORD_{order_id:04d}",
                    'item_id': item_id,
                    'shelf_location_x': item_info['shelf_x'],
                    'shelf_location_y': item_info['shelf_y'],
                    'zone': item_info['zone'],
                    'item_type': item_info['item_type'],
                    'priority': item_info['priority'],
                    'quantity': np.random.randint(1, 4),
                    'order_timestamp': pd.Timestamp.now() - pd.Timedelta(minutes=np.random.randint(0, 1440))
                })
        
        return pd.DataFrame(orders)
    
    def save_sample_orders(self):
        """Save sample order data for all layouts"""
        self.create_sample_data_directory()
        
        for layout_name in self.sample_layouts.keys():
            # Generate different numbers of orders for different layouts
            if layout_name == 'walmart_style':
                num_orders = 200  # High volume
            elif layout_name == 'amazon_style':
                num_orders = 150  # Medium-high volume
            elif layout_name == 'target_style':
                num_orders = 120  # Medium volume
            else:  # costco_style
                num_orders = 80   # Lower volume, bulk orders
            
            orders_df = self.generate_sample_orders(layout_name, num_orders)
            filename = f"sample_data/{layout_name}_orders.csv"
            orders_df.to_csv(filename, index=False)
            st.success(f"✅ Saved {len(orders_df)} orders for {layout_name} to {filename}")
    
    def generate_walmart_style_layout(self) -> Dict:
        """Generate a Walmart-style warehouse layout"""
        layout = {
            "name": "Walmart Distribution Center",
            "description": "Large-scale retail distribution center with high-volume picking",
            "grid_width": 20,
            "grid_height": 15,
            "layout_type": "Walmart Style",
            "shelves": [],
            "stations": [],
            "entry_exit": {"x": 10, "y": 14},
            "zones": {
                "electronics": {"color": "#FF6B6B", "items": ["laptops", "phones", "tablets"]},
                "clothing": {"color": "#4ECDC4", "items": ["shirts", "pants", "shoes"]},
                "groceries": {"color": "#45B7D1", "items": ["canned_goods", "frozen_foods", "produce"]},
                "home": {"color": "#96CEB4", "items": ["furniture", "appliances", "decor"]}
            }
        }
        
        # Generate shelves in organized zones
        # Electronics zone (top left)
        for x in range(2, 8):
            for y in range(2, 6):
                layout["shelves"].append({
                    "x": x, "y": y, 
                    "zone": "electronics",
                    "capacity": 100,
                    "current_items": np.random.randint(20, 80)
                })
        
        # Clothing zone (top right)
        for x in range(12, 18):
            for y in range(2, 6):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "clothing", 
                    "capacity": 150,
                    "current_items": np.random.randint(30, 120)
                })
        
        # Groceries zone (middle left)
        for x in range(2, 8):
            for y in range(7, 11):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "groceries",
                    "capacity": 200,
                    "current_items": np.random.randint(50, 180)
                })
        
        # Home zone (middle right)
        for x in range(12, 18):
            for y in range(7, 11):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "home",
                    "capacity": 80,
                    "current_items": np.random.randint(15, 65)
                })
        
        # Packing stations along bottom
        layout["stations"] = [
            {"x": 3, "y": 13, "type": "standard", "capacity": 50},
            {"x": 7, "y": 13, "type": "express", "capacity": 30},
            {"x": 11, "y": 13, "type": "standard", "capacity": 50},
            {"x": 15, "y": 13, "type": "bulk", "capacity": 100}
        ]
        
        return layout
    
    def generate_amazon_style_layout(self) -> Dict:
        """Generate an Amazon-style warehouse layout"""
        layout = {
            "name": "Amazon Fulfillment Center",
            "description": "High-tech fulfillment center with robotic assistance",
            "grid_width": 18,
            "grid_height": 12,
            "layout_type": "Amazon Style",
            "shelves": [],
            "stations": [],
            "entry_exit": {"x": 9, "y": 11},
            "zones": {
                "books": {"color": "#FFD93D", "items": ["fiction", "non_fiction", "textbooks"]},
                "electronics": {"color": "#6BCF7F", "items": ["computers", "accessories", "gaming"]},
                "fashion": {"color": "#4D96FF", "items": ["clothing", "jewelry", "watches"]},
                "home": {"color": "#FF6B6B", "items": ["kitchen", "bathroom", "bedroom"]}
            }
        }
        
        # Generate shelves in robotic-friendly grid pattern
        # Books zone
        for x in range(1, 7):
            for y in range(1, 5):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "books",
                    "capacity": 120,
                    "current_items": np.random.randint(25, 100),
                    "robot_accessible": True
                })
        
        # Electronics zone
        for x in range(11, 17):
            for y in range(1, 5):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "electronics",
                    "capacity": 80,
                    "current_items": np.random.randint(15, 70),
                    "robot_accessible": True
                })
        
        # Fashion zone
        for x in range(1, 7):
            for y in range(6, 10):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "fashion",
                    "capacity": 100,
                    "current_items": np.random.randint(20, 85),
                    "robot_accessible": True
                })
        
        # Home zone
        for x in range(11, 17):
            for y in range(6, 10):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "home",
                    "capacity": 90,
                    "current_items": np.random.randint(18, 75),
                    "robot_accessible": True
                })
        
        # Packing stations with different types
        layout["stations"] = [
            {"x": 2, "y": 10, "type": "standard", "capacity": 40},
            {"x": 6, "y": 10, "type": "prime", "capacity": 25},
            {"x": 10, "y": 10, "type": "standard", "capacity": 40},
            {"x": 14, "y": 10, "type": "same_day", "capacity": 20}
        ]
        
        return layout
    
    def generate_target_style_layout(self) -> Dict:
        """Generate a Target-style warehouse layout"""
        layout = {
            "name": "Target Distribution Center",
            "description": "Multi-category retail distribution with seasonal focus",
            "grid_width": 16,
            "grid_height": 14,
            "layout_type": "Target Style",
            "shelves": [],
            "stations": [],
            "entry_exit": {"x": 8, "y": 13},
            "zones": {
                "apparel": {"color": "#FF9FF3", "items": ["men", "women", "kids", "accessories"]},
                "home": {"color": "#54A0FF", "items": ["furniture", "decor", "kitchen", "bath"]},
                "seasonal": {"color": "#5F27CD", "items": ["holiday", "outdoor", "garden"]},
                "essentials": {"color": "#00D2D3", "items": ["health", "beauty", "cleaning"]}
            }
        }
        
        # Generate shelves in department-style layout
        # Apparel zone (left side)
        for x in range(1, 5):
            for y in range(1, 7):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "apparel",
                    "capacity": 110,
                    "current_items": np.random.randint(22, 95),
                    "seasonal": False
                })
        
        # Home zone (right side)
        for x in range(11, 15):
            for y in range(1, 7):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "home",
                    "capacity": 95,
                    "current_items": np.random.randint(19, 80),
                    "seasonal": False
                })
        
        # Seasonal zone (middle top)
        for x in range(6, 10):
            for y in range(1, 5):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "seasonal",
                    "capacity": 130,
                    "current_items": np.random.randint(26, 110),
                    "seasonal": True
                })
        
        # Essentials zone (middle bottom)
        for x in range(6, 10):
            for y in range(6, 10):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "essentials",
                    "capacity": 85,
                    "current_items": np.random.randint(17, 70),
                    "seasonal": False
                })
        
        # Packing stations
        layout["stations"] = [
            {"x": 2, "y": 12, "type": "standard", "capacity": 45},
            {"x": 6, "y": 12, "type": "express", "capacity": 30},
            {"x": 10, "y": 12, "type": "standard", "capacity": 45},
            {"x": 14, "y": 12, "type": "bulk", "capacity": 80}
        ]
        
        return layout
    
    def generate_costco_style_layout(self) -> Dict:
        """Generate a Costco-style warehouse layout"""
        layout = {
            "name": "Costco Wholesale Warehouse",
            "description": "Bulk wholesale warehouse with large item storage",
            "grid_width": 22,
            "grid_height": 16,
            "layout_type": "Costco Style",
            "shelves": [],
            "stations": [],
            "entry_exit": {"x": 11, "y": 15},
            "zones": {
                "bulk_goods": {"color": "#FF6B6B", "items": ["paper_products", "cleaning_supplies", "beverages"]},
                "electronics": {"color": "#4ECDC4", "items": ["tvs", "computers", "appliances"]},
                "food": {"color": "#45B7D1", "items": ["frozen_foods", "dairy", "meat", "produce"]},
                "clothing": {"color": "#96CEB4", "items": ["casual_wear", "work_wear", "seasonal"]}
            }
        }
        
        # Generate shelves optimized for bulk storage
        # Bulk goods zone (large area)
        for x in range(2, 10):
            for y in range(2, 8):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "bulk_goods",
                    "capacity": 300,
                    "current_items": np.random.randint(60, 250),
                    "bulk_storage": True
                })
        
        # Electronics zone
        for x in range(12, 18):
            for y in range(2, 6):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "electronics",
                    "capacity": 150,
                    "current_items": np.random.randint(30, 120),
                    "bulk_storage": False
                })
        
        # Food zone
        for x in range(2, 10):
            for y in range(9, 13):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "food",
                    "capacity": 200,
                    "current_items": np.random.randint(40, 170),
                    "bulk_storage": True,
                    "refrigerated": True
                })
        
        # Clothing zone
        for x in range(12, 18):
            for y in range(7, 11):
                layout["shelves"].append({
                    "x": x, "y": y,
                    "zone": "clothing",
                    "capacity": 120,
                    "current_items": np.random.randint(24, 100),
                    "bulk_storage": False
                })
        
        # Packing stations for bulk orders
        layout["stations"] = [
            {"x": 4, "y": 14, "type": "bulk", "capacity": 150},
            {"x": 8, "y": 14, "type": "standard", "capacity": 60},
            {"x": 12, "y": 14, "type": "bulk", "capacity": 150},
            {"x": 16, "y": 14, "type": "express", "capacity": 40}
        ]
        
        return layout
    
    def save_sample_layouts(self):
        """Save all sample layouts to JSON files"""
        self.create_sample_data_directory()
        
        layouts = {
            'walmart_style': self.generate_walmart_style_layout(),
            'amazon_style': self.generate_amazon_style_layout(),
            'target_style': self.generate_target_style_layout(),
            'costco_style': self.generate_costco_style_layout()
        }
        
        for name, layout in layouts.items():
            filename = f"sample_data/{name}_warehouse.json"
            with open(filename, 'w') as f:
                json.dump(layout, f, indent=2)
            st.success(f"✅ Saved {layout['name']} layout to {filename}")
    
    def load_layout_from_json(self, filepath: str) -> Optional[Dict]:
        """Load warehouse layout from JSON file"""
        try:
            with open(filepath, 'r') as f:
                layout_data = json.load(f)
            return layout_data
        except FileNotFoundError:
            st.error(f"❌ File not found: {filepath}")
            return None
        except json.JSONDecodeError:
            st.error(f"❌ Invalid JSON format in: {filepath}")
            return None
    
    def convert_to_grid_format(self, layout_data: Dict) -> Dict:
        """Convert layout data to the grid format used in layout.py"""
        grid_width = layout_data.get('grid_width', 12)
        grid_height = layout_data.get('grid_height', 10)
        
        # Initialize empty grid
        grid_data = []
        for y in range(grid_height):
            for x in range(grid_width):
                grid_data.append({
                    'x': x, 'y': y, 'type': 'Empty', 'color': 'white', 'symbol': 'square'
                })
        
        # Add shelves
        for shelf in layout_data.get('shelves', []):
            x, y = shelf['x'], shelf['y']
            zone = shelf.get('zone', 'general')
            zone_color = layout_data.get('zones', {}).get(zone, {}).get('color', 'brown')
            
            # Find and update the grid cell
            for cell in grid_data:
                if cell['x'] == x and cell['y'] == y:
                    cell.update({
                        'type': 'Shelf',
                        'color': zone_color,
                        'symbol': 'square',
                        'zone': zone,
                        'capacity': shelf.get('capacity', 100),
                        'current_items': shelf.get('current_items', 50)
                    })
                    break
        
        # Add packing stations
        for station in layout_data.get('stations', []):
            x, y = station['x'], station['y']
            
            for cell in grid_data:
                if cell['x'] == x and cell['y'] == y:
                    cell.update({
                        'type': 'Packing Station',
                        'color': 'green',
                        'symbol': 'diamond',
                        'station_type': station.get('type', 'standard'),
                        'capacity': station.get('capacity', 50)
                    })
                    break
        
        # Add entry/exit point
        entry_exit = layout_data.get('entry_exit', {'x': 0, 'y': 0})
        x, y = entry_exit['x'], entry_exit['y']
        
        for cell in grid_data:
            if cell['x'] == x and cell['y'] == y:
                cell.update({
                    'type': 'Entry/Exit',
                    'color': 'blue',
                    'symbol': 'circle'
                })
                break
        
        return {
            'grid_width': grid_width,
            'grid_height': grid_height,
            'grid_data': grid_data,
            'layout_name': layout_data.get('name', 'Unknown Layout'),
            'layout_description': layout_data.get('description', ''),
            'layout_type': layout_data.get('layout_type', 'Custom'),
            'zones': layout_data.get('zones', {})
        }
    
    def load_and_convert_layout(self, layout_name: str) -> Optional[Dict]:
        """Load and convert a specific layout to grid format"""
        if layout_name not in self.sample_layouts:
            st.error(f"❌ Unknown layout: {layout_name}")
            return None
        
        filepath = self.sample_layouts[layout_name]
        layout_data = self.load_layout_from_json(filepath)
        
        if layout_data:
            return self.convert_to_grid_format(layout_data)
        return None
    
    def get_available_layouts(self) -> List[str]:
        """Get list of available layout names"""
        return list(self.sample_layouts.keys())
    
    def display_layout_info(self, layout_name: str):
        """Display information about a specific layout"""
        layout_data = self.load_layout_from_json(self.sample_layouts[layout_name])
        if layout_data:
            st.markdown(f"### {layout_data['name']}")
            st.markdown(f"**Description:** {layout_data['description']}")
            st.markdown(f"**Grid Size:** {layout_data['grid_width']} x {layout_data['grid_height']}")
            st.markdown(f"**Shelves:** {len(layout_data['shelves'])}")
            st.markdown(f"**Stations:** {len(layout_data['stations'])}")
            
            if 'zones' in layout_data:
                st.markdown("**Zones:**")
                for zone_name, zone_info in layout_data['zones'].items():
                    st.markdown(f"- **{zone_name.title()}**: {', '.join(zone_info['items'])}")

def load_sample_warehouse_data():
    """Main function to load and display sample warehouse data"""
    loader = WarehouseDataLoader()
    
    st.markdown("### 🏪 Sample Warehouse Layouts")
    st.markdown("Load pre-configured warehouse layouts from major retailers")
    
    # Create sample data if it doesn't exist
    if not os.path.exists('sample_data'):
        if st.button("📁 Generate Sample Data"):
            loader.save_sample_layouts()
            loader.save_sample_orders()
    
    # Layout selection
    available_layouts = loader.get_available_layouts()
    selected_layout = st.selectbox(
        "Choose a warehouse layout:",
        available_layouts,
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    if selected_layout:
        # Display layout information
        loader.display_layout_info(selected_layout)
        
        # Load and convert layout
        if st.button("🔄 Load Layout"):
            grid_data = loader.load_and_convert_layout(selected_layout)
            if grid_data:
                # Update session state with the loaded layout
                st.session_state['grid_width'] = grid_data['grid_width']
                st.session_state['grid_height'] = grid_data['grid_height']
                st.session_state['layout_type'] = grid_data['layout_type']
                
                # Update custom layout state if it exists
                if 'custom_layout_state' not in st.session_state:
                    st.session_state.custom_layout_state = {}
                
                st.session_state.custom_layout_state.update({
                    'grid_data': grid_data['grid_data'],
                    'shelves': [cell for cell in grid_data['grid_data'] if cell['type'] == 'Shelf'],
                    'stations': [cell for cell in grid_data['grid_data'] if cell['type'] == 'Packing Station'],
                    'entry_exit': next((cell for cell in grid_data['grid_data'] if cell['type'] == 'Entry/Exit'), None)
                })
                
                st.success(f"✅ Loaded {grid_data['layout_name']} successfully!")
                st.rerun()

if __name__ == "__main__":
    # Test the module
    loader = WarehouseDataLoader()
    loader.save_sample_layouts()
    loader.save_sample_orders()
    print("Sample warehouse layouts and orders generated successfully!") 