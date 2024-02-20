

import cv2
from time import sleep
import numpy as np
import math
import pyttsx3
import threading
import tkinter as tk
import tkinter.font as font
from PIL import Image, ImageTk


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

    focal_length_value = (width_in_rf_image * measured_distance) / real_width


    return focal_length_value


# distance estimation function
def distance_finder(focal_length, real_face_width, face_width_in_frame):

    distance = (real_face_width * focal_length) / face_width_in_frame
    return distance


# face detector function
def face_data(image):

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



def voice_alert(distance, position_info):
    try:
        sleep(1)
        value = math.floor(distance)
        inch_result = value / 2.54
        result = f"Person detected {math.floor(inch_result)} inches on the {position_info} side "
        bot.say(result)
        bot.runAndWait()
    except RuntimeError:
        pass




def camera_loop():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        if frame is None or frame.size == 0:
            print("Empty frame detected")
            continue

        try:
            face_positions = face_data(frame)
        except Exception as e:
            print("Error:", e)
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize the frame to fit the GUI window
        frame_resized = cv2.resize(frame_rgb, (640, 480))

        # Convert the frame to ImageTk format
        img = Image.fromarray(frame_resized)
        img_tk = ImageTk.PhotoImage(image=img)

        # Update the label with the new frame
        label.config(image=img_tk)
        label.image = img_tk


        for (x, face_width_in_frame) in face_positions:
            if face_width_in_frame != 0:
                Distance = distance_finder(focal_length_found, KNOWN_WIDTH, face_width_in_frame)
                position_info = "Left" if x > width // 2 else "Right"
                cv2.putText(
                    frame, f"Distance = {round(Distance, 2)} cm, Position: {position_info}", (50, 50), fonts, 1, WHITE, 2
                )

                # Launch a new thread for voice alert
                threading.Thread(target=voice_alert, args=(Distance, position_info)).start()

        #cv2.line(frame, mid_bottom, mid_top, (0, 0, 255), 2)
        #cv2.imshow("frame", frame)
        if cv2.waitKey(1) == ord("q"):
            break


def start_code():
    threading.Thread(target=camera_loop).start()

def stop_code():
    cap.release()
    root.destroy()
    cv2.destroyAllWindows()


root = tk.Tk()
root.title("See with the ears")
root.geometry("800x600")


button_font = font.Font(family="Times new roman", size=12)

start_button = tk.Button(root, text="Start Camera", bg='#ffaf00',
                         fg="green",
                         bd=0,
                         font=button_font,
                         height=2,
                         width=15,
                         command=start_code)
start_button.pack(pady=10, side=tk.BOTTOM)



stop_button = tk.Button(root, text="Stop Camera", bg='#ffaf00',
                        fg='red',
                        bd=0,
                        font=button_font,
                        height=2,
                        width=15,
                        command=stop_code)
stop_button.pack(pady=10, side=tk.BOTTOM)


label = tk.Label(root)
label.pack()

root.mainloop()
