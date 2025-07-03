import numpy as np
from simulation.city import CityGrid
from simulation.rl_agent import RLAgent
import time

# Initialize city grid
city = CityGrid(30, 20)

# Initialize RL agent
rl_agent = RLAgent(grid_size=(30, 20))

# Training parameters
num_episodes = 10000
log_interval = 1000

# Start training
print("Starting RL training...")
start_time = time.time()

for episode in range(num_episodes):
    # Random start and end points
    start = (np.random.randint(0, 30), np.random.randint(0, 20))
    while not city.is_valid_position(start[0], start[1]):
        start = (np.random.randint(0, 30), np.random.randint(0, 20))
        
    end = (np.random.randint(0, 30), np.random.randint(0, 20))
    while not city.is_valid_position(end[0], end[1]) or end == start:
        end = (np.random.randint(0, 30), np.random.randint(0, 20))
    
    # Battery level (0-100)
    battery = np.random.randint(20, 100)
    
    # Generate path with RL
    path = rl_agent.get_path(start, end, battery, city)
    
    # Calculate optimal path length (Manhattan distance)
    optimal_length = abs(start[0]-end[0]) + abs(start[1]-end[1])
    
    # Update Q-values based on path performance
    # (In a real implementation, we'd update at each step)
    if path and path[-1] == end:
        reward = 100 - len(path)  # Reward efficient paths
    else:
        reward = -50  # Penalty for failure
        
    # Simplified update for this example
    # In a real implementation, we'd update at each step
    rl_agent.q_table[rl_agent.state_to_key((start, end, battery))] += reward
    
    # Log progress
    if (episode + 1) % log_interval == 0:
        print(f"Episode {episode+1}/{num_episodes} | "
              f"Exploration: {rl_agent.exploration_rate:.3f}")

# Save trained model
rl_agent.save_model()
print(f"Training completed in {time.time()-start_time:.2f} seconds")
print("Model saved to models/routing_model.pkl")