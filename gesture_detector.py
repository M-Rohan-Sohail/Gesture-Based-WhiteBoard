import math
import config
import cv2 # Adding merely for any drawing functionality inside the gesture debug process if ever needed, but main logic is decoupled

class GestureDetector:
    def __init__(self):
        self.pinch_threshold = config.PINCH_THRESHOLD

    def detect_gestures(self, landmarks_data):
        """
        Receives structured landmark pixel coordinates.
        Returns a dictionary indicating the current recognized gestures.
        """
        if not landmarks_data:
            return {"pinch": False, "flat_hand": False}

        pinch_active = self._check_pinch(
            thumb_tip=landmarks_data["thumb_tip"],
            index_tip=landmarks_data["index_tip"]
        )

        flat_hand = self._check_flat_hand(landmarks_data)

        # No other gestures should trigger drawing, so we explicitly handle mutual exclusivity
        # in the main drawing engine, but we report pure gesture state here.
        return {
            "pinch": pinch_active,
            "flat_hand": flat_hand
        }

    def _check_pinch(self, thumb_tip, index_tip):
        """
        Calculate Euclidean distance between thumb and index.
        """
        dist = math.hypot(thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1])
        return dist < self.pinch_threshold

    def _check_flat_hand(self, d):
        """
        A hand is considered 'flat' if all fingers are extended.
        Requires tip y < pip y for index, middle, ring, pinky.
        Requires thumb to be extended outward on the x-axis relative to palm structure.
        """
        # Note: image coordinates: 0,0 is top-left, so "higher up" means lower y.
        # Finger extension check:
        # tip.y should be less than pip.y (fingers pointing up)
        fingers_extended = (
            d["index_tip"][1] < d["index_pip"][1] and
            d["middle_tip"][1] < d["middle_pip"][1] and
            d["ring_tip"][1] < d["ring_pip"][1] and
            d["pinky_tip"][1] < d["pinky_pip"][1]
        )

        # Thumb extension check depends on hand laterality, but since we're tracking a mirror
        # flipped feed, we check the distance from MCP to TIP to see if the thumb isn't tucked in.
        # A simpler check is that thumb_tip x and thumb_ip x have a distinct separation from the index finger horizontally.
        thumb_extended_distance = math.hypot(d["thumb_tip"][0] - d["thumb_mcp"][0], d["thumb_tip"][1] - d["thumb_mcp"][1])
        
        # Another heuristic for "all fingers extended" includes the thumb being pointing mostly up or outward,
        # but the primary condition defined was simply tips < pips for fingers + thumb extended.
        # We'll use a rudimentary thumb extension length check as an analog to it not being bent inward.
        # usually thumb mcp to tip distance is fairly large when extended.
        thumb_extended = thumb_extended_distance > 30 
        
        # We also want to ensure we're not just getting a flat hand reading during a weird rotation.
        # For our purposes, the requested condition:
        # index_tip.y < index_pip.y
        # middle_tip.y < middle_pip.y
        # ring_tip.y < ring_pip.y
        # pinky_tip.y < pinky_pip.y
        
        return fingers_extended and thumb_extended
