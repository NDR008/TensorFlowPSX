import numpy as np
from PIL import ImageGrab
import cv2
import time

# Might redo in gl shader
# https: // towardsdatascience.com/how-i-learned-lane-detection-using-asphalt-8-airborne-bae4d0982134
def procImage(originalImage):
    # convert to gray
    processed_img = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.GaussianBlur(processed_img, (5, 5), 1.4)
    # edge detection
    processed_img = cv2.Canny(originalImage, threshold1=100, threshold2=250)
    # Sobel Edge Detection on the X axis
    # sobelx = cv2.Sobel(src=processed_img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5)
    # sobely = cv2.Sobel(src=processed_img, ddepth=cv2.CV_64F, dx=0,
    #                dy=1, ksize=5)  # Sobel Edge Detection on the Y axis
    # sobelxy = cv2.Sobel(src=processed_img, ddepth=cv2.CV_64F,
    #                 dx=1, dy=1, ksize=11)  # Combined X

    return processed_img


def overlay_lines(image, lines):

    for line in lines:
        coordinates = line[0]
        cv2.line(image, (coordinates[0], coordinates[1]),
                 (coordinates[2], coordinates[3]), [255, 255, 255], 3)


def edgeprocessed(image, lower):

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edgeprocessed_img = cv2.Canny(gray_image, threshold1=100,
                                  threshold2=200+lower)

    edgeprocessed_img = cv2.GaussianBlur(edgeprocessed_img, (3, 3), 2)

    return edgeprocessed_img

# canny image processing for detecting edges

## https://www.youtube.com/watch?v=ks4MPfMq8aQ&list=PLQVvvaa0QuDeETZEOy4VdocT7TOjfSA8a&index=2
def screen_record():
    last_time = time.time()
    b = 1
    fps_avg = 0
    last_time = .0000001
    lower = 10
    while(True):
        if b % 10000 == 0:
            lower = lower + 10
        fps_avg = fps_avg + (1/(time.time()-last_time)) / b
        printscreen = np.array(ImageGrab.grab(bbox=(8, 64, 640, 560)))
        proScreen = edgeprocessed(printscreen, lower)
        print('loop took {} seconds'.format(1/(time.time()-last_time)))
        last_time = time.time()
        cv2.imshow('window', cv2.cvtColor(printscreen, cv2.COLOR_BGR2RGB))
        cv2.imshow('window', proScreen)
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows() 
            print(b)
            break


        b = b + 1

screen_record()
