import random
import numpy as np
import pygame
from .utils import *

class CityGrid:
    def __init__(self, width, height, cell_size=40):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = np.zeros((width, height), dtype=int)
        self.buildings = []
        self.roads = []
        self.generate_city_layout()
        
    def generate_city_layout(self):
        # Create main roads
        for i in range(0, self.width, 5):
            for j in range(self.height):
                if random.random() < 0.8:
                    self.grid[i][j] = 1
                    self.roads.append((i, j))
        
        for j in range(0, self.height, 5):
            for i in range(self.width):
                if random.random() < 0.8:
                    self.grid[i][j] = 1
                    self.roads.append((i, j))
        
        # Create buildings
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[i][j] == 0 and random.random() < 0.3:
                    size = random.randint(2, 4)
                    if i + size < self.width and j + size < self.height:
                        for x in range(i, i + size):
                            for y in range(j, j + size):
                                self.grid[x][y] = 2
                        self.buildings.append((i, j, size, size))
    
    def is_valid_position(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y] != 2
        return False
    
    def draw(self, surface):
        # Draw background grid
        for i in range(0, WIDTH, self.cell_size):
            pygame.draw.line(surface, GRID_COLOR, (i, 0), (i, HEIGHT), 1)
        for j in range(0, HEIGHT, self.cell_size):
            pygame.draw.line(surface, GRID_COLOR, (0, j), (WIDTH, j), 1)
        
        # Draw roads
        for (i, j) in self.roads:
            pygame.draw.rect(surface, ROAD_COLOR, 
                            (i * self.cell_size, j * self.cell_size, 
                             self.cell_size, self.cell_size))
        
        # Draw buildings
        for (i, j, w, h) in self.buildings:
            pygame.draw.rect(surface, BUILDING_COLOR, 
                            (i * self.cell_size, j * self.cell_size, 
                             w * self.cell_size, h * self.cell_size))