import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from .rl_agent import RLAgent
from .demand_predictor import DemandPredictor

class MLModel:
    def __init__(self, grid_size=(30, 20)):
        self.demand_predictor = DemandPredictor()
        self.rl_agent = RLAgent(grid_size)
        self.battery_model = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        
    def load_models(self):
        """Load all trained models"""
        self.demand_predictor.load_model()
        self.rl_agent.load_model()
        
        if os.path.exists("models/battery_model.pkl"):
            self.battery_model = joblib.load("models/battery_model.pkl")
            
        if os.path.exists("models/anomaly_detector.pkl"):
            self.anomaly_detector = joblib.load("models/anomaly_detector.pkl")
            
        return True
    
    def train_demand_model(self, data_file):
        """Train demand forecasting model"""
        return self.demand_predictor.train_model(data_file)
    
    def train_rl_agent(self, num_episodes=10000):
        """Train RL agent (should be done separately)"""
        # This would be implemented in a separate training script
        print("RL training should be done via train_rl.py script")
        return 0.0
    
    def get_optimized_route(self, start, end, battery, city):
        """Get RL-optimized route"""
        return self.rl_agent.get_path(start, end, battery, city)
    
    def train_battery_model(self, data_file):
        """Train battery prediction model"""
        df = pd.read_csv(data_file)
        X = df[['distance', 'payload', 'wind_speed', 'weather_impact']]
        y = df['battery_used']
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Train model
        self.battery_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.battery_model.fit(X, y)
        
        # Save model
        joblib.dump(self.battery_model, "models/battery_model.pkl")
        return self.battery_model.score(X, y)
    
    def predict_battery_usage(self, distance, payload, wind_speed, weather_impact):
        """Predict battery usage for a route"""
        if self.battery_model:
            features = np.array([[distance, payload, wind_speed, weather_impact]])
            scaled_features = self.scaler.transform(features)
            return self.battery_model.predict(scaled_features)[0]
        return distance * 0.1  # Default estimate
    
    def train_anomaly_detector(self, data_file):
        """Train anomaly detection model"""
        df = pd.read_csv(data_file)
        features = df[['speed', 'battery_drain', 'payload', 'distance']]
        
        # Train model
        self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
        self.anomaly_detector.fit(features)
        
        # Save model
        joblib.dump(self.anomaly_detector, "models/anomaly_detector.pkl")
        return self.anomaly_detector
    
    def detect_anomalies(self, drones):
        """Detect anomalous drones using ML model"""
        if not self.anomaly_detector:
            return []
            
        anomalies = []
        for drone in drones:
            # Create feature vector
            features = np.array([[
                drone.speed,
                drone.battery_decrease_rate,
                drone.payload,
                distance((drone.x, drone.y), (drone.destination[0], drone.destination[1]))
            ]])
            
            # Predict anomaly
            prediction = self.anomaly_detector.predict(features)
            if prediction[0] == -1:  # Anomaly detected
                anomalies.append(f"Drone {drone.id} - Anomalous behavior detected")
                
        return anomalies
    
    def predict_demand(self, historical_data, current_weather):
        """Predict package demand"""
        return self.demand_predictor.predict_demand(historical_data, current_weather)