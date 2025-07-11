# Optimizer for warehouse layout based on order history demand

try:
    from warehouse_state import warehouse_state
except ImportError:
    warehouse_state = {}

from core.data_management import calculate_demand_distribution

def optimize_layout_by_demand():
    layout = warehouse_state.get('layout')
    if not layout or 'shelves' not in layout:
        return None
    shelves = layout['shelves']
    width = layout['width']
    height = layout['height']
    demand_profile = calculate_demand_distribution()
    # Sort shelves by demand (most ordered type first)
    sorted_shelves = sorted(shelves, key=lambda s: -demand_profile.get(s.get('type', ''), 0))
    # Place high-demand shelves near (0,0), low-demand further away
    # Fill grid row by row from (0,0)
    new_shelves = []
    idx = 0
    for y in range(height):
        for x in range(width):
            if idx < len(sorted_shelves):
                shelf = dict(sorted_shelves[idx])
                shelf['x'] = x
                shelf['y'] = y
                new_shelves.append(shelf)
                idx += 1
    optimized_layout = {
        'width': width,
        'height': height,
        'shelves': new_shelves
    }
    warehouse_state['optimization'] = {
        'optimized_layout': optimized_layout,
        'based_on_demand': demand_profile
    }
    return warehouse_state['optimization']

# Optional: Streamlit trigger
if __name__ == '__main__':
    import streamlit as st
    if st.button('Optimize with Order History'):
        result = optimize_layout_by_demand()
        if result:
            st.success('Layout optimized based on order demand!')
            st.json(result)
        else:
            st.error('No layout or order history available.') 