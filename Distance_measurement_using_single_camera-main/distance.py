

import cv2
from time import sleep
import numpy as np
import math
import pyttsx3



bot = pyttsx3.init()


# variablesq
# distance from camera to object(face) measured
KNOWN_DISTANCE = 60.96   # centimeter
# width of face in the real world or Object Plane
KNOWN_WIDTH = 14.3  # centimeter
# Colors
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
fonts = cv2.FONT_HERSHEY_COMPLEX
cap = cv2.VideoCapture(0)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


mid_bottom = (width // 2, 0)
mid_top = (width // 2, height)



# face detector object
face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


# focal length finder function
def focal_length(measured_distance, real_width, width_in_rf_image):
    """
    This Function Calculate the Focal Length(distance between lens to CMOS sensor), it is simple constant we can find by using
    MEASURED_DISTACE, REAL_WIDTH(Actual width of object) and WIDTH_OF_OBJECT_IN_IMAGE
    :param1 Measure_Distance(int): It is distance measured from object to the Camera while Capturing Reference image

    :param2 Real_Width(int): It is Actual width of object, in real world (like My face width is = 14.3 centimeters)
    :param3 Width_In_Image(int): It is object width in the frame /image in our case in the reference image(found by Face detector)
    :retrun focal_length(Float):"""
    focal_length_value = (width_in_rf_image * measured_distance) / real_width


    return focal_length_value


# distance estimation function
def distance_finder(focal_length, real_face_width, face_width_in_frame):
    """
    This Function simply Estimates the distance between object and camera using arguments(focal_length, Actual_object_width, Object_width_in_the_image)
    :param1 focal_length(float): return by the focal_length_Finder function

    :param2 Real_Width(int): It is Actual width of object, in real world (like My face width is = 5.7 Inches)
    :param3 object_Width_Frame(int): width of object in the image(frame in our case, using Video feed)
    :return Distance(float) : distance Estimated
    """
    distance = (real_face_width * focal_length) / face_width_in_frame
    return distance


# face detector function
def face_data(image):
    """
    This function Detect the face
    :param Takes image as argument.
    :returns face_width in the pixels
    """

    face_info = []
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray_image, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), WHITE, 1)
        face_info.append((x, w))

    return face_info


# reading reference image from directory
ref_image = cv2.imread("Ref_image2.png")

ref_image_face_width = face_data(ref_image)
if ref_image_face_width:
    ref_image_face_width = int(ref_image_face_width[0][1])
else:
    print("No face detected in the reference image.")
focal_length_found = focal_length(KNOWN_DISTANCE, KNOWN_WIDTH, ref_image_face_width)
print(focal_length_found)
#cv2.imshow("ref_image", ref_image)




while True:
    _, frame = cap.read()
    face_positions = face_data(frame)

    for (x, face_width_in_frame) in face_positions:
        if face_width_in_frame != 0:
            Distance = distance_finder(focal_length_found, KNOWN_WIDTH, face_width_in_frame)
            position_info = "Left" if x > width // 2 else "Right"
            cv2.putText(
                frame, f"Distance = {round(Distance, 2)} cm, Position: {position_info}", (50, 50), fonts, 1, (WHITE), 2
            )
            value = (math.floor(Distance) if position_info == "Left" else math.floor(Distance))
            inch_result = (value / 2.54)

            sleep(2)
            print(f"{math.floor(inch_result)} inches on the {position_info} side " )
            result = (f"Person approaching {math.floor(inch_result)} inches on the {position_info} side " )
            bot.say(result)
            bot.runAndWait()

    cv2.line(frame, mid_bottom, mid_top, (0, 0, 255), 2)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == ord("q"):
        break








