import pygame
from .utils import *

class ChargingStation:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.color = STATION_COLOR
        self.radius = 10
        self.capacity = 3
        self.drones_charging = []
    
    def can_charge(self):
        return len(self.drones_charging) < self.capacity
    
    def add_drone(self, drone):
        if self.can_charge():
            self.drones_charging.append(drone)
            return True
        return False
    
    def remove_drone(self, drone):
        if drone in self.drones_charging:
            self.drones_charging.remove(drone)
    
    def draw(self, surface, cell_size, font_small):
        # Draw station
        pygame.draw.circle(surface, self.color, 
                          (self.x * cell_size, self.y * cell_size), 
                          self.radius)
        
        # Draw lightning symbol
        points = [
            (self.x * cell_size, self.y * cell_size - 5),
            (self.x * cell_size + 3, self.y * cell_size),
            (self.x * cell_size - 3, self.y * cell_size),
            (self.x * cell_size, self.y * cell_size + 5)
        ]
        pygame.draw.lines(surface, (255, 255, 200), False, points, 2)
        
        # Draw capacity
        text = font_small.render(f"ST{self.id}: {len(self.drones_charging)}/{self.capacity}", True, TEXT_COLOR)
        surface.blit(text, (self.x * cell_size - 15, self.y * cell_size - 15))