import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime

# ...existing code...
class PostureDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        # changed: use lighter model_complexity for speed
        self.pose = self.mp_pose.Pose(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.posture_status = "Unknown"
        self.posture_score = 0

    # ...existing code...
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    # changed: optionally resize to process smaller frames (speeds up inference)
    def analyze_posture(self, image, process_width=640):
        # resize while keeping aspect ratio if image is wider than target
        h, w = image.shape[:2]
        if w > process_width:
            scale = process_width / w
            image_small = cv2.resize(image, (int(w*scale), int(h*scale)))
        else:
            image_small = image

        image_rgb = cv2.cvtColor(image_small, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            try:
                # landmarks are normalized to resized frame — that's fine for relative angles
                shoulder_left = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                               landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                shoulder_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                ear_left = [landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value].y]
                ear_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value].x,
                           landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value].y]
                hip_left = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                hip_right = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                           landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]

                neck_angle = self.calculate_angle(ear_left, shoulder_left, hip_left)
                shoulder_alignment = abs(shoulder_left[1] - shoulder_right[1])

                score = 100

                if neck_angle < 160 or neck_angle > 180:
                    score -= 30
                    self.posture_status = "Poor - Head Forward"
                elif neck_angle < 170:
                    score -= 15
                    self.posture_status = "Fair - Slight Forward Head"
                else:
                    self.posture_status = "Good Posture"

                if shoulder_alignment > 0.05:
                    score -= 20
                    self.posture_status += " (Shoulders Uneven)"

                self.posture_score = max(0, score)

                # draw landmarks on the resized image (faster). If you need original-size overlay,
                # run drawing on the full frame after mapping coordinates.
                self.mp_drawing.draw_landmarks(
                    image_small,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )

                # if resized, scale drawing back to original frame size
                if image_small.shape != image.shape:
                    image = cv2.resize(image_small, (w, h))
                else:
                    image = image_small

            except Exception as e:
                print(f"Error analyzing posture: {e}")
                self.posture_status = "Error"
                self.posture_score = 0
        else:
            self.posture_status = "No person detected"
            self.posture_score = 0

        return image, self.posture_status, self.posture_score

    def get_frame(self, cap):
        ret, frame = cap.read()
        if ret:
            return self.analyze_posture(frame)
        return None, "No camera feed", 0

    def release(self):
        self.pose.close()

# added: threaded capture that always keeps the latest frame (drops older frames)
class ThreadedVideoCapture:
    def __init__(self, src=0, width=640, height=480, backend=cv2.CAP_DSHOW):
        self.cap = cv2.VideoCapture(src, backend)
        # recommend setting buffer to 1, and lower resolution for speed
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            # CAP_PROP_BUFFERSIZE may not be supported on all backends; ignore failures
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        self.grabbed = False
        self.frame = None
        self.running = True
        import threading
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        while self.running:
            grabbed, frame = self.cap.read()
            if not grabbed:
                continue
            with self.lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.lock:
            if not self.grabbed:
                return False, None
            return True, self.frame.copy()

    def release(self):
        self.running = False
        self.thread.join(timeout=1)
        self.cap.release()