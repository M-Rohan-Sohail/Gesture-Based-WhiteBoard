# Real-Time Gesture-Controlled Virtual Whiteboard

This project is a high-performance, modular virtual whiteboard that allows users to draw, erase, and select different tools using purely hand gestures captured via a webcam. It relies on **OpenCV** for image processing and **MediaPipe** for real-time hand tracking.

---

## 🏗️ Project Architecture

The application is strictly divided into individual modules to maintain a clean separation of concerns.

### 1. `config.py` (Configuration)
Acts as the central control panel for the entire application.
- **Webcam Settings**: Defines resolution (`FRAME_WIDTH_MAX`) and mirroring.
- **MediaPipe Settings**: Controls how confident the AI must be to detect a hand (`MIN_DETECTION_CONFIDENCE`) and track it afterwards (`MIN_TRACKING_CONFIDENCE`).
- **Thresholds**: Defines `PINCH_THRESHOLD`. A lower value means your fingers must be squeezed tighter together to trigger a drawing mode.
- **Smoothing**: Defines `SMOOTHING_WINDOW`. A higher value averages your finger movements over more frames, making jagged lines appear buttery smooth.
- **Initial State**: Defines the default pen color, size, and shape type when the app launches.

### 2. `hand_tracker.py` (Hand Tracking Engine)
Wraps Google's MediaPipe Tasks Vision API.
- Captures raw webcam frames and feeds them into the AI model.
- Determines the exact pixel coordinates of the hand joints (fingertips, knuckles, etc.).
- Returns a structured dictionary of coordinates (e.g., `index_tip`, `thumb_tip`) without doing any actual drawing itself.

### 3. `gesture_detector.py` (Logic & Math)
Analyzes the coordinates provided by the tracker to determine what gesture the user is making.
- **`_check_pinch`**: Uses the mathematical Euclidean distance between the thumb tip and index tip. If they are closer than the `PINCH_THRESHOLD`, it reports that a pinch is actively happening (used for drawing or selecting).
- **`_check_flat_hand`**: Checks if the "tip" of every finger is physically higher up on the screen than the "pip" knuckle, meaning the hand is open and flat (used for the Eraser).

### 4. `dashboard.py` (User Interface)
Handles the top toolbar UI.
- Divides the top strip of the screen into clickable rectangular zones.
- If the gesture detector reports a "Pinch" while the index finger is over one of these zones, it updates the global state dictionary (e.g., changing `pen_color` to red or `shape_type` to circle).

### 5. `drawing_engine.py` (Rendering Canvas)
Manages two invisible canvases: a permanent canvas and a temporary preview canvas.
- **Smoothing**: Uses a `deque` queue to constantly average out the last few positions of the index finger to remove natural hand shaking.
- **Erasing**: If a flat hand is detected, it draws a black circle on the canvas (erasing the pixels).
- **Shapes**: If drawing a rectangle, line, or circle, it renders a preview on the temporary canvas while the user is actively pinching. When the pinch is released, it "commits" the shape permanently to the main canvas.
- Finally, it intelligently merges the drawing canvas on top of the physical webcam feed.

### 6. `main.py` (The Orchestrator)
The central loop of the program.
- Connects to the webcam using `cv2.VideoCapture`.
- Reads a frame -> passes it to `HandTracker` -> passes points to `GestureDetector`.
- Checks if the user is interacting with the `Dashboard`.
- Passes the final state into the `DrawingEngine` to produce the final image.
- Calculates and displays the real-time FPS on the bottom left.

---


*(Webcam exits gracefully by pressing the `q` key on your keyboard).*
