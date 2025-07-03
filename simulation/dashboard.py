import time
import pygame
import numpy as np
from .utils import *

class Dashboard:
    def __init__(self):
        self.metrics = {
            "total_deliveries": 0,
            "packages_in_transit": 0,
            "avg_delivery_time": 0,
            "total_distance": 0,
            "energy_used": 0,
            "drones_available": 0,
            "drones_charging": 0,
            "drones_delivering": 0
        }
        self.delivery_times = []
        self.start_time = time.time()
    
    def update(self, drones, packages_delivered, total_packages):
        # Update metrics
        delivering = sum(1 for d in drones if d.status in ["DELIVERING", "LOADING"])
        charging = sum(1 for d in drones if d.status == "CHARGING")
        available = sum(1 for d in drones if d.status == "IDLE")
        
        self.metrics = {
            "total_deliveries": packages_delivered,
            "packages_in_transit": delivering,
            "avg_delivery_time": np.mean(self.delivery_times) if self.delivery_times else 0,
            "total_distance": self.metrics["total_distance"] + 0.1 * len(drones),
            "energy_used": self.metrics["energy_used"] + 0.05 * len(drones),
            "drones_available": available,
            "drones_charging": charging,
            "drones_delivering": delivering,
            "total_packages": total_packages,
            "simulation_time": int(time.time() - self.start_time)
        }
    
    def add_delivery_time(self, delivery_time):
        self.delivery_times.append(delivery_time)
        if len(self.delivery_times) > 100:
            self.delivery_times.pop(0)
    
    def draw(self, surface, font_small, font_medium, font_large):
        # Draw semi-transparent panel
        panel = pygame.Surface((300, 250), pygame.SRCALPHA)
        panel.fill(PANEL_BG)
        surface.blit(panel, (WIDTH - 310, 10))
        
        # Draw title
        title = font_large.render("Swarm Delivery Dashboard", True, TEXT_COLOR)
        surface.blit(title, (WIDTH - 300, 15))
        
        # Draw metrics
        y_pos = 50
        for key, value in self.metrics.items():
            if key == "avg_delivery_time":
                text = f"{key.replace('_', ' ').title()}: {value:.1f}s"
            elif key in ["total_distance", "energy_used"]:
                text = f"{key.replace('_', ' ').title()}: {value:.1f}"
            else:
                text = f"{key.replace('_', ' ').title()}: {value}"
            
            text_surf = font_small.render(text, True, TEXT_COLOR)
            surface.blit(text_surf, (WIDTH - 300, y_pos))
            y_pos += 20
        
        # Draw drone status distribution
        pygame.draw.rect(surface, (50, 50, 70), (WIDTH - 300, y_pos + 10, 280, 80))
        total_drones = self.metrics["drones_available"] + self.metrics["drones_charging"] + self.metrics["drones_delivering"]
        
        if total_drones > 0:
            avail_width = 280 * self.metrics["drones_available"] / total_drones
            charg_width = 280 * self.metrics["drones_charging"] / total_drones
            deliv_width = 280 * self.metrics["drones_delivering"] / total_drones
            
            pygame.draw.rect(surface, DRONE_COLOR, (WIDTH - 300, y_pos + 10, avail_width, 25))
            pygame.draw.rect(surface, STATION_COLOR, (WIDTH - 300 + avail_width, y_pos + 10, charg_width, 25))
            pygame.draw.rect(surface, PACKAGE_COLOR, (WIDTH - 300 + avail_width + charg_width, y_pos + 10, deliv_width, 25))
            
            status_text = font_small.render("Drone Status: Available | Charging | Delivering", True, TEXT_COLOR)
            surface.blit(status_text, (WIDTH - 300, y_pos + 40))

class Button:
    def __init__(self, x, y, width, height, text, font_medium):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER
        self.is_hovered = False
        self.font_medium = font_medium
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=5)
        
        text_surf = self.font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False