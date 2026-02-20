import cv2
import numpy as np
import collections
import config

class DrawingEngine:
    def __init__(self, frame_height, frame_width):
        self.height = frame_height
        self.width = frame_width
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.smoothing_queue = collections.deque(maxlen=config.SMOOTHING_WINDOW)
        self.prev_point = None
        
        # Shape preview specifics
        self.start_point = None
        self.preview_canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def draw(self, current_state, index_tip, dashboard_consumed):
        """
        Handle all drawing/erasing logic on the canvas and preview canvas.
        Requires state dictionary to know tool, size, color, shape, and active gestures.
        Index tip is the raw pixel coordinate returned from HandTracker.
        dashboard_consumed True means we just changed a tool or hovered Dash. DONT DRAW.
        """
        # Clear preview canvas every frame
        self.preview_canvas.fill(0)

        pinch = current_state["pinch_active"]
        flat_hand = current_state.get("flat_hand", False)

        # Handle Erasing (Overrides everything else, assuming flat_hand takes priority)
        if flat_hand:
            # Erase by drawing black circle on the main canvas
            # Eraser ignores smoothing and shapes
            cv2.circle(self.canvas, index_tip, current_state["eraser_size"], config.COLORS["black"], -1)
            # Reset drawing states so we don't accidentally connect lines after erasing
            self.smoothing_queue.clear()
            self.prev_point = None
            self.start_point = None
            return

        # If we are over the dashboard or not pinching, reset states and stop
        if dashboard_consumed or not pinch:
            self.smoothing_queue.clear()
            self.prev_point = None
            
            # If we were drawing a shape and just released the pinch, commit the shape!
            if self.start_point is not None and not dashboard_consumed:
                self._commit_shape(current_state, index_tip)
            
            self.start_point = None
            return

        # --- Active Drawing Logic below ---

        # 1. Smooth the point
        self.smoothing_queue.append(index_tip)
        smoothed_x = int(sum([p[0] for p in self.smoothing_queue]) / len(self.smoothing_queue))
        smoothed_y = int(sum([p[1] for p in self.smoothing_queue]) / len(self.smoothing_queue))
        current_point = (smoothed_x, smoothed_y)

        # Set Start Point if beginning a shape or a new line
        if self.start_point is None:
            self.start_point = current_point
            self.prev_point = current_point

        shape_type = current_state["shape_type"]
        color = current_state["pen_color"]
        size = current_state["pen_size"]

        # 2. Freehand vs Shapes
        if shape_type == "freehand":
            # Draw directly to main canvas
            cv2.line(self.canvas, self.prev_point, current_point, color, size)
            self.prev_point = current_point
        else:
            # Draw preview onto the temporary preview canvas
            if shape_type == "line":
                cv2.line(self.preview_canvas, self.start_point, current_point, color, size)
            
            elif shape_type == "rectangle":
                cv2.rectangle(self.preview_canvas, self.start_point, current_point, color, size)
            
            elif shape_type == "circle":
                # Auto fit circle: radius is distance between start and current
                radius = int(np.hypot(current_point[0] - self.start_point[0], 
                                      current_point[1] - self.start_point[1]))
                cv2.circle(self.preview_canvas, self.start_point, radius, color, size)
                
    def _commit_shape(self, current_state, end_point):
        """
        When pinch is released, draw the final shape permanently onto the canvas.
        """
        shape_type = current_state["shape_type"]
        color = current_state["pen_color"]
        size = current_state["pen_size"]
        
        if shape_type == "line":
            cv2.line(self.canvas, self.start_point, end_point, color, size)
        elif shape_type == "rectangle":
            cv2.rectangle(self.canvas, self.start_point, end_point, color, size)
        elif shape_type == "circle":
            radius = int(np.hypot(end_point[0] - self.start_point[0], 
                                  end_point[1] - self.start_point[1]))
            cv2.circle(self.canvas, self.start_point, radius, color, size)

    def render_overlay(self, frame):
        """
        Merge the permanent canvas and the preview canvas with the main video frame.
        """
        # Convert black pixels to transparent (by using a mask, or addWeighted if canvas has black background)
        # Using simple mask addition since canvas uses 0 for blank space
        
        # 1. Add permanent canvas
        mask_canvas = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask_canvas = cv2.threshold(mask_canvas, 1, 255, cv2.THRESH_BINARY)
        mask_canvas_inv = cv2.bitwise_not(mask_canvas)
        
        # Black-out the area of drawing in the frame
        frame_bg = cv2.bitwise_and(frame, frame, mask=mask_canvas_inv)
        # Add the drawing
        frame_canvas = cv2.add(frame_bg, self.canvas)
        
        # 2. Add preview canvas on top
        mask_preview = cv2.cvtColor(self.preview_canvas, cv2.COLOR_BGR2GRAY)
        _, mask_preview = cv2.threshold(mask_preview, 1, 255, cv2.THRESH_BINARY)
        mask_preview_inv = cv2.bitwise_not(mask_preview)
        
        frame_canvas_bg = cv2.bitwise_and(frame_canvas, frame_canvas, mask=mask_preview_inv)
        final_frame = cv2.add(frame_canvas_bg, self.preview_canvas)
        
        return final_frame
