import cv2
import config

class Dashboard:
    def __init__(self, width):
        self.height = config.DASHBOARD_HEIGHT
        self.width = width
        
        # Tools layout
        # We'll split the width into actionable regions
        # colors: red, green, blue, yellow, purple
        # sizes: S, M, L
        # shapes: freehand, line, circle, rect
        # eraser sizes: S, M, L
        
        self.regions = {}
        self._setup_regions()
        
    def _setup_regions(self):
        """
        Divide the dashboard into rectangular clickable areas.
        """
        # We have ~14 distinct buttons, split evenly for simplicity
        button_width = self.width // 14
        
        buttons = [
            ("color", config.COLORS["red"], "Red"),
            ("color", config.COLORS["green"], "Green"),
            ("color", config.COLORS["blue"], "Blue"),
            ("color", config.COLORS["yellow"], "Yellow"),
            ("size", 2, "Pen S"),
            ("size", 5, "Pen M"),
            ("size", 10, "Pen L"),
            ("shape", "freehand", "Free"),
            ("shape", "line", "Line"),
            ("shape", "circle", "Circ"),
            ("shape", "rectangle", "Rect"),
            ("eraser_size", 20, "Eraser S"),
            ("eraser_size", 40, "Eraser M"),
            ("eraser_size", 60, "Eraser L")
        ]
        
        for i, (b_type, b_val, b_name) in enumerate(buttons):
            x1 = i * button_width
            x2 = (i + 1) * button_width
            y1 = 0
            y2 = self.height
            self.regions[b_name] = {
                "type": b_type,
                "value": b_val,
                "rect": (x1, y1, x2, y2)
            }

    def render(self, frame, current_state):
        """
        Draw the dashboard onto the frame.
        """
        # Draw background
        cv2.rectangle(frame, (0, 0), (self.width, self.height), config.COLORS["dark_gray"], -1)
        
        for name, data in self.regions.items():
            x1, y1, x2, y2 = data["rect"]
            b_type = data["type"]
            val = data["value"]
            
            # Determine background highlight based on active state
            bg_color = config.COLORS["gray"]
            
            if b_type == "color" and current_state["pen_color"] == val:
                bg_color = config.COLORS["white"]
            elif b_type == "size" and current_state["pen_size"] == val:
                bg_color = config.COLORS["white"]
            elif b_type == "shape" and current_state["shape_type"] == val:
                bg_color = config.COLORS["white"]
            elif b_type == "eraser_size" and current_state["eraser_size"] == val:
                bg_color = config.COLORS["white"]
                
            cv2.rectangle(frame, (x1, y1), (x2, y2), bg_color, -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), config.COLORS["black"], 2) # Border
            
            # Label
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            text_size = cv2.getTextSize(name, font, font_scale, thickness)[0]
            
            tx = x1 + (x2 - x1 - text_size[0]) // 2
            ty = y1 + (y2 - y1 + text_size[1]) // 2
            
            text_color = config.COLORS["black"]
            if b_type == "color":
                text_color = val # draw text in the color itself if it's a color button
                
            cv2.putText(frame, name, (tx, ty), font, font_scale, text_color, thickness)

    def process_interaction(self, index_tip, is_pinching, current_state):
        """
        Check if the index tip is over the dashboard and pinching.
        Update state if true, return whether the event was handled.
        """
        x, y = index_tip
        
        # If not pinching, or not in dashboard area, do nothing
        if not is_pinching or y > self.height:
            return False
            
        # Check which button was clicked
        for name, data in self.regions.items():
            x1, y1, x2, y2 = data["rect"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                # Update current state
                b_type = data["type"]
                val = data["value"]
                
                if b_type == "color":
                    current_state["pen_color"] = val
                elif b_type == "size":
                    current_state["pen_size"] = val
                elif b_type == "shape":
                    current_state["shape_type"] = val
                elif b_type == "eraser_size":
                    current_state["eraser_size"] = val
                    
                return True # consumed
                
        return True # if inside dashboard but no button, still consumed (don't draw on dashboard)
