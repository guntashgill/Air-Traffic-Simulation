import pygame
from .utils import *

class SmartLocker:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        self.capacity = 10
        self.packages = []
        self.color = (180, 100, 220)
    
    def add_package(self, package):
        if len(self.packages) < self.capacity:
            self.packages.append(package)
            return True
        return False
    
    def draw(self, surface, cell_size, font_small):
        # Draw locker
        pygame.draw.rect(surface, self.color, 
                        (self.x * cell_size - 8, self.y * cell_size - 8, 16, 16))
        
        # Draw package count
        text = font_small.render(f"L{self.id}: {len(self.packages)}", True, TEXT_COLOR)
        surface.blit(text, (self.x * cell_size - 15, self.y * cell_size - 20))