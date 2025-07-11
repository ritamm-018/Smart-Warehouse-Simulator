from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import random
import time
from datetime import datetime, timedelta
import uvicorn
import json
import os

app = FastAPI(title="Warehouse Order API", description="Real-time order simulation for warehouse management")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for order data
class OrderItem(BaseModel):
    item_id: str
    shelf_location_x: int
    shelf_location_y: int
    zone: str
    item_type: str
    priority: int
    quantity: int

class Order(BaseModel):
    order_id: str
    items: List[OrderItem]
    order_timestamp: datetime
    status: str = "pending"
    total_items: int = 0
    estimated_pick_time: float = 0.0

class OrderResponse(BaseModel):
    orders: List[Order]
    timestamp: datetime
    total_orders: int

# Global state for order simulation
class OrderSimulator:
    def __init__(self):
        self.order_counter = 0
        self.last_order_time = datetime.now()
        self.warehouse_layouts = {
            'walmart_style': {
                'zones': {
                    'electronics': {'items': ['laptops', 'phones', 'tablets'], 'shelves': [(x, y) for x in range(2, 8) for y in range(2, 6)]},
                    'clothing': {'items': ['shirts', 'pants', 'shoes'], 'shelves': [(x, y) for x in range(12, 18) for y in range(2, 6)]},
                    'groceries': {'items': ['canned_goods', 'frozen_foods', 'produce'], 'shelves': [(x, y) for x in range(2, 8) for y in range(7, 11)]},
                    'home': {'items': ['furniture', 'appliances', 'decor'], 'shelves': [(x, y) for x in range(12, 18) for y in range(7, 11)]}
                }
            },
            'amazon_style': {
                'zones': {
                    'books': {'items': ['fiction', 'non_fiction', 'textbooks'], 'shelves': [(x, y) for x in range(1, 7) for y in range(1, 5)]},
                    'electronics': {'items': ['computers', 'accessories', 'gaming'], 'shelves': [(x, y) for x in range(11, 17) for y in range(1, 5)]},
                    'fashion': {'items': ['clothing', 'jewelry', 'watches'], 'shelves': [(x, y) for x in range(1, 7) for y in range(6, 10)]},
                    'home': {'items': ['kitchen', 'bathroom', 'bedroom'], 'shelves': [(x, y) for x in range(11, 17) for y in range(6, 10)]}
                }
            },
            'target_style': {
                'zones': {
                    'apparel': {'items': ['men', 'women', 'kids', 'accessories'], 'shelves': [(x, y) for x in range(1, 5) for y in range(1, 7)]},
                    'home': {'items': ['furniture', 'decor', 'kitchen', 'bath'], 'shelves': [(x, y) for x in range(11, 15) for y in range(1, 7)]},
                    'seasonal': {'items': ['holiday', 'outdoor', 'garden'], 'shelves': [(x, y) for x in range(6, 10) for y in range(1, 5)]},
                    'essentials': {'items': ['health', 'beauty', 'cleaning'], 'shelves': [(x, y) for x in range(6, 10) for y in range(6, 10)]}
                }
            },
            'costco_style': {
                'zones': {
                    'bulk_goods': {'items': ['paper_products', 'cleaning_supplies', 'beverages'], 'shelves': [(x, y) for x in range(2, 10) for y in range(2, 8)]},
                    'electronics': {'items': ['tvs', 'computers', 'appliances'], 'shelves': [(x, y) for x in range(12, 18) for y in range(2, 6)]},
                    'food': {'items': ['frozen_foods', 'dairy', 'meat', 'produce'], 'shelves': [(x, y) for x in range(2, 10) for y in range(9, 13)]},
                    'clothing': {'items': ['casual_wear', 'work_wear', 'seasonal'], 'shelves': [(x, y) for x in range(12, 18) for y in range(7, 11)]}
                }
            }
        }
        self.current_layout = 'walmart_style'
        self.order_history = []
        self.max_history = 1000  # Keep last 1000 orders

    def set_layout(self, layout_name: str):
        """Set the current warehouse layout for order generation"""
        if layout_name in self.warehouse_layouts:
            self.current_layout = layout_name
            return {"message": f"Layout changed to {layout_name}"}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown layout: {layout_name}")

    def generate_order(self) -> Order:
        """Generate a single realistic order"""
        self.order_counter += 1
        order_id = f"API_ORD_{self.order_counter:06d}"
        
        # Get current layout zones
        zones = self.warehouse_layouts[self.current_layout]['zones']
        
        # Generate 1-5 items per order
        num_items = random.randint(1, 5)
        items = []
        
        # Select random zones for this order
        selected_zones = random.sample(list(zones.keys()), min(num_items, len(zones)))
        
        for i in range(num_items):
            zone_name = selected_zones[i % len(selected_zones)]
            zone_data = zones[zone_name]
            
            # Select random item type and shelf
            item_type = random.choice(zone_data['items'])
            shelf_x, shelf_y = random.choice(zone_data['shelves'])
            
            # Generate item ID
            item_id = f"{zone_name}_{item_type}_{shelf_x}_{shelf_y}"
            
            # Create order item
            item = OrderItem(
                item_id=item_id,
                shelf_location_x=shelf_x,
                shelf_location_y=shelf_y,
                zone=zone_name,
                item_type=item_type,
                priority=random.randint(1, 3),  # 1=low, 2=medium, 3=high
                quantity=random.randint(1, 3)
            )
            items.append(item)
        
        # Calculate estimated pick time based on number of items and zones
        estimated_pick_time = len(items) * 30 + random.randint(10, 60)  # 30s per item + travel time
        
        order = Order(
            order_id=order_id,
            items=items,
            order_timestamp=datetime.now(),
            total_items=sum(item.quantity for item in items),
            estimated_pick_time=estimated_pick_time
        )
        
        # Add to history
        self.order_history.append(order)
        if len(self.order_history) > self.max_history:
            self.order_history.pop(0)
        
        return order

    def generate_orders_batch(self, min_orders: int = 1, max_orders: int = 5) -> List[Order]:
        """Generate a batch of new orders"""
        num_orders = random.randint(min_orders, max_orders)
        orders = []
        
        for _ in range(num_orders):
            order = self.generate_order()
            orders.append(order)
        
        return orders

