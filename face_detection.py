import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import socket
import struct
cam = cv2.VideoCapture(0)

def main():
    esp_ip = "192.168.4.1"
    last_send = 0
    interval = 0.5
    esp_port = 12345
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    model_path = "/Users/kyrohanna/Documents/skeleton-project/blaze_face_full_range.tflite"

    BaseOptions = mp.tasks.BaseOptions
    FaceDetector = mp.tasks.vision.FaceDetector
    FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceDetectorOptions(base_options=BaseOptions(model_asset_path = model_path), running_mode=VisionRunningMode.VIDEO)
    with FaceDetector.create_from_options(options) as detector:
        while True:
            try:
                if (time.monotonic() - last_send >= interval):
                    last_send = time.monotonic()
                    x, y = get_face_position(detector)
                    data = struct.pack('<ii', x, y)
                    try:
                        socket1.sendto(data, (esp_ip, esp_port))
                    except OSError:
                        print("IP Address not found")
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
        x = int(bbox.origin_x + bbox.width / 2)
        y = int(bbox.origin_y + bbox.height / 2)
        return x, y
    return -1, -1

main()