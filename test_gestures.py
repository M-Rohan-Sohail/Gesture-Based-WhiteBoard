"""
Unit tests or offline verification for gesture detection logic.
"""
import copy
from gesture_detector import GestureDetector
from config import INITIAL_STATE

def test_flat_hand():
    gd = GestureDetector()
    
    # Mock landmarks for a flat hand (fingers extended up, y is smaller for tips than pips)
    # y=100 is tip, y=200 is pip
    flat_data = {
        "index_tip": (100, 100), "index_pip": (100, 200),
        "middle_tip": (150, 100), "middle_pip": (150, 200),
        "ring_tip": (200, 100), "ring_pip": (200, 200),
        "pinky_tip": (250, 100), "pinky_pip": (250, 200),
        "thumb_tip": (50, 150), "thumb_mcp": (100, 250), # Thumb is extended outward (dist=111 > 30)
    }
    
    result = gd.detect_gestures(flat_data)
    assert result["flat_hand"] == True, f"Expected flat_hand=True, got {result['flat_hand']}"
    assert result["pinch"] == False, f"Expected pinch=False, got {result['pinch']}"
    print("test_flat_hand passed")

def test_pinch():
    gd = GestureDetector()
    
    # Mock landmarks for a pinch (thumb tip and index tip are close)
    pinch_data = {
        "index_tip": (100, 100), "index_pip": (100, 200),
        "middle_tip": (150, 250), "middle_pip": (150, 200), # Not extended
        "ring_tip": (200, 250), "ring_pip": (200, 200),
        "pinky_tip": (250, 250), "pinky_pip": (250, 200),
        "thumb_tip": (105, 105), "thumb_mcp": (100, 250), # Thumb tip close to index tip
    }
    
    result = gd.detect_gestures(pinch_data)
    assert result["flat_hand"] == False, f"Expected flat_hand=False, got {result['flat_hand']}"
    assert result["pinch"] == True, f"Expected pinch=True, got {result['pinch']}"
    print("test_pinch passed")

if __name__ == "__main__":
    test_flat_hand()
    test_pinch()
    print("All tests passed.")