# Global simulator instance
simulator = OrderSimulator()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Warehouse Order Simulation API",
        "version": "1.0.0",
        "endpoints": {
            "/api/orders": "Get new orders (1-5 every 10 seconds)",
            "/api/orders/history": "Get order history",
            "/api/layouts": "Get available layouts",
            "/api/layout/{layout_name}": "Set current layout"
        }
    }

@app.get("/api/orders", response_model=OrderResponse)
async def get_new_orders():
    """Get new orders - simulates real-time order inflow"""
    try:
        # Generate 1-5 new orders
        new_orders = simulator.generate_orders_batch(1, 5)
        
        return OrderResponse(
            orders=new_orders,
            timestamp=datetime.now(),
            total_orders=len(new_orders)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating orders: {str(e)}")

@app.get("/api/orders/history")
async def get_order_history(limit: int = 50):
    """Get recent order history"""
    try:
        recent_orders = simulator.order_history[-limit:] if limit > 0 else simulator.order_history
        return {
            "orders": recent_orders,
            "total_orders": len(simulator.order_history),
            "showing": len(recent_orders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving order history: {str(e)}")

@app.get("/api/layouts")
async def get_available_layouts():
    """Get available warehouse layouts"""
    return {
        "layouts": list(simulator.warehouse_layouts.keys()),
        "current_layout": simulator.current_layout
    }

@app.post("/api/layout/{layout_name}")
async def set_layout(layout_name: str):
    """Set the current warehouse layout"""
    try:
        result = simulator.set_layout(layout_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting layout: {str(e)}")

@app.get("/api/stats")
async def get_api_stats():
    """Get API statistics"""
    return {
        "total_orders_generated": simulator.order_counter,
        "current_layout": simulator.current_layout,
        "orders_in_history": len(simulator.order_history),
        "last_order_time": simulator.last_order_time.isoformat() if simulator.last_order_time else None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 