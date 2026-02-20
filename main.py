import cv2
import time
import copy
import config
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from dashboard import Dashboard
from drawing_engine import DrawingEngine

def main():
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened properly
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Set camera resolution. Typical wide format
    # The actual output might be different based on hardware support
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Initialize Modules
    hand_tracker = HandTracker()
    gesture_detector = GestureDetector()
    
    # We need the actual frame width/height to initialize the Dashboard and DrawingEngine
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame from webcam.")
        return
        
    # Resize frame to respect MAX_WIDTH in config
    h, w = frame.shape[:2]
    if w > config.FRAME_WIDTH_MAX:
        ratio = config.FRAME_WIDTH_MAX / w
        h = int(h * ratio)
        w = config.FRAME_WIDTH_MAX
        
    dashboard = Dashboard(w)
    drawing_engine = DrawingEngine(h, w)
    
    # Centralized state dictionary
    state = copy.deepcopy(config.INITIAL_STATE)

    # FPS Calculation
    prev_time = 0
    
    print("Whiteboard initialized. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Flip the frame horizontally for mirror effect
        if config.FLIP_FRAME:
            frame = cv2.flip(frame, 1)

        # Resize for performance and sizing consistency
        frame = cv2.resize(frame, (w, h))
        
        # 1. Detect Hand Landmarks
        landmarks_data = hand_tracker.process_frame(frame)
        
        dashboard_consumed = False
        
        if landmarks_data:
            # 2. Extract specific landmarks
            index_tip = landmarks_data["index_tip"]
            
            # 3. Detect Gestures
            gestures = gesture_detector.detect_gestures(landmarks_data)
            
            # Update state with gesture data
            state["pinch_active"] = gestures["pinch"]
            state["flat_hand"] = gestures["flat_hand"]
            
            # 4. Handle Dashboard Interactions
            # Dashboard interaction takes precedence over drawing
            dashboard_consumed = dashboard.process_interaction(
                index_tip=index_tip, 
                is_pinching=state["pinch_active"], 
                current_state=state
            )
            
            # 5. Handle Drawing Logic
            drawing_engine.draw(
                current_state=state,
                index_tip=index_tip,
                dashboard_consumed=dashboard_consumed
            )
            
            # Optional: Draw cursor for user feedback (a small hollow circle at index tip)
            if not dashboard_consumed:
                # If pinching, render a solid circle instead
                cursor_color = state["pen_color"] if not state["flat_hand"] else config.COLORS["white"]
                cursor_thickness = -1 if state["pinch_active"] else 2
                cursor_radius = state["pen_size"] if not state["flat_hand"] else state["eraser_size"]
                cv2.circle(frame, index_tip, cursor_radius, cursor_color, cursor_thickness)
        else:
            # Reset gestures if no hand found
            state["pinch_active"] = False
            state["flat_hand"] = False
            
            # Finalize any pending shape if hand is lost mid-draw
            drawing_engine.draw(
                current_state=state,
                index_tip=(0,0), # Dummy tip
                dashboard_consumed=False
            )
            
        # 6. Render Dashboard (Visuals)
        dashboard.render(frame, state)
            
        # 7. Render Composite Frame (Canvas overlay)
        final_output = drawing_engine.render_overlay(frame)
        
        # FPS Calculation & Display
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        
        cv2.putText(final_output, f"FPS: {int(fps)}", (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.COLORS["green"], 2)
                    
        # Show Output
        cv2.imshow("Gesture Controlled Virtual Whiteboard", final_output)

        # Clean Exit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    hand_tracker.release()

if __name__ == "__main__":
    main()
