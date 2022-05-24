import numpy as np
from PIL import ImageGrab
import cv2
import time

def procImage(originalImage):
    # convert to gray
    # processed_img = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    # edge detection
    processed_img = cv2.Canny(originalImage, threshold1=50, threshold2=200)
    processed_img = processed_img[150:500, :]

    return processed_img

## https://www.youtube.com/watch?v=ks4MPfMq8aQ&list=PLQVvvaa0QuDeETZEOy4VdocT7TOjfSA8a&index=2
def screen_record():
    last_time = time.time()
    while(True):

        printscreen = np.array(ImageGrab.grab(bbox=(8, 64, 640, 560)))
        proScreen = procImage(printscreen)
        print('loop took {} seconds'.format(1/(time.time()-last_time)))
        last_time = time.time()
        #cv2.imshow('window', cv2.cvtColor(printscreen, cv2.COLOR_BGR2RGB))
        cv2.imshow('window', proScreen)
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows() 
            break


screen_record()
