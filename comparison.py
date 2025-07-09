import streamlit as st
from metrics import calculate_efficiency_score

def capture_current_metrics():
    """Capture current metrics as 'before' optimization"""
    if 'realtime_metrics' in st.session_state:
        metrics = st.session_state.realtime_metrics.copy()
        total_orders = st.session_state.get('num_orders', 50)
        
        # Calculate efficiency score
        efficiency_score = calculate_efficiency_score(
            metrics['average_pick_time'],
            metrics['total_distance'],
            metrics['orders_completed'],
            total_orders
        )
        
        # Store as before metrics
        st.session_state['before_metrics'] = {
            'average_pick_time': metrics['average_pick_time'],
            'orders_completed': metrics['orders_completed'],
            'total_distance': metrics['total_distance'],
            'efficiency_score': efficiency_score
        }
        return True
    return False

def capture_optimized_metrics():
    """Capture optimized metrics as 'after' optimization"""
    if 'realtime_metrics' in st.session_state:
        metrics = st.session_state.realtime_metrics.copy()
        total_orders = st.session_state.get('num_orders', 50)
        
        # Calculate efficiency score
        efficiency_score = calculate_efficiency_score(
            metrics['average_pick_time'],
            metrics['total_distance'],
            metrics['orders_completed'],
            total_orders
        )
        
        # Store as after metrics
        st.session_state['after_metrics'] = {
            'average_pick_time': metrics['average_pick_time'],
            'orders_completed': metrics['orders_completed'],
            'total_distance': metrics['total_distance'],
            'efficiency_score': efficiency_score
        }
        return True
    return False

def comparison_panel():
    """Display the AI Optimization Results comparison panel"""
    if 'before_metrics' not in st.session_state or 'after_metrics' not in st.session_state:
        return
    
    st.markdown("""
    <style>
    .comparison-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
    }
    .comparison-column {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin: 0.5rem 0;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #dee2e6;
    }
    .metric-row:last-child {
        border-bottom: none;
    }
    .metric-label {
        font-weight: bold;
        color: #495057;
    }
    .metric-value {
        font-size: 1.1rem;
        font-weight: bold;
    }
    .improvement-up {
        color: #28a745;
        font-weight: bold;
    }
    .improvement-down {
        color: #dc3545;
        font-weight: bold;
    }
    .improvement-neutral {
        color: #6c757d;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="comparison-header">🤖 AI Optimization Results</div>', unsafe_allow_html=True)
    
    before_metrics = st.session_state['before_metrics']
    after_metrics = st.session_state['after_metrics']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="comparison-column">', unsafe_allow_html=True)
        st.markdown('<h4 style="text-align: center; color: #495057;">📊 Before Optimization</h4>', unsafe_allow_html=True)
        
        # Average Pick Time
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Average Pick Time:</span>
            <span class="metric-value">{before_metrics['average_pick_time']:.1f}s</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Orders Completed
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Orders Completed:</span>
            <span class="metric-value">{before_metrics['orders_completed']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Total Distance
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Total Distance:</span>
            <span class="metric-value">{before_metrics['total_distance']:.0f}m</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Efficiency Score
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Efficiency Score:</span>
            <span class="metric-value">{before_metrics['efficiency_score']:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="comparison-column">', unsafe_allow_html=True)
        st.markdown('<h4 style="text-align: center; color: #495057;">🚀 After Optimization</h4>', unsafe_allow_html=True)
        
        # Calculate improvements
        pick_time_change = before_metrics['average_pick_time'] - after_metrics['average_pick_time']
        distance_change = before_metrics['total_distance'] - after_metrics['total_distance']
        efficiency_change = after_metrics['efficiency_score'] - before_metrics['efficiency_score']
        
        # Average Pick Time with improvement indicator
        if pick_time_change > 0:
            pick_time_indicator = f"<span class='improvement-up'>↑ {pick_time_change:.1f}s</span>"
        elif pick_time_change < 0:
            pick_time_indicator = f"<span class='improvement-down'>↓ {abs(pick_time_change):.1f}s</span>"
        else:
            pick_time_indicator = f"<span class='improvement-neutral'>→ 0s</span>"
        
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Average Pick Time:</span>
            <span class="metric-value">{after_metrics['average_pick_time']:.1f}s {pick_time_indicator}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Orders Completed
        orders_change = after_metrics['orders_completed'] - before_metrics['orders_completed']
        if orders_change > 0:
            orders_indicator = f"<span class='improvement-up'>↑ +{orders_change}</span>"
        elif orders_change < 0:
            orders_indicator = f"<span class='improvement-down'>↓ {orders_change}</span>"
        else:
            orders_indicator = f"<span class='improvement-neutral'>→ 0</span>"
        
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Orders Completed:</span>
            <span class="metric-value">{after_metrics['orders_completed']} {orders_indicator}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Total Distance with improvement indicator
        if distance_change > 0:
            distance_indicator = f"<span class='improvement-up'>↑ {distance_change:.0f}m</span>"
        elif distance_change < 0:
            distance_indicator = f"<span class='improvement-down'>↓ {abs(distance_change):.0f}m</span>"
        else:
            distance_indicator = f"<span class='improvement-neutral'>→ 0m</span>"
        
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Total Distance:</span>
            <span class="metric-value">{after_metrics['total_distance']:.0f}m {distance_indicator}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Efficiency Score with improvement indicator
        if efficiency_change > 0:
            efficiency_indicator = f"<span class='improvement-up'>↑ +{efficiency_change:.1f}%</span>"
        elif efficiency_change < 0:
            efficiency_indicator = f"<span class='improvement-down'>↓ {efficiency_change:.1f}%</span>"
        else:
            efficiency_indicator = f"<span class='improvement-neutral'>→ 0%</span>"
        
        st.markdown(f"""
        <div class="metric-row">
            <span class="metric-label">Efficiency Score:</span>
            <span class="metric-value">{after_metrics['efficiency_score']:.1f}% {efficiency_indicator}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Summary of improvements
    total_improvements = 0
    if pick_time_change > 0: total_improvements += 1
    if distance_change > 0: total_improvements += 1
    if efficiency_change > 0: total_improvements += 1
    
    if total_improvements >= 2:
        summary_color = "#28a745"
        summary_icon = "✅"
        summary_text = f"Excellent! {total_improvements}/3 metrics improved"
    elif total_improvements == 1:
        summary_color = "#ffc107"
        summary_icon = "⚠️"
        summary_text = f"Good! {total_improvements}/3 metrics improved"
    else:
        summary_color = "#dc3545"
        summary_icon = "❌"
        summary_text = f"Needs work! {total_improvements}/3 metrics improved"
    
    st.markdown(f"""
    <div style="background: {summary_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-top: 1rem;">
        <div style="font-size: 1.2rem; font-weight: bold;">
            {summary_icon} {summary_text}
        </div>
    </div>
    """, unsafe_allow_html=True) 