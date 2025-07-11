import simpy
from collections import deque
import numpy as np
import heapq

class Order:
    def __init__(self, order_id, items):
        self.order_id = order_id
        self.items = items  # List of (x, y) shelf locations

def a_star(start, goal, grid, width, height, cache=None):
    # Use cache if available
    if cache is not None:
        key = (start, goal)
        if key in cache:
            return cache[key]
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, [start]))
    closed_set = set()
    while open_set:
        est_total, cost, current, path = heapq.heappop(open_set)
        if current == goal:
            if cache is not None:
                cache[(start, goal)] = path
            return path
        if current in closed_set:
            continue
        closed_set.add(current)
        x, y = current
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx] == 1:  # 1 = blocked (shelf)
                    continue
                neighbor = (nx, ny)
                if neighbor in closed_set:
                    continue
                heapq.heappush(open_set, (cost+1+heuristic(neighbor, goal), cost+1, neighbor, path+[neighbor]))
    # No path found
    if cache is not None:
        cache[(start, goal)] = [start]
    return [start]

class Worker:
    def __init__(self, env, wid, entry_point, packing_stations, warehouse, stats, activity_map, grid, width, height, path_cache, decay_every=20):
        self.env = env
        self.wid = wid
        self.entry_point = entry_point
        self.packing_stations = packing_stations
        self.warehouse = warehouse
        self.stats = stats
        self.activity_map = activity_map
        self.grid = grid
        self.width = width
        self.height = height
        self.path_cache = path_cache
        self.process = env.process(self.run())
        self.order_queue = deque()
        self.idle = True
        self.decay_every = decay_every
        self.steps_since_decay = 0

    def assign_order(self, order):
        self.order_queue.append(order)
        if self.idle:
            self.env.process(self.run())

    def decay_congestion(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.activity_map[y][x] > 0:
                    self.activity_map[y][x] -= 1

    def run(self):
        self.idle = False
        while self.order_queue:
            order = self.order_queue.popleft()
            start_time = self.env.now
            pos = self.entry_point
            total_steps = 0
            # Go to each item's shelf
            for item in order.items:
                path = a_star(pos, item, self.grid, self.width, self.height, self.path_cache)
                for cell in path:
                    x, y = cell
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.activity_map[y][x] += 1
                        congestion = self.activity_map[y][x]
                        if congestion < 3:
                            yield self.env.timeout(1)
                        elif congestion < 6:
                            yield self.env.timeout(2)
                        else:
                            yield self.env.timeout(3)
                        total_steps += 1
                        self.steps_since_decay += 1
                        if self.steps_since_decay >= self.decay_every:
                            self.decay_congestion()
                            self.steps_since_decay = 0
                pos = item
                yield self.env.timeout(1)  # Pick item
            # Go to nearest packing station
            nearest_ps = min(self.packing_stations, key=lambda ps: abs(pos[0]-ps[0])+abs(pos[1]-ps[1]))
            path = a_star(pos, nearest_ps, self.grid, self.width, self.height, self.path_cache)
            for cell in path:
                x, y = cell
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.activity_map[y][x] += 1
                    congestion = self.activity_map[y][x]
                    if congestion < 3:
                        yield self.env.timeout(1)
                    elif congestion < 6:
                        yield self.env.timeout(2)
                    else:
                        yield self.env.timeout(3)
                    total_steps += 1
                    self.steps_since_decay += 1
                    if self.steps_since_decay >= self.decay_every:
                        self.decay_congestion()
                        self.steps_since_decay = 0
            pos = nearest_ps
            # Drop off (instant)
            pick_time = self.env.now - start_time
            self.stats['pick_times'].append(pick_time)
            self.stats['distances'].append(total_steps)
            self.stats['orders_completed'] += 1
        self.idle = True

try:
    from warehouse_state import warehouse_state
except ImportError:
    warehouse_state = {}

def run_simulation(config):
    """
    config: dict with keys:
        - grid_width, grid_height
        - shelf_positions: list of (x, y)
        - packing_stations: list of (x, y)
        - num_workers: int
        - orders: list of list of (x, y) (each order is a list of shelf locations)
        - shelves: list of dicts with x, y, type (optional, for type tracking)
    Returns: dict with avg pick time, total distance, orders completed, activity_map
    """
    env = simpy.Environment()
    stats = {
        'pick_times': [],
        'distances': [],
        'orders_completed': 0
    }
    grid_width = config['grid_width']
    grid_height = config['grid_height']
    # Build grid: 0 = free, 1 = blocked (shelf)
    grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
    for (x, y) in config['shelf_positions']:
        if 0 <= x < grid_width and 0 <= y < grid_height:
            grid[y][x] = 1
    activity_map = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
    path_cache = dict()
    workers = []
    entry_point = (0, 0)  # Default entry; could be parameterized
    for wid in range(config['num_workers']):
        workers.append(Worker(env, wid, entry_point, config['packing_stations'], config, stats, activity_map, grid, grid_width, grid_height, path_cache))
    # Assign orders round-robin
    order_objs = [Order(i, items) for i, items in enumerate(config['orders'])]
    for i, order in enumerate(order_objs):
        workers[i % len(workers)].assign_order(order)
    # --- ORDER HISTORY TRACKING ---
    # Build a lookup for (x, y) -> type
    shelf_type_lookup = {}
    shelves = config.get('shelves', [])
    for shelf in shelves:
        if isinstance(shelf, dict) and 'x' in shelf and 'y' in shelf and 'type' in shelf:
            shelf_type_lookup[(shelf['x'], shelf['y'])] = shelf['type']
    # For each order, for each item, append type to warehouse_state['order_history']
    if 'order_history' not in warehouse_state:
        warehouse_state['order_history'] = []
    for items in config['orders']:
        for item in items:
            t = shelf_type_lookup.get(tuple(item), None)
            if t:
                warehouse_state['order_history'].append(t)
    # Run until all orders are processed
    env.run()
    # Compute metrics
    total_orders = stats['orders_completed']
    avg_pick_time = sum(stats['pick_times']) / total_orders if total_orders else 0
    total_distance = sum(stats['distances'])
    return {
        'average_pick_time': avg_pick_time,
        'total_distance': total_distance,
        'orders_completed': total_orders,
        'activity_map': activity_map
    } 