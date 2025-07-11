import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class WarehouseEnv(gym.Env):
    def __init__(self, grid_width=12, grid_height=10, num_orders=50, items_per_order=4, initial_shelves=None):
        super(WarehouseEnv, self).__init__()
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.num_orders = num_orders
        self.items_per_order = items_per_order
        self.max_shelves = 20
        self.initial_shelves = initial_shelves

        # Action: Swap two shelf positions (encoded as a single int from 0 to n*n-1)
        self.action_space = spaces.Discrete(self.max_shelves ** 2)

        # Observation: Flattened layout representation (0 = empty, 1 = shelf)
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(self.grid_width * self.grid_height,), dtype=np.int32
        )

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.layout = np.zeros((self.grid_height, self.grid_width), dtype=np.int32)
        self.shelves = []
        if self.initial_shelves is not None:
            # Use provided shelves (list of (x, y) tuples)
            for x, y in self.initial_shelves:
                if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                    self.layout[y, x] = 1
                    self.shelves.append((x, y))
        else:
            placed = 0
            while placed < self.max_shelves:
                x, y = random.randint(1, self.grid_width - 2), random.randint(1, self.grid_height - 2)
                if self.layout[y, x] == 0:
                    self.layout[y, x] = 1
                    self.shelves.append((x, y))
                    placed += 1

        obs = self.layout.flatten()
        info = {}
        return obs, info

    def step(self, action):
        idx1 = action // self.max_shelves
        idx2 = action % self.max_shelves

        if idx1 < len(self.shelves) and idx2 < len(self.shelves):
            self.shelves[idx1], self.shelves[idx2] = self.shelves[idx2], self.shelves[idx1]

        self.layout.fill(0)
        for x, y in self.shelves:
            self.layout[y, x] = 1

        reward = -self._simulate_pick_time()

        # Gymnasium requires `terminated` and `truncated`
        terminated = True  # One-step episode
        truncated = False  # Not forcefully ended

        return self.layout.flatten(), reward, terminated, truncated, {}

    def _simulate_pick_time(self):
        # Fake estimation: more spread-out shelves = better performance
        spread = np.std([x for x, y in self.shelves]) + np.std([y for x, y in self.shelves])
        return 100 - spread * 10 