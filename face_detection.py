import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import socket
import struct

#Create camera using openCV library. Port is 0 to use default camera
cam = cv2.VideoCapture(0)

def main():
    #Strings containing IP address and port (for data transfer) of the ESP 32
    esp_ip = "192.168.4.1"
    esp_port = 12345
    last_send = 0
    interval = 0.5
    #Creates socket object, using IP v4 adresses and UDP protocol
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #file location of face detector program (this was downloaded off the internet)
    model_path = "/Users/kyrohanna/Documents/skeleton-project/blaze_face_full_range.tflite"

    #Create shorter references of objects existing in the mediapipe library
    BaseOptions = mp.tasks.BaseOptions
    FaceDetector = mp.tasks.vision.FaceDetector
    FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    #Creates configuration object of the face detector, with the default options, location of face detector model, and sets it to video mode
    options = FaceDetectorOptions(base_options=BaseOptions(model_asset_path = model_path), running_mode=VisionRunningMode.VIDEO)
    #creates face detector
    with FaceDetector.create_from_options(options) as detector:
        #repeats infinitely
        while True:
            try:
                #if more than the interval (seconds) has passed, send a new value to the ESP
                if (time.monotonic() - last_send >= interval):
                    last_send = time.monotonic()
                    #gets x and y position of the detected face
                    x, y = get_face_position(detector)
                    # struct.pack is used to convert coordinates into binary data so it can be sent to the ESP via UDP
                    #< means store the smallest bytes first, i means 32-bit integer (there are 2 i's since we are sending 2 integers). x and y refer to the integers being packaged and sent
                    data = struct.pack('<ii', x, y)
                    #tries to send the data to the ESP (at the given IP address and port), will print out error message if this is unsuccessful
                    try:
                        socket1.sendto(data, (esp_ip, esp_port))
                    except OSError:
                        print("IP Address not found")
                    print(f"X: {x}, Y: {y}")
            except TypeError:
                pass


def get_face_position(detector):
    #Reads data from camera.
    #ret is a boolean indicating whether a frame was recieved, frame is the actual image stored
    ret, frame = cam.read()

    #if a frame is actually recieved, the frame is convered from BGR to RGB format so the face detector can process it
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Creates a timestamp (in ms) when the frame was recieved. This is needed for the face detector when running in video
    timestamp = int(time.monotonic() * 1000)

    #converts image from openCV into an image format mediapipe can process
    mp_frame = mp.Image(image_format = mp.ImageFormat.SRGB, data = frame)

    #run the face detector with the frame and the time it was recorded
    face_detector_result = detector.detect_for_video(image = mp_frame, timestamp_ms = timestamp)
    #Checks if a face was detected
    if face_detector_result.detections:
        #Assumes first detected face is the largest one
        largestDetection = face_detector_result.detections[0]
        largestArea = 0
        #goes through list of detected faces
        for detection in face_detector_result.detections:
            #calculates area of detected face.
            temp_bbox = detection.bounding_box
            area = temp_bbox.width * temp_bbox.height
            #If the area of the current face is larger than the largest area, set the largestArea to the area of the current face and the largest detected face to the current face
            if (area > largestArea):
                largestArea = area
                largestDetection = detection
        #get the middle coordinates x and y of the face using the width and height and the top left x and y coordintes
        bbox = largestDetection.bounding_box
        x = int(bbox.origin_x + bbox.width / 2)
        y = int(bbox.origin_y + bbox.height / 2)
        return x, y
    #returns -1, -1 as the coordinates if no face detected (if a face is actually detected, the coordinates won't be a negative value)
    return -1, -1

main()