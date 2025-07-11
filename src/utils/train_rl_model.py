from warehouse_env import WarehouseEnv
from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env

# Initialize environment
env = WarehouseEnv(grid_width=12, grid_height=10, num_orders=50, items_per_order=4)

# Optional: validate the environment
check_env(env, warn=True)

# Create DQN model
model = DQN(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=0.001,
    buffer_size=10000,
    learning_starts=1000,
    batch_size=64,
    gamma=0.95,
    train_freq=4,
    target_update_interval=250,
    exploration_fraction=0.3,
    exploration_final_eps=0.05,
    tensorboard_log="./rl_logs/"
)

# Train the model
model.learn(total_timesteps=10000)

# Save the model
model.save("optimized_warehouse_model")
print("✅ Model trained and saved as 'optimized_warehouse_model.zip'")

# Dependencies required:
# pip install stable-baselines3 gym 