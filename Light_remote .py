# Imports
import numpy as np
import cv2
import math
import serial
import time
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages')


# Open Camera
capture = cv2.VideoCapture(0)


while capture.isOpened():

    # Capture frames from the camera
    ret, frame = capture.read()

    # Get hand data from the rectangle sub window
    cv2.rectangle(frame, (100, 100), (500, 500), (0, 255, 0), 0)  # (output of, (x1,y1), (x2,y2), color, width)
    crop_image = frame[100:500, 100:500] # cropped image from frame to check the value

    # Apply Gaussian blur
    blur = cv2.GaussianBlur(crop_image, (3, 3), 0) # it is a filter to reduce the noise of the image captured from camera

    # Change color-space from BGR -> HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Create a binary image with where white will be skin colors and rest is black
    mask2 = cv2.inRange(hsv, np.array([2, 0, 0]), np.array([20, 255, 255]))

    # Kernel for morphological transformation
    kernel = np.ones((5, 5))

    # Apply morphological transformations to filter out the background noise
    dilation = cv2.dilate(mask2, kernel, iterations=1)
    erosion = cv2.erode(dilation, kernel, iterations=1)

    # Apply Gaussian Blur and Threshold
    filtered = cv2.GaussianBlur(erosion, (3, 3), 0)
    ret, thresh = cv2.threshold(filtered, 127, 255, 0)

    # Show threshold image
    cv2.imshow("Thresholded", thresh)

    # Find contours
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # time.sleep(0.3)
    try:
        
        # Find contour with maximum area
        contour = max(contours, key=lambda x: cv2.contourArea(x))

        # Create bounding rectangle around the contour
        x, y, w, h = cv2.boundingRect(contour) #Small rectangle in which the hand is showing gesture
        cv2.rectangle(crop_image, (x, y), (x + w, y + h), (0, 0, 255), 0)

        # Find convex hull
        hull = cv2.convexHull(contour)

        # Draw contour
        drawing = np.zeros(crop_image.shape, np.uint8)
        cv2.drawContours(drawing, [contour], -1, (0, 255, 0), 0)
        cv2.drawContours(drawing, [hull], -1, (0, 0, 255), 0)

        # Find convexity defects
        hull = cv2.convexHull(contour, returnPoints=False)
        defects = cv2.convexityDefects(contour, hull)

        # Use cosine rule to find angle of the far point from the start and end point i.e. the convex points (the finger
        # tips) for all defects
        count_defects = 0

        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]      #start, end, far, and distance
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])

            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = (math.acos((b ** 2 + c ** 2 - a ** 2) /
                               (2 * b * c)) * 180) / 3.14

            # if angle < 90 draw a circle at the far point
            if angle <= 90:
                count_defects += 1
                cv2.circle(crop_image, far, 1, [0, 0, 255], -1)

            cv2.line(crop_image, start, end, [0, 255, 0], 2)

        # Print number of fingers
        if count_defects == 0:
            print("count_defect: ON")
            cv2.putText(frame, "LIGHTS ON", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2) #(font size, color, width)
            
            #time.sleep(.4)

        elif count_defects == 1:
            print("count_defect: OFF")
            cv2.putText(frame, "LIGHTS OFF", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            
            #time.sleep(.4)

        elif count_defects == 2:
            print("count_defect: BLUE")
            cv2.putText(frame, "BLUE", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            
            #time.sleep(.4)

        elif count_defects == 3:
            print("count_defect: GREEN")
            cv2.putText(frame, "GREEN", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            
            #time.sleep(.4)
        elif count_defects == 4:
            print("count_defect: SMOOTH EFFECT")
            cv2.putText(frame, "SMOOTH", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            
            #time.sleep(.4)
        else: #when unrecognised gesture is made by user
            pass
        
    except: #When no gesture is made by the user
        pass

    # Show required images
    cv2.imshow("Gesture", frame)
    # all_image = np.hstack((drawing, crop_image))
    # cv2.imshow('Contours', all_image)

    # Close the camera if 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
