import cv2

# Video & Display Settings
FRAME_WIDTH_MAX = 1080
TARGET_FPS = 60 # For internal logic if needed, OpenCV handles camera hardware FPS
FLIP_FRAME = True

# MediaPipe Hand Tracking Settings
STATIC_IMAGE_MODE = False
MAX_NUM_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.9
MIN_TRACKING_CONFIDENCE = 0.65

# Gesture Thresholds
PINCH_THRESHOLD = 23.5  # Lowered slightly so fingers must be closer together to pinch 

# Drawing Engine Settings
SMOOTHING_WINDOW = 2 # Increased further for smooth drawing

# Dashboard Settings
DASHBOARD_HEIGHT = 75

# Colors (BGR format for OpenCV)
COLORS = {
    "red": (0, 0, 255),
    "green": (0, 255, 0),
    "blue": (255, 0, 0),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (200, 200, 200),
    "dark_gray": (50, 50, 50),
    "yellow": (0, 255, 255),
    "purple": (255, 0, 255),
    "cyan": (255, 255, 0)
}

# Initial State Dictionary
INITIAL_STATE = {
    "current_tool": "pen",       # Tools: 'pen'
    "pen_size": 5,
    "pen_color": COLORS["blue"],
    "eraser_size": 30,           # Active only when flat_hand is True
    "shape_type": "freehand",    # Shapes: 'freehand', 'line', 'circle', 'rectangle'
    "pinch_active": False
}
