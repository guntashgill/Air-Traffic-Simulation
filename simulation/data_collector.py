import csv
from datetime import datetime
import os
import pandas as pd

class DataCollector:
    def __init__(self):
        self.routing_data = []
        self.demand_data = []
        self.battery_data = []
        self.anomaly_data = []
        
        self.routing_file = "data/routing_data.csv"
        self.demand_file = "data/demand_data.csv"
        self.battery_file = "data/battery_data.csv"
        self.anomaly_file = "data/anomaly_data.csv"
        
        self.create_files()
    
    def create_files(self):
        """Create data files with headers"""
        os.makedirs("data", exist_ok=True)
        
        # Routing data
        if not os.path.exists(self.routing_file):
            with open(self.routing_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'start_x', 'start_y', 'end_x', 'end_y',
                    'path_length', 'optimal_length', 'battery_start',
                    'battery_end', 'weather_impact'
                ])
        
        # Demand data
        if not os.path.exists(self.demand_file):
            with open(self.demand_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'actual_demand', 'predicted_demand',
                    'weather_impact', 'hour', 'day_of_week'
                ])
                
        # Battery data
        if not os.path.exists(self.battery_file):
            with open(self.battery_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'drone_id', 'distance', 'payload',
                    'wind_speed', 'weather_impact', 'actual_battery_used',
                    'predicted_battery_used'
                ])
                
        # Anomaly data
        if not os.path.exists(self.anomaly_file):
            with open(self.anomaly_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'drone_id', 'speed', 'battery_drain',
                    'payload', 'distance', 'is_anomaly'
                ])
    
    def record_routing(self, start, end, path, optimal_path, 
                      battery_start, battery_end, weather_impact):
        """Record routing performance data"""
        self.routing_data.append({
            'timestamp': datetime.now(),
            'start_x': start[0], 'start_y': start[1],
            'end_x': end[0], 'end_y': end[1],
            'path_length': len(path),
            'optimal_length': optimal_path,
            'battery_start': battery_start,
            'battery_end': battery_end,
            'weather_impact': weather_impact
        })
    
    def record_demand(self, actual_demand, predicted_demand, weather_impact):
        """Record demand prediction data"""
        now = datetime.now()
        self.demand_data.append({
            'timestamp': now,
            'actual_demand': actual_demand,
            'predicted_demand': predicted_demand,
            'weather_impact': weather_impact,
            'hour': now.hour,
            'day_of_week': now.weekday()
        })
    
    def record_battery(self, drone_id, distance, payload, wind_speed, 
                      weather_impact, actual_used, predicted_used):
        """Record battery performance data"""
        self.battery_data.append({
            'timestamp': datetime.now(),
            'drone_id': drone_id,
            'distance': distance,
            'payload': payload,
            'wind_speed': wind_speed,
            'weather_impact': weather_impact,
            'actual_battery_used': actual_used,
            'predicted_battery_used': predicted_used
        })
    
    def record_anomaly_features(self, drone):
        """Record features for anomaly detection"""
        self.anomaly_data.append({
            'timestamp': datetime.now(),
            'drone_id': drone.id,
            'speed': drone.speed,
            'battery_drain': drone.battery_decrease_rate,
            'payload': drone.payload,
            'distance': distance((drone.x, drone.y), drone.destination),
            'is_anomaly': 0  # Will be labeled during training
        })
    
    def save_all_data(self):
        """Save all collected data to files"""
        self.append_to_csv(self.routing_file, self.routing_data)
        self.append_to_csv(self.demand_file, self.demand_data)
        self.append_to_csv(self.battery_file, self.battery_data)
        self.append_to_csv(self.anomaly_file, self.anomaly_data)
        
        self.routing_data = []
        self.demand_data = []
        self.battery_data = []
        self.anomaly_data = []
    
    def append_to_csv(self, filename, data):
        """Append data to CSV file"""
        if not data:
            return
            
        with open(filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writerows(data)