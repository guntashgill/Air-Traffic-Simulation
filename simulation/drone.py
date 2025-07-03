import math
import heapq
import time
from datetime import datetime

import pygame

from simulation import city
from .utils import distance, heuristic
from .utils import *
from .ml_model import MLModel

import math
import heapq
import time
import pygame
import numpy as np
from datetime import datetime
from .utils import distance, heuristic
from .ml_model import MLModel

class Drone:
    def __init__(self, id, x, y, warehouse):
        self.id = id
        self.x = x
        self.y = y
        self.warehouse = warehouse
        self.color = DRONE_COLOR
        self.radius = 8
        self.speed = 0.04
        self.battery = 100
        self.battery_consumption = 0.05
        self.max_payload = 5.0
        self.payload = 0
        self.status = "IDLE"
        self.package = None
        self.path = []
        self.current_target = None
        self.next_target = None
        self.destination = None
        self.charging_station = None
        self.battery_warning_sent = False
        self.last_update = time.time()
        self.start_pos = (x, y)
        self.battery_decrease_rate = 0
        self.last_battery = 100
        self.ml_model = MLModel()
        self.ml_model.load_models()
        self.stuck_timer = 0
        self.last_position = (x, y)
    
    def update(self, city, stations):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        
        # Check if drone is stuck
        current_pos = (self.x, self.y)
        if distance(current_pos, self.last_position) < 0.01:
            self.stuck_timer += delta_time
            if self.stuck_timer > 5:  # Stuck for 5 seconds
                self.recover_from_stuck(city, stations)
        else:
            self.stuck_timer = 0
        self.last_position = current_pos
        
        # Consume battery based on activity
        if self.status in ["DELIVERING", "RETURNING"]:
            self.battery -= self.battery_consumption * delta_time * 60
        elif self.status == "CHARGING":
            self.battery += 0.5 * delta_time * 60
            
            if self.battery >= 100:
                self.battery = 100
                self.status = "IDLE"
                if self.charging_station:
                    self.charging_station.remove_drone(self)
                self.charging_station = None
        
        # Track battery decrease rate
        battery_decrease = self.last_battery - self.battery
        if delta_time > 0:
            self.battery_decrease_rate = battery_decrease / delta_time
        self.last_battery = self.battery
        
        # Check for low battery
        if self.battery < 20 and not self.battery_warning_sent:
            self.battery_warning_sent = True
            if self.status != "CHARGING":
                self.find_nearest_station(city, stations)
        
        # Handle movement
        if self.path and self.status in ["DELIVERING", "RETURNING"]:
            if not self.current_target:
                self.current_target = self.path.pop(0)
            
            dx = self.current_target[0] - self.x
            dy = self.current_target[1] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < self.speed:
                self.x, self.y = self.current_target
                if self.path:
                    self.current_target = self.path.pop(0)
                else:
                    self.current_target = None
                    
                    # Reached destination
                    if self.status == "DELIVERING":
                        self.status = "RETURNING"
                        self.find_path(city, (self.x, self.y), 
                                      (self.warehouse.x, self.warehouse.y))
                    elif self.status == "RETURNING":
                        self.status = "IDLE"
                        self.payload = 0
                        self.package = None
            else:
                # Move toward target
                self.x += dx * self.speed / dist
                self.y += dy * self.speed / dist
    
    def recover_from_stuck(self, city, stations):
        """Recover when drone is stuck"""
        print(f"Drone {self.id} is stuck! Attempting recovery...")
        
        if self.status == "DELIVERING":
            # Try to find new path to destination
            self.find_path(city, (self.x, self.y), self.destination)
        elif self.battery < 30:
            # Low battery - find charging station
            self.find_nearest_station(city, stations)
        else:
            # Return to warehouse
            self.status = "RETURNING"
            self.find_path(city, (self.x, self.y), 
                          (self.warehouse.x, self.warehouse.y))
        
        self.stuck_timer = 0

    def assign_package(self, package):
        if self.status == "IDLE" and self.payload == 0:
            self.package = package
            self.payload = package['weight']
            self.destination = package['destination']
            self.status = "LOADING"
            self.battery_warning_sent = False
            return True
        return False

    def start_delivery(self, city):
        if self.status == "LOADING":
            self.status = "DELIVERING"
            self.find_path(city, (self.x, self.y), self.destination)

    def find_path(self, city, start, end):
        # Try ML optimized path
        ml_path = self.ml_model.get_optimized_route(start, end, self.battery, city)
        if ml_path:
            self.path = ml_path
            if self.path:
                self.current_target = self.path.pop(0)
            return

        # Fallback to A*
        open_set = []
        closed_set = set()
        came_from = {}

        g_score = {start: 0}
        f_score = {start: heuristic(start, end)}

        heapq.heappush(open_set, (f_score[start], start))

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == end:
                self.path = []
                while current in came_from:
                    self.path.append(current)
                    current = came_from[current]
                self.path.reverse()
                if self.path:
                    self.current_target = self.path.pop(0)
                return

            closed_set.add(current)

            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                neighbor = (current[0]+dx, current[1]+dy)

                if not city.is_valid_position(int(neighbor[0]), int(neighbor[1])):
                    continue
                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        self.path = [end]
        self.current_target = end

    def find_nearest_station(self, city, stations):
        min_dist = float('inf')
        nearest = None

        for station in stations:
            if station.can_charge():
                dist = distance((self.x, self.y), (station.x, station.y))
                if dist < min_dist:
                    min_dist = dist
                    nearest = station

        if nearest:
            self.charging_station = nearest
            self.status = "CHARGING"
            nearest.add_drone(self)
            self.find_path(city, (self.x, self.y), (nearest.x, nearest.y))
            return True
        return False

    def draw(self, surface, cell_size, font_small):
        pygame.draw.circle(surface, self.color, 
                          (int(self.x * cell_size), int(self.y * cell_size)), 
                          self.radius)

        text = font_small.render(f"D{self.id}", True, TEXT_COLOR)
        surface.blit(text, (int(self.x * cell_size) - 5, int(self.y * cell_size) - 20))

        status_text = f"{self.status[:4]} | {int(self.battery)}%"
        if self.payload > 0:
            status_text += f" | {self.payload}kg"
        text = font_small.render(status_text, True, TEXT_COLOR)
        surface.blit(text, (int(self.x * cell_size) - 25, int(self.y * cell_size) - 35))

        if self.path and self.status in ["DELIVERING", "RETURNING"]:
            points = [(int(self.x * cell_size), int(self.y * cell_size))]
            points.extend((int(x * cell_size), int(y * cell_size)) for x, y in self.path)

            if len(points) > 1:
                pygame.draw.lines(surface, DRONE_PATH, False, points, 2)
                dest_x, dest_y = points[-1]
                pygame.draw.circle(surface, (200, 100, 100), (dest_x, dest_y), 6, 2)

    def get_predicted_battery_life(self):
        return self.ml_model.predict_battery_life(self)
