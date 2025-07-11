import sqlite3
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import streamlit as st
import pickle
import hashlib

class WarehouseDataPersistence:
    """SQLite and Pandas-based data persistence for warehouse simulation"""
    
    def __init__(self, db_path: str = "warehouse_data.db"):
        self.db_path = db_path
        self.init_database()
        
        # Initialize session state for data tracking
        if 'simulation_runs' not in st.session_state:
            st.session_state.simulation_runs = []
        if 'current_run_id' not in st.session_state:
            st.session_state.current_run_id = None
        if 'auto_save_enabled' not in st.session_state:
            st.session_state.auto_save_enabled = True
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create warehouse layouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warehouse_layouts (
                layout_id TEXT PRIMARY KEY,
                layout_name TEXT NOT NULL,
                layout_type TEXT NOT NULL,
                grid_width INTEGER NOT NULL,
                grid_height INTEGER NOT NULL,
                layout_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create simulation runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulation_runs (
                run_id TEXT PRIMARY KEY,
                layout_id TEXT NOT NULL,
                run_name TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_seconds REAL,
                num_pickers INTEGER,
                num_orders INTEGER,
                items_per_order INTEGER,
                simulation_speed TEXT,
                status TEXT DEFAULT 'running',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (layout_id) REFERENCES warehouse_layouts (layout_id)
            )
        ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                order_timestamp TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                total_items INTEGER,
                estimated_pick_time REAL,
                actual_pick_time REAL,
                priority INTEGER,
                zone TEXT,
                shelf_x INTEGER,
                shelf_y INTEGER,
                item_type TEXT,
                quantity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES simulation_runs (run_id)
            )
        ''')
        
        # Create performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metric_unit TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES simulation_runs (run_id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_run_id ON orders (run_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_timestamp ON orders (order_timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_run_id ON performance_metrics (run_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_runs_layout_id ON simulation_runs (layout_id)')
        
        conn.commit()
        conn.close()
    
    def generate_run_id(self, layout_id: str) -> str:
        """Generate unique run ID based on layout and timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"run_{layout_id}_{timestamp}"
    
    def save_warehouse_layout(self, layout_data: Dict) -> str:
        """Save warehouse layout to database"""
        layout_id = self.generate_layout_id(layout_data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if layout already exists
        cursor.execute('SELECT layout_id FROM warehouse_layouts WHERE layout_id = ?', (layout_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing layout
            cursor.execute('''
                UPDATE warehouse_layouts 
                SET layout_name = ?, layout_type = ?, grid_width = ?, grid_height = ?, 
                    layout_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE layout_id = ?
            ''', (
                layout_data.get('layout_name', 'Unknown'),
                layout_data.get('layout_type', 'Custom'),
                layout_data.get('grid_width', 12),
                layout_data.get('grid_height', 10),
                json.dumps(layout_data),
                layout_id
            ))
        else:
            # Insert new layout
            cursor.execute('''
                INSERT INTO warehouse_layouts 
                (layout_id, layout_name, layout_type, grid_width, grid_height, layout_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                layout_id,
                layout_data.get('layout_name', 'Unknown'),
                layout_data.get('layout_type', 'Custom'),
                layout_data.get('grid_width', 12),
                layout_data.get('grid_height', 10),
                json.dumps(layout_data)
            ))
        
        conn.commit()
        conn.close()
        
        return layout_id
    
    def generate_layout_id(self, layout_data: Dict) -> str:
        """Generate unique layout ID based on layout content"""
        # Create a hash of the layout data for consistent ID generation
        layout_hash = hashlib.md5(json.dumps(layout_data, sort_keys=True).encode()).hexdigest()[:8]
        layout_type = layout_data.get('layout_type', 'custom')
        return f"{layout_type}_{layout_hash}"
    
    def start_simulation_run(self, layout_id: str, run_config: Dict) -> str:
        """Start a new simulation run and return run ID"""
        run_id = self.generate_run_id(layout_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO simulation_runs 
            (run_id, layout_id, run_name, start_time, num_pickers, num_orders, items_per_order, simulation_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            layout_id,
            run_config.get('run_name', f'Simulation {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
            datetime.now(),
            run_config.get('num_pickers', 3),
            run_config.get('num_orders', 50),
            run_config.get('items_per_order', 3),
            run_config.get('simulation_speed', 'Normal')
        ))
        
        conn.commit()
        conn.close()
        
        # Update session state
        st.session_state.current_run_id = run_id
        st.session_state.simulation_runs.append({
            'run_id': run_id,
            'layout_id': layout_id,
            'start_time': datetime.now(),
            'config': run_config
        })
        
        return run_id
    
    def end_simulation_run(self, run_id: str, final_metrics: Dict):
        """End a simulation run and save final metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        end_time = datetime.now()
        
        # Update run end time and duration
        cursor.execute('''
            UPDATE simulation_runs 
            SET end_time = ?, duration_seconds = ?, status = 'completed'
            WHERE run_id = ?
        ''', (end_time, (end_time - datetime.now()).total_seconds(), run_id))
        
        # Save final performance metrics
        for metric_name, metric_data in final_metrics.items():
            cursor.execute('''
                INSERT INTO performance_metrics (run_id, metric_name, metric_value, metric_unit)
                VALUES (?, ?, ?, ?)
            ''', (
                run_id,
                metric_name,
                metric_data.get('value', 0),
                metric_data.get('unit', '')
            ))
        
        conn.commit()
        conn.close()
        
        # Auto-save to file if enabled
        if st.session_state.auto_save_enabled:
            self.auto_save_run_data(run_id)
    
    def save_order(self, run_id: str, order_data: Dict):
        """Save individual order to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save main order
        cursor.execute('''
            INSERT OR REPLACE INTO orders 
            (order_id, run_id, order_timestamp, status, total_items, estimated_pick_time, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data.get('order_id', ''),
            run_id,
            order_data.get('timestamp', datetime.now()),
            order_data.get('status', 'pending'),
            order_data.get('total_items', 0),
            order_data.get('estimated_pick_time', 0),
            order_data.get('priority', 1)
        ))
        
        # Save individual items with unique IDs
        for i, item in enumerate(order_data.get('items', [])):
            item_id = f"{order_data.get('order_id', '')}_item_{i}"
            cursor.execute('''
                INSERT OR REPLACE INTO orders 
                (order_id, run_id, order_timestamp, status, total_items, estimated_pick_time, 
                 priority, zone, shelf_x, shelf_y, item_type, quantity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_id,
                run_id,
                order_data.get('timestamp', datetime.now()),
                'item',
                1,
                order_data.get('estimated_pick_time', 0),
                item.get('priority', 1),
                item.get('zone', ''),
                item.get('shelf_x', item.get('shelf_location_x', 0)),
                item.get('shelf_y', item.get('shelf_location_y', 0)),
                item.get('item_type', ''),
                item.get('quantity', 1)
            ))
        
        conn.commit()
        conn.close()
    
    def save_performance_metric(self, run_id: str, metric_name: str, value: float, unit: str = ''):
        """Save performance metric to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics (run_id, metric_name, metric_value, metric_unit)
            VALUES (?, ?, ?, ?)
        ''', (run_id, metric_name, value, unit))
        
        conn.commit()
        conn.close()
    
    def get_simulation_runs(self, limit: int = 50) -> List[Dict]:
        """Get recent simulation runs"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT r.run_id, r.run_name, r.start_time, r.end_time, r.duration_seconds,
                   r.num_pickers, r.num_orders, r.status, l.layout_name
            FROM simulation_runs r
            LEFT JOIN warehouse_layouts l ON r.layout_id = l.layout_id
            ORDER BY r.start_time DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        
        return df.to_dict('records')
    
    def get_run_orders(self, run_id: str) -> pd.DataFrame:
        """Get all orders for a specific run"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM orders 
            WHERE run_id = ? 
            ORDER BY order_timestamp
        '''
        
        df = pd.read_sql_query(query, conn, params=[run_id])
        conn.close()
        
        return df
    
    def get_run_metrics(self, run_id: str) -> pd.DataFrame:
        """Get performance metrics for a specific run"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT metric_name, metric_value, metric_unit, timestamp
            FROM performance_metrics 
            WHERE run_id = ? 
            ORDER BY timestamp
        '''
        
        df = pd.read_sql_query(query, conn, params=[run_id])
        conn.close()
        
        return df
    
    def get_layout_summary(self) -> pd.DataFrame:
        """Get summary of all layouts"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT l.layout_id, l.layout_name, l.layout_type, l.grid_width, l.grid_height,
                   l.created_at, l.updated_at,
                   COUNT(r.run_id) as num_runs
            FROM warehouse_layouts l
            LEFT JOIN simulation_runs r ON l.layout_id = r.layout_id
            GROUP BY l.layout_id
            ORDER BY l.created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def auto_save_run_data(self, run_id: str):
        """Auto-save run data to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create data directory if it doesn't exist
        data_dir = "simulation_data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Save orders
        orders_df = self.get_run_orders(run_id)
        if not orders_df.empty:
            orders_file = f"{data_dir}/orders_{run_id}_{timestamp}.csv"
            orders_df.to_csv(orders_file, index=False)
        
        # Save metrics
        metrics_df = self.get_run_metrics(run_id)
        if not metrics_df.empty:
            metrics_file = f"{data_dir}/metrics_{run_id}_{timestamp}.csv"
            metrics_df.to_csv(metrics_file, index=False)
        
        # Save run summary
        conn = sqlite3.connect(self.db_path)
        run_summary = pd.read_sql_query(
            'SELECT * FROM simulation_runs WHERE run_id = ?', 
            conn, params=[run_id]
        )
        conn.close()
        
        if not run_summary.empty:
            summary_file = f"{data_dir}/summary_{run_id}_{timestamp}.csv"
            run_summary.to_csv(summary_file, index=False)
    
    def export_all_data(self, format: str = 'csv') -> Dict[str, str]:
        """Export all data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = f"data_export_{timestamp}"
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        exported_files = {}
        
        # Export layouts
        layouts_df = self.get_layout_summary()
        layouts_file = f"{export_dir}/warehouse_layouts.{format}"
        layouts_df.to_csv(layouts_file, index=False)
        exported_files['layouts'] = layouts_file
        
        # Export simulation runs
        runs_df = pd.DataFrame(self.get_simulation_runs(1000))
        runs_file = f"{export_dir}/simulation_runs.{format}"
        runs_df.to_csv(runs_file, index=False)
        exported_files['runs'] = runs_file
        
        # Export all orders
        conn = sqlite3.connect(self.db_path)
        orders_df = pd.read_sql_query('SELECT * FROM orders ORDER BY created_at DESC', conn)
        conn.close()
        
        orders_file = f"{export_dir}/all_orders.{format}"
        orders_df.to_csv(orders_file, index=False)
        exported_files['orders'] = orders_file
        
        # Export all metrics
        conn = sqlite3.connect(self.db_path)
        metrics_df = pd.read_sql_query('SELECT * FROM performance_metrics ORDER BY timestamp DESC', conn)
        conn.close()
        
        metrics_file = f"{export_dir}/all_metrics.{format}"
        metrics_df.to_csv(metrics_file, index=False)
        exported_files['metrics'] = metrics_file
        
        return exported_files
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count layouts
        cursor.execute('SELECT COUNT(*) FROM warehouse_layouts')
        stats['total_layouts'] = cursor.fetchone()[0]
        
        # Count simulation runs
        cursor.execute('SELECT COUNT(*) FROM simulation_runs')
        stats['total_runs'] = cursor.fetchone()[0]
        
        # Count orders
        cursor.execute('SELECT COUNT(*) FROM orders')
        stats['total_orders'] = cursor.fetchone()[0]
        
        # Count metrics
        cursor.execute('SELECT COUNT(*) FROM performance_metrics')
        stats['total_metrics'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats

def data_persistence_ui():
    """Streamlit UI for data persistence management"""
    st.markdown("### Data Persistence Management")
    
    # Initialize persistence
    persistence = WarehouseDataPersistence()
    
    # Auto-save toggle
    col1, col2 = st.columns(2)
    with col1:
        auto_save = st.checkbox("🔄 Enable Auto-Save", value=st.session_state.auto_save_enabled)
        if auto_save != st.session_state.auto_save_enabled:
            st.session_state.auto_save_enabled = auto_save
            st.success("✅ Auto-save setting updated")
    
    with col2:
        if st.button("📊 Database Stats"):
            stats = persistence.get_database_stats()
            st.json(stats)
    
    # Data export section
    st.markdown("---")
    st.markdown("#### 📤 Data Export")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📁 Export All Data"):
            with st.spinner("Exporting data..."):
                exported_files = persistence.export_all_data()
                st.success("✅ Data exported successfully!")
                for file_type, file_path in exported_files.items():
                    st.write(f"**{file_type.title()}**: {file_path}")
    
    with col2:
        if st.button("🗑️ Clear Database"):
            if st.checkbox("I understand this will delete all data"):
                # This would implement database clearing
                st.warning("Database clearing not implemented for safety")
    
    # Simulation runs history
    st.markdown("---")
    st.markdown("#### 📋 Recent Simulation Runs")
    
    runs = persistence.get_simulation_runs(10)
    if runs:
        runs_df = pd.DataFrame(runs)
        st.dataframe(runs_df, use_container_width=True)
    else:
        st.info("📭 No simulation runs found")
    
    # Layout summary
    st.markdown("---")
    st.markdown("#### 🏗️ Warehouse Layouts")
    
    layouts_df = persistence.get_layout_summary()
    if not layouts_df.empty:
        st.dataframe(layouts_df, use_container_width=True)
    else:
        st.info("📭 No layouts found")

# Global persistence instance
persistence = WarehouseDataPersistence()

def save_current_layout():
    """Save current layout from session state"""
    if 'custom_layout_state' in st.session_state and st.session_state.custom_layout_state.get('grid_data'):
        layout_data = {
            'layout_name': st.session_state.get('layout_type', 'Custom Layout'),
            'layout_type': st.session_state.get('layout_type', 'Custom'),
            'grid_width': st.session_state.get('grid_width', 12),
            'grid_height': st.session_state.get('grid_height', 10),
            'grid_data': st.session_state.custom_layout_state['grid_data'],
            'shelves': st.session_state.custom_layout_state.get('shelves', []),
            'stations': st.session_state.custom_layout_state.get('stations', []),
            'entry_exit': st.session_state.custom_layout_state.get('entry_exit', None)
        }
        
        layout_id = persistence.save_warehouse_layout(layout_data)
        st.success(f"✅ Layout saved with ID: {layout_id}")
        return layout_id
    
    return None

def start_new_simulation():
    """Start a new simulation run"""
    layout_id = save_current_layout()
    if layout_id:
        run_config = {
            'run_name': f"Simulation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'num_pickers': st.session_state.get('num_pickers', 3),
            'num_orders': st.session_state.get('num_orders', 50),
            'items_per_order': st.session_state.get('items_per_order', 3),
            'simulation_speed': st.session_state.get('simulation_speed', 'Normal')
        }
        
        run_id = persistence.start_simulation_run(layout_id, run_config)
        st.success(f"✅ Simulation started with run ID: {run_id}")
        return run_id
    
    return None 