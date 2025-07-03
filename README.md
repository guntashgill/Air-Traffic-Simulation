# Air-Traffic-Simulation
This project simulates a swarm of delivery drones operating in a city environment, 
with machine learning capabilities for optimized routing and demand forecasting.

## Features

- **City Simulation**: Grid-based city with buildings, roads, and obstacles
- **Drone Fleet Management**: 
  - Reinforcement learning-based pathfinding
  - Battery management
  - Charging station integration
- **Weather System**: Dynamic weather affecting drone performance
- **Smart Lockers**: Package delivery locations with capacity limits
- **Machine Learning Integration**:
  - **Reinforcement Learning (RL) Pathfinding**: Drones learn optimal routes over time
  - **LSTM Demand Forecasting**: Predicts package demand based on time and weather
- **Dashboard**: Real-time metrics and visualization

## Requirements

- Python 3.9+
- Pygame
- NumPy
- pandas
- scikit-learn
- TensorFlow
- joblib

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/swarm-delivery-simulation.git
cd swarm-delivery-simulation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt