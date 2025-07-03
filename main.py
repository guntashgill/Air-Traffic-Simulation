import pygame
import random
import time
import numpy as np
from datetime import datetime
from simulation.city import CityGrid
from simulation.warehouse import Warehouse
from simulation.station import ChargingStation
from simulation.locker import SmartLocker
from simulation.weather import WeatherSimulator
from simulation.dashboard import Dashboard, Button
from simulation.utils import *
from simulation.ml_model import MLModel
from simulation.data_collector import DataCollector
from simulation.drone import Drone

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swarm Delivery Network Simulation")
clock = pygame.time.Clock()

# Initialize fonts
font_small = pygame.font.SysFont("Arial", FONT_SMALL_SIZE)
font_medium = pygame.font.SysFont("Arial", FONT_MEDIUM_SIZE)
font_large = pygame.font.SysFont("Arial", FONT_LARGE_SIZE, bold=True)

# Initialize simulation objects
city = CityGrid(30, 20)

# Create lockers first
lockers = []
locker_positions = []
for i in range(3):
    x, y = random.randint(5, 25), random.randint(5, 15)
    while not city.is_valid_position(x, y):
        x, y = random.randint(5, 25), random.randint(5, 15)
    lockers.append(SmartLocker(x, y, i+1))
    locker_positions.append((x, y))

# Pass city to warehouse
warehouse = Warehouse(2, 2, 1, city)

# Create charging stations
stations = []
for i in range(3):
    x, y = random.randint(5, 25), random.randint(5, 15)
    while not city.is_valid_position(x, y):
        x, y = random.randint(5, 25), random.randint(5, 15)
    stations.append(ChargingStation(x, y, i+1))

# Create drones
drones = []
for i in range(1, 11):
    drones.append(Drone(i, warehouse.x + random.uniform(-0.5, 0.5), 
                      warehouse.y + random.uniform(-0.5, 0.5), warehouse))

# Initialize weather and dashboard
weather = WeatherSimulator()
dashboard = Dashboard()

# Initialize ML and data collection
data_collector = DataCollector()
ml_system = MLModel()
ml_system.load_models()

# Create control buttons
add_package_btn = Button(10, 10, 200, 40, "Add Package", font_medium)
add_drone_btn = Button(10, 60, 200, 40, "Add Drone", font_medium)
storm_btn = Button(10, 110, 200, 40, "Simulate Storm", font_medium)
retrain_btn = Button(10, 160, 200, 40, "Retrain Models", font_medium)

# Simulation state
packages_delivered = 0
running = True
last_package_time = time.time()
last_demand_update = time.time()
last_data_save = time.time()
package_interval = 5  # seconds

# Main simulation loop
while running:
    current_time = time.time()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle button events
        mouse_pos = pygame.mouse.get_pos()
        add_package_btn.check_hover(mouse_pos)
        add_drone_btn.check_hover(mouse_pos)
        storm_btn.check_hover(mouse_pos)
        retrain_btn.check_hover(mouse_pos)
        
        if add_package_btn.handle_event(event):
            warehouse.add_package()
        
        if add_drone_btn.handle_event(event):
            drones.append(Drone(len(drones) + 1, 
                              warehouse.x + random.uniform(-0.5, 0.5), 
                              warehouse.y + random.uniform(-0.5, 0.5), 
                              warehouse))
        
        if storm_btn.handle_event(event):
            weather.current_event = {"name": "Storm", "duration": 50, "wind": (30, 60)}
            weather.update_counter = 0
            
        if retrain_btn.handle_event(event):
            print("Retraining ML models...")
            # In a real implementation, we'd retrain models here
            # This would typically be done in a separate process
            ml_system.load_models()  # Just reload for now
    
    # Update demand based on ML prediction
    if current_time - last_demand_update > 300:  # Every 5 minutes
        weather_impact = weather.get_weather_impact()
        warehouse.generate_packages(weather_impact)
        last_demand_update = current_time
    
    # Assign packages to idle drones
    for drone in drones:
        if drone.status == "IDLE":
            package = warehouse.get_next_package()
            if package:
                if drone.assign_package(package):
                    drone.start_delivery(city)
    
    # Update drones
    for drone in drones:
        drone.update(city, stations)
        
        # Check if drone reached delivery location
        if (drone.status == "DELIVERING" and drone.current_target and 
            distance((drone.x, drone.y), drone.destination) < 0.5):
            # Deliver package to nearest locker
            delivered = False
            for locker in lockers:
                if locker.add_package(drone.package):
                    packages_delivered += 1
                    delivery_time = (datetime.now() - drone.package['created_at']).total_seconds()
                    dashboard.add_delivery_time(delivery_time)
                    
                    # Record routing performance
                    optimal_length = abs(drone.start_pos[0]-drone.destination[0]) + abs(drone.start_pos[1]-drone.destination[1])
                    data_collector.record_routing(
                        drone.start_pos, drone.destination, drone.path,
                        optimal_length, 100, drone.battery, weather.get_weather_impact()
                    )
                    
                    drone.package = None
                    drone.payload = 0
                    drone.status = "RETURNING"
                    drone.find_path(city, (drone.x, drone.y), 
                                  (drone.warehouse.x, drone.warehouse.y))
                    delivered = True
                    break
            
            if not delivered:
                # If lockers are full, return to warehouse
                drone.status = "RETURNING"
                drone.find_path(city, (drone.x, drone.y), 
                              (drone.warehouse.x, drone.warehouse.y))
    
    # Update weather
    weather.update()
    weather_impact = weather.get_weather_impact()
    
    # Apply weather impact to drones
    for drone in drones:
        if drone.status in ["DELIVERING", "RETURNING"]:
            drone.speed = 0.04 * weather_impact
    
    # Update dashboard
    dashboard.update(drones, packages_delivered, len(warehouse.packages))
    
    # Save data periodically
    if current_time - last_data_save > 300:  # Every 5 minutes
        data_collector.save_all_data()
        last_data_save = current_time
    
    # Detect and display anomalies
    anomalies = ml_system.detect_anomalies(drones)
    if anomalies:
        print("\n--- ANOMALIES DETECTED ---")
        for anomaly in anomalies:
            print(anomaly)
    
    # Draw everything
    screen.fill(BACKGROUND)
    city.draw(screen)
    
    # Draw lockers
    for locker in lockers:
        locker.draw(screen, city.cell_size, font_small)
    
    # Draw charging stations
    for station in stations:
        station.draw(screen, city.cell_size, font_small)
    
    # Draw warehouse
    warehouse.draw(screen, city.cell_size, font_small)
    
    # Draw drones
    for drone in drones:
        drone.draw(screen, city.cell_size, font_small)
    
    # Draw weather
    weather.draw(screen, font_medium)
    
    # Draw dashboard
    dashboard.draw(screen, font_small, font_medium, font_large)
    
    # Draw buttons
    add_package_btn.draw(screen)
    add_drone_btn.draw(screen)
    storm_btn.draw(screen)
    retrain_btn.draw(screen)
    
    # Draw title
    title = font_large.render("Swarm Delivery Network Simulation", True, (100, 200, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
    
    # Draw ML status
    ml_status = "ML: Active" if ml_system.rl_agent.exploration_rate < 0.1 else "ML: Training"
    status_text = font_medium.render(ml_status, True, (0, 255, 100))
    screen.blit(status_text, (WIDTH - 150, HEIGHT - 30))
    
    pygame.display.flip()
    clock.tick(60)

# Save data before exit
data_collector.save_all_data()
pygame.quit()