import numpy as np
import random
from collections import defaultdict
import joblib
import os

class RLAgent:
    def __init__(self, grid_size, learning_rate=0.1, discount_factor=0.95, 
                 exploration_rate=1.0, exploration_decay=0.995, min_exploration=0.01):
        self.grid_size = grid_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration = min_exploration
        self.q_table = defaultdict(lambda: np.zeros(8))  # 8 possible actions
        self.actions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Up, Right, Down, Left
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonals
        ]
        self.model_path = "models/routing_model.pkl"
        
    def state_to_key(self, state):
        """Convert state to hashable key"""
        drone_pos, target_pos, battery = state
        return (drone_pos[0], drone_pos[1], 
                target_pos[0], target_pos[1], 
                int(battery))
    
    def choose_action(self, state, valid_moves):
        """Choose action using epsilon-greedy strategy"""
        state_key = self.state_to_key(state)
        
        if random.random() < self.exploration_rate:
            # Exploration: choose random valid action
            return random.choice(valid_moves)
        else:
            # Exploitation: choose best known action
            q_values = self.q_table[state_key]
            # Only consider valid moves
            valid_q_values = [q_values[i] for i in valid_moves]
            if valid_q_values:
                best_index = np.argmax(valid_q_values)
                return valid_moves[best_index]
            return random.choice(valid_moves)  # Fallback
    
    def update_q_value(self, state, action, reward, next_state, next_valid_moves):
        """Update Q-table using Q-learning"""
        state_key = self.state_to_key(state)
        next_state_key = self.state_to_key(next_state)
        
        current_q = self.q_table[state_key][action]
        
        # Calculate max Q for next state
        if next_valid_moves:
            next_q_values = [self.q_table[next_state_key][a] for a in next_valid_moves]
            max_next_q = max(next_q_values) if next_q_values else 0
        else:
            max_next_q = 0
            
        # Update Q-value
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.q_table[state_key][action] = new_q
        
        # Decay exploration rate
        self.exploration_rate = max(self.min_exploration, 
                                   self.exploration_rate * self.exploration_decay)
    
    # Change the get_path method to:
    def get_path(self, start, end, battery, city):
        """Generate path using RL policy"""
        path = []
        current_pos = start
        battery_left = battery
        
        # Max steps to prevent infinite loops
        for _ in range(1000):
            if current_pos == end:
                break
                
            # Get valid moves
            valid_moves = []
            for i, action in enumerate(self.actions):
                new_pos = (current_pos[0] + action[0], current_pos[1] + action[1])
                if city.is_valid_position(int(new_pos[0]), int(new_pos[1])):
                    valid_moves.append(i)
            
            if not valid_moves:
                break
                
            # Get state
            state = (current_pos, end, battery_left)
            action_idx = self.choose_action(state, valid_moves)
            
            # Take action
            move = self.actions[action_idx]
            new_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
            
            # Add to path
            path.append(new_pos)
            current_pos = new_pos
            battery_left -= 0.5  # Battery cost per move
            
        return path
    
    def save_model(self):
        """Save Q-table to file"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(dict(self.q_table), self.model_path)
    
    def load_model(self):
        """Load Q-table from file"""
        if os.path.exists(self.model_path):
            q_table_dict = joblib.load(self.model_path)
            self.q_table = defaultdict(lambda: np.zeros(8), q_table_dict)
            self.exploration_rate = self.min_exploration  # Set to min for exploitation
            return True
        return False