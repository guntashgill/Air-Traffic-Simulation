import math

# Screen dimensions
WIDTH, HEIGHT = 1200, 800

# Colors
BACKGROUND = (10, 20, 30)
GRID_COLOR = (40, 50, 70)
ROAD_COLOR = (60, 70, 90)
BUILDING_COLOR = (70, 80, 100)
WAREHOUSE_COLOR = (0, 150, 200)
STATION_COLOR = (220, 180, 0)
DRONE_COLOR = (0, 200, 100)
DRONE_PATH = (0, 150, 100)
PACKAGE_COLOR = (220, 50, 50)
TEXT_COLOR = (220, 220, 220)
PANEL_BG = (20, 30, 40, 220)
BUTTON_COLOR = (50, 120, 180)
BUTTON_HOVER = (70, 150, 210)

# Font sizes
FONT_SMALL_SIZE = 14
FONT_MEDIUM_SIZE = 18
FONT_LARGE_SIZE = 24

def heuristic(a, b):
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def distance(a, b):
    """Euclidean distance between two points"""
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)