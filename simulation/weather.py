import random
import math
import pygame
from .utils import *

class WeatherSimulator:
    def __init__(self):
        self.conditions = "Clear"
        self.temperature = 20
        self.wind_speed = 5
        self.wind_direction = random.uniform(0, 2 * math.pi)
        self.update_counter = 0
        self.weather_events = [
            {"name": "Clear", "duration": 300, "wind": (0, 15)},
            {"name": "Rain", "duration": 150, "wind": (10, 30)},
            {"name": "Storm", "duration": 50, "wind": (30, 60)},
            {"name": "Fog", "duration": 100, "wind": (0, 10)}
        ]
        self.current_event = random.choice(self.weather_events)
        self.event_duration = self.current_event["duration"]
    
    def update(self):
        self.update_counter += 1
        
        # Change weather periodically
        if self.update_counter > self.event_duration:
            self.current_event = random.choice(self.weather_events)
            self.event_duration = self.current_event["duration"]
            self.update_counter = 0
            self.wind_direction = random.uniform(0, 2 * math.pi)
        
        # Update wind speed
        min_wind, max_wind = self.current_event["wind"]
        self.wind_speed = min_wind + (max_wind - min_wind) * random.random()
        self.conditions = self.current_event["name"]
    
    def get_weather_impact(self):
        if self.conditions == "Clear":
            return 1.0
        elif self.conditions == "Rain":
            return 0.8
        elif self.conditions == "Storm":
            return 0.5
        elif self.conditions == "Fog":
            return 0.7
        return 1.0
    
    def draw(self, surface, font_medium):
        text = font_medium.render(f"Weather: {self.conditions} | Wind: {int(self.wind_speed)} km/h | Temp: {self.temperature}°C", 
                                True, TEXT_COLOR)
        surface.blit(text, (10, HEIGHT - 30))