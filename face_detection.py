import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
cam = cv2.VideoCapture(0)

def main():
    model_path = "/Users/kyrohanna/Documents/blaze_face_full_range.tflite"

    BaseOptions = mp.tasks.BaseOptions
    FaceDetector = mp.tasks.vision.FaceDetector
    FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceDetectorOptions(base_options=BaseOptions(model_asset_path = model_path), running_mode=VisionRunningMode.VIDEO)
    with FaceDetector.create_from_options(options) as detector:
        while True:
            try:
                x, y = get_face_position(detector)
                print(f"X: {x}, Y: {y}")
            except TypeError:
                pass


def get_face_position(detector):
    timestamp = 0
    ret, frame = cam.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    timestamp = int(time.monotonic() * 1000)
    mp_frame = mp.Image(image_format = mp.ImageFormat.SRGB, data = frame)

    face_detector_result = detector.detect_for_video(image = mp_frame, timestamp_ms = timestamp)
    if face_detector_result.detections:
        largestDetection = face_detector_result.detections[0]
        largestArea = 0
        for detection in face_detector_result.detections:
            temp_bbox = detection.bounding_box
            area = temp_bbox.width * temp_bbox.height
            if (area > largestArea):
                largestArea = area
                largestDetection = detection
        bbox = largestDetection.bounding_box
        x = bbox.origin_x + bbox.width / 2
        y = bbox.origin_y + bbox.height / 2
        return x, y

main()