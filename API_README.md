# 🔌 Real-Time Order API Integration

This project now includes a FastAPI backend that simulates real-time order inflow and integrates with the Streamlit frontend.

## 🚀 Quick Start

### Option 1: Start Both Services Together
```bash
python start_api_and_app.py
```

### Option 2: Start Services Separately

**Terminal 1 - Start FastAPI Backend:**
```bash
python api_backend.py
```
The API will be available at: http://localhost:8000

**Terminal 2 - Start Streamlit Frontend:**
```bash
streamlit run app.py
```
The app will be available at: http://localhost:8501

## 📋 API Endpoints

### Base URL: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/api/orders` | GET | Get new orders (1-5 every request) |
| `/api/orders/history` | GET | Get order history (limit parameter) |
| `/api/layouts` | GET | Get available warehouse layouts |
| `/api/layout/{layout_name}` | POST | Set current warehouse layout |
| `/api/stats` | GET | Get API statistics |

## 🏗️ Warehouse Layouts

The API supports 4 different warehouse layouts:

1. **Walmart Style** - Large-scale retail distribution
2. **Amazon Style** - High-tech fulfillment center
3. **Target Style** - Multi-category retail distribution
4. **Costco Style** - Bulk wholesale warehouse

Each layout has different zones, items, and shelf configurations.

## 📦 Order Structure

Each order contains:
- **Order ID**: Unique identifier (e.g., `API_ORD_000001`)
- **Items**: List of items to be picked
- **Timestamp**: When the order was created
- **Status**: Order status (pending, in_progress, completed)
- **Total Items**: Sum of all item quantities
- **Estimated Pick Time**: Calculated pick time in seconds

Each item contains:
- **Item ID**: Unique item identifier
- **Shelf Location**: X,Y coordinates
- **Zone**: Warehouse zone (electronics, clothing, etc.)
- **Item Type**: Specific product type
- **Priority**: 1-3 (low, medium, high)
- **Quantity**: Number of items to pick

## 🔌 Streamlit Integration

### New Tab: "Real-Time API"

The Streamlit app now includes a new tab with three sections:

#### 1. 🎛️ Control Panel
- **Check API Connection**: Verify API is running
- **Get API Stats**: View API statistics
- **Fetch New Orders**: Manually fetch orders
- **Layout Configuration**: Set warehouse layout in API

#### 2. 📦 Real-Time Orders
- **Auto-Refresh Toggle**: Enable automatic order fetching
- **Order Table**: Display incoming orders in real-time
- **Summary Metrics**: Total orders, items, priorities, pick times

#### 3. 📊 Order History
- **Load Order History**: Fetch historical orders from API
- **Configurable Limit**: Choose how many orders to display

## 🛠️ Installation

### Install API Dependencies
```bash
pip install -r api_requirements.txt
```

### Required Packages
- `fastapi==0.104.1`
- `uvicorn[standard]==0.24.0`
- `pydantic==2.5.0`
- `requests==2.31.0`
- `python-multipart==0.0.6`

## 🔧 Configuration

### API Configuration
- **Host**: 0.0.0.0 (accessible from any IP)
- **Port**: 8000
- **CORS**: Enabled for all origins (development)

### Streamlit Configuration
- **API URL**: http://localhost:8000 (configurable in `api_integration.py`)
- **Auto-refresh**: Every 10 seconds (configurable)

## 📊 API Statistics

The API tracks:
- **Total Orders Generated**: Running count of all orders
- **Current Layout**: Active warehouse layout
- **Orders in History**: Number of orders in memory
- **Last Order Time**: Timestamp of most recent order

## 🔄 Real-Time Features

### Order Generation
- **Frequency**: 1-5 orders per API call
- **Realistic Data**: Based on warehouse layout zones
- **Priority Distribution**: Random priority levels
- **Pick Time Calculation**: Based on items and zones

### Layout Synchronization
- **Dynamic Layouts**: Change warehouse layout via API
- **Zone-based Orders**: Orders respect current layout zones
- **Shelf Coordinates**: Items placed at valid shelf locations

## 🚨 Troubleshooting

### API Not Starting
1. Check if port 8000 is available
2. Verify all dependencies are installed
3. Check Python version compatibility

### Connection Issues
1. Ensure API is running on http://localhost:8000
2. Check firewall settings
3. Verify CORS configuration

### No Orders Appearing
1. Check API connection status
2. Verify layout is set in API
3. Try manual "Fetch New Orders" button

## 🔮 Future Enhancements

- **WebSocket Support**: Real-time order streaming
- **Order Status Updates**: Track order processing
- **Performance Metrics**: Pick time optimization
- **Multiple Warehouses**: Support for multiple locations
- **Order Prioritization**: Smart order queuing

## 📝 API Documentation

Once the API is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation and testing interface. 