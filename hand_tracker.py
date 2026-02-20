import cv2
import time
import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config

class HandTracker:
    def __init__(self):
        # MediaPipe Tasks API requires a model file
        model_path = os.path.join(os.path.dirname(__file__), 'hand_landmarker.task')
        if not os.path.exists(model_path):
            print("Downloading hand_landmarker.task...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            
        base_options = python.BaseOptions(model_asset_path=model_path)

        running_mode = vision.RunningMode.IMAGE if config.STATIC_IMAGE_MODE else vision.RunningMode.VIDEO
        
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=running_mode,
            num_hands=config.MAX_NUM_HANDS,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.running_mode = running_mode

    def process_frame(self, frame):
        """
        Processes a BGR image and returns structured hand landmark pixel coordinates.
        Does not draw anything on the frame.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        if self.running_mode == vision.RunningMode.VIDEO:
            timestamp_ms = int(time.time() * 1000)
            # Ensure strictly increasing timestamp for VIDEO mode
            if hasattr(self, 'last_timestamp') and timestamp_ms <= self.last_timestamp:
                timestamp_ms = self.last_timestamp + 1
            self.last_timestamp = timestamp_ms
            detection_result = self.detector.detect_for_video(mp_image, timestamp_ms)
        else:
            detection_result = self.detector.detect(mp_image)

        if not detection_result.hand_landmarks:
            return None

        # Process the primary hand (index 0)
        hand_landmarks = detection_result.hand_landmarks[0]
        h, w, _ = frame.shape

        landmarks = []
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            landmarks.append((cx, cy))

        try:
            structured_data = {
                "landmarks": landmarks,
                "thumb_mcp": landmarks[2],
                "thumb_ip": landmarks[3],
                "thumb_tip": landmarks[4],
                "index_pip": landmarks[6],
                "index_tip": landmarks[8],
                "middle_pip": landmarks[10],
                "middle_tip": landmarks[12],
                "ring_pip": landmarks[14],
                "ring_tip": landmarks[16],
                "pinky_pip": landmarks[18],
                "pinky_tip": landmarks[20]
            }
            return structured_data
        except IndexError:
            return None

    def release(self):
        """Releases MediaPipe resources."""
        self.detector.close()
