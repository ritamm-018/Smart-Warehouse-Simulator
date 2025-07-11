import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import threading
from typing import Dict, List, Optional
import json
from utils.data_persistence import persistence

class APIIntegration:
    """Streamlit integration with the FastAPI order simulation backend"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Initialize session state for API integration
        if 'api_orders' not in st.session_state:
            st.session_state.api_orders = []
        if 'api_connection_status' not in st.session_state:
            st.session_state.api_connection_status = "disconnected"
        if 'api_last_update' not in st.session_state:
            st.session_state.api_last_update = None
        if 'api_stats' not in st.session_state:
            st.session_state.api_stats = {}
    
    def check_api_connection(self) -> bool:
        """Check if the API is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/", timeout=5)
            if response.status_code == 200:
                st.session_state.api_connection_status = "connected"
                return True
            else:
                st.session_state.api_connection_status = "error"
                return False
        except requests.exceptions.RequestException:
            st.session_state.api_connection_status = "disconnected"
            return False
    
    def get_api_stats(self) -> Dict:
        """Get API statistics"""
        try:
            response = self.session.get(f"{self.api_url}/api/stats", timeout=5)
            if response.status_code == 200:
                st.session_state.api_stats = response.json()
                return st.session_state.api_stats
            else:
                return {}
        except requests.exceptions.RequestException:
            return {}
    
    def get_available_layouts(self) -> List[str]:
        """Get available warehouse layouts from API"""
        try:
            response = self.session.get(f"{self.api_url}/api/layouts", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('layouts', [])
            else:
                return []
        except requests.exceptions.RequestException:
            return []
    
    def set_api_layout(self, layout_name: str) -> bool:
        """Set the warehouse layout in the API"""
        try:
            response = self.session.post(f"{self.api_url}/api/layout/{layout_name}", timeout=5)
            if response.status_code == 200:
                st.success(f"✅ API layout set to {layout_name}")
                return True
            else:
                st.error(f"❌ Failed to set API layout: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API connection error: {str(e)}")
            return False
    
    def fetch_new_orders(self) -> List[Dict]:
        """Fetch new orders from the API"""
        try:
            response = self.session.get(f"{self.api_url}/api/orders", timeout=5)
            if response.status_code == 200:
                data = response.json()
                new_orders = data.get('orders', [])
                
                # Convert orders to a more usable format
                processed_orders = []
                for order in new_orders:
                    processed_order = {
                        'order_id': order['order_id'],
                        'timestamp': order['order_timestamp'],
                        'status': order['status'],
                        'total_items': order['total_items'],
                        'estimated_pick_time': order['estimated_pick_time'],
                        'items': []
                    }
                    
                    for item in order['items']:
                        processed_order['items'].append({
                            'item_id': item['item_id'],
                            'shelf_x': item['shelf_location_x'],
                            'shelf_y': item['shelf_location_y'],
                            'zone': item['zone'],
                            'item_type': item['item_type'],
                            'priority': item['priority'],
                            'quantity': item['quantity']
                        })
                    
                    processed_orders.append(processed_order)
                
                # Add to session state
                st.session_state.api_orders.extend(processed_orders)
                st.session_state.api_last_update = datetime.now()
                
                # Save orders to data persistence if we have a current run
                if st.session_state.get('current_run_id'):
                    for order in processed_orders:
                        persistence.save_order(st.session_state.current_run_id, order)
                
                return processed_orders
            else:
                st.error(f"❌ Failed to fetch orders: {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API connection error: {str(e)}")
            return []
    
    def get_order_history(self, limit: int = 50) -> List[Dict]:
        """Get order history from API"""
        try:
            response = self.session.get(f"{self.api_url}/api/orders/history?limit={limit}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('orders', [])
            else:
                return []
        except requests.exceptions.RequestException:
            return []

def api_control_panel():
    """Streamlit control panel for API integration"""
    st.markdown("### 🔌 API Integration Control Panel")
    
    # Initialize API integration
    api = APIIntegration()
    
    # Connection status
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Check API Connection"):
            if api.check_api_connection():
                st.success("✅ API Connected")
            else:
                st.error("❌ API Not Available")
    
    with col2:
        if st.button("📊 Get API Stats"):
            stats = api.get_api_stats()
            if stats:
                st.success("✅ Stats Retrieved")
            else:
                st.error("❌ Failed to get stats")
    
    with col3:
        if st.button("🔄 Fetch New Orders"):
            new_orders = api.fetch_new_orders()
            if new_orders:
                st.success(f"✅ Fetched {len(new_orders)} orders")
            else:
                st.error("❌ Failed to fetch orders")
    
    # Display connection status
    status_color = {
        "connected": "🟢",
        "disconnected": "🔴", 
        "error": "🟡"
    }
    st.markdown(f"**API Status:** {status_color.get(st.session_state.api_connection_status, '⚪')} {st.session_state.api_connection_status.title()}")
    
    # Layout selection for API
    st.markdown("---")
    st.markdown("#### 🏗️ API Layout Configuration")
    
    available_layouts = api.get_available_layouts()
    if available_layouts:
        selected_layout = st.selectbox(
            "Select API Warehouse Layout:",
            available_layouts,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if st.button("🎯 Set API Layout"):
            api.set_api_layout(selected_layout)
    else:
        st.warning("⚠️ No layouts available from API")
    
    # API Statistics
    if st.session_state.api_stats:
        st.markdown("---")
        st.markdown("#### 📈 API Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Orders", st.session_state.api_stats.get('total_orders_generated', 0))
        with col2:
            st.metric("Current Layout", st.session_state.api_stats.get('current_layout', 'Unknown').replace('_', ' ').title())
        with col3:
            st.metric("Orders in History", st.session_state.api_stats.get('orders_in_history', 0))
        with col4:
            last_time = st.session_state.api_stats.get('last_order_time', 'Never')
            if last_time != 'Never':
                last_time = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                st.metric("Last Order", last_time.strftime('%H:%M:%S'))

def real_time_orders_display():
    """Display real-time orders from API"""
    st.markdown("### 📦 Real-Time Orders from API")
    
    api = APIIntegration()
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("🔄 Enable Auto-Refresh (every 10 seconds)", value=False)
    
    if auto_refresh:
        # Use st.empty() for real-time updates
        orders_container = st.empty()
        
        # This would need to be implemented with a background thread
        # For now, we'll show the current orders
        if st.session_state.api_orders:
            display_orders_table(st.session_state.api_orders)
        else:
            st.info("📭 No orders received yet. Click 'Fetch New Orders' to get started.")
    
    else:
        # Manual display
        if st.session_state.api_orders:
            display_orders_table(st.session_state.api_orders)
        else:
            st.info("📭 No orders received yet. Click 'Fetch New Orders' to get started.")
    
    # Last update info
    if st.session_state.api_last_update:
        st.caption(f"Last updated: {st.session_state.api_last_update.strftime('%H:%M:%S')}")

def display_orders_table(orders: List[Dict]):
    """Display orders in a formatted table"""
    if not orders:
        st.info("📭 No orders to display")
        return
    
    # Create a DataFrame for display
    display_data = []
    for order in orders[-20:]:  # Show last 20 orders
        # Handle different order formats (API vs processed)
        order_id = order.get('order_id', 'Unknown')
        timestamp = order.get('timestamp', order.get('order_timestamp', 'Unknown'))
        status = order.get('status', 'Unknown')
        estimated_pick_time = order.get('estimated_pick_time', 0)
        
        # Handle items - could be in different formats
        items = order.get('items', [])
        if not items:
            # If no items, create a placeholder row
            display_data.append({
                'Order ID': order_id,
                'Timestamp': timestamp,
                'Item ID': 'No items',
                'Zone': 'N/A',
                'Type': 'N/A',
                'Shelf (X,Y)': 'N/A',
                'Priority': 'N/A',
                'Quantity': 'N/A',
                'Status': status,
                'Est. Pick Time': f"{estimated_pick_time:.1f}s"
            })
        else:
            for item in items:
                # Handle different item formats
                item_id = item.get('item_id', 'Unknown')
                zone = item.get('zone', 'Unknown')
                item_type = item.get('item_type', 'Unknown')
                shelf_x = item.get('shelf_x', item.get('shelf_location_x', 0))
                shelf_y = item.get('shelf_y', item.get('shelf_location_y', 0))
                priority = item.get('priority', 1)
                quantity = item.get('quantity', 1)
                
                display_data.append({
                    'Order ID': order_id,
                    'Timestamp': timestamp,
                    'Item ID': item_id,
                    'Zone': zone,
                    'Type': item_type,
                    'Shelf (X,Y)': f"({shelf_x}, {shelf_y})",
                    'Priority': priority,
                    'Quantity': quantity,
                    'Status': status,
                    'Est. Pick Time': f"{estimated_pick_time:.1f}s"
                })
    
    if display_data:
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Orders", len(orders))
        with col2:
            total_items = sum(len(order.get('items', [])) for order in orders)
            st.metric("Total Items", total_items)
        with col3:
            # Calculate average priority safely
            priorities = []
            for order in orders:
                items = order.get('items', [])
                for item in items:
                    priority = item.get('priority', 1)
                    priorities.append(priority)
            
            avg_priority = sum(priorities) / max(1, len(priorities)) if priorities else 0
            st.metric("Avg Priority", f"{avg_priority:.1f}")
        with col4:
            # Calculate average pick time safely
            pick_times = [order.get('estimated_pick_time', 0) for order in orders]
            avg_pick_time = sum(pick_times) / max(1, len(pick_times))
            st.metric("Avg Pick Time", f"{avg_pick_time:.1f}s")

def api_orders_tab():
    """Main tab for API orders integration"""
    st.markdown("## 🔌 Real-Time Order API Integration")
    
    # Create tabs for different features
    tab1, tab2, tab3 = st.tabs(["🎛️ Control Panel", "📦 Real-Time Orders", "📊 Order History"])
    
    with tab1:
        api_control_panel()
    
    with tab2:
        real_time_orders_display()
    
    with tab3:
        st.markdown("### 📊 Order History")
        api = APIIntegration()
        
        limit = st.slider("Number of orders to display", 10, 200, 50)
        
        if st.button("📥 Load Order History"):
            history = api.get_order_history(limit)
            if history:
                st.success(f"✅ Loaded {len(history)} orders from history")
                # Display history in a similar format
                display_orders_table(history)
            else:
                st.warning("⚠️ No order history available") 