import random
import pygame
import numpy as np
from datetime import datetime
from .utils import *
from .ml_model import MLModel

class Warehouse:
    def __init__(self, x, y, id, city, area_population=1000):
        self.x = x
        self.y = y
        self.id = id
        self.packages = []
        self.color = WAREHOUSE_COLOR
        self.radius = 15
        self.area_population = area_population
        self.ml_model = MLModel()
        self.ml_model.load_models()
        self.historical_data = pd.DataFrame(columns=[
            'timestamp', 'demand', 'weather_impact'
        ])
        self.city = city
        self.valid_destinations = self.find_valid_destinations()
        
    def find_valid_destinations(self):
        """Find all valid delivery locations in the city"""
        destinations = []
        for i in range(self.city.width):
            for j in range(self.city.height):
                if self.city.is_valid_position(i, j):
                    destinations.append((i, j))
        return destinations
    
    def generate_packages(self, weather_impact):
        """Generate packages based on ML demand prediction"""
        current_time = datetime.now()
        
        # Add current demand to historical data
        new_row = pd.DataFrame([{
            'timestamp': current_time,
            'demand': len(self.packages),
            'weather_impact': weather_impact
        }])
        self.historical_data = pd.concat(
            [self.historical_data, new_row], ignore_index=True
        )
        
        # Predict demand
        predicted_demand = self.ml_model.predict_demand(
            self.historical_data, weather_impact
        )
        
        # Generate packages based on prediction
        num_packages = max(0, int(predicted_demand) - len(self.packages))
        for _ in range(num_packages):
            self.add_package()
    
    def add_package(self):
        # Add a new package with valid destination
        if self.valid_destinations:
            destination = random.choice(self.valid_destinations)
            self.packages.append({
                'id': len(self.packages) + 1,
                'destination': destination,
                'priority': random.choices(
                    ['Normal', 'Express', 'Urgent'], 
                    weights=[0.7, 0.2, 0.1]
                )[0],
                'weight': random.uniform(0.1, 3.0),
                'created_at': datetime.now()
            })
    
    def get_next_package(self):
        if self.packages:
            # Prioritize urgent packages
            for i, pkg in enumerate(self.packages):
                if pkg['priority'] == 'Urgent':
                    return self.packages.pop(i)
            
            # Then express
            for i, pkg in enumerate(self.packages):
                if pkg['priority'] == 'Express':
                    return self.packages.pop(i)
            
            # Then normal
            return self.packages.pop(0)
        return None
    
    def draw(self, surface, cell_size, font_small):
        # Draw warehouse
        pygame.draw.circle(surface, self.color, 
                          (self.x * cell_size, self.y * cell_size), 
                          self.radius)
        
        # Draw package count
        text = font_small.render(f"WH{self.id}", True, TEXT_COLOR)
        surface.blit(text, (self.x * cell_size - 15, self.y * cell_size - 30))
        
        text = font_small.render(f"Packages: {len(self.packages)}", True, TEXT_COLOR)
        surface.blit(text, (self.x * cell_size - 25, self.y * cell_size - 15))