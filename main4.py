import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
import datetime

from main3 import *

from typing import List

def ShowFrame(frame_name: str,cam:Maskinator):
    frame, mask = cam.get_frame()
    frame_circles = cam.locate_circles(mask)
    cam.pinpoint_cirlce(frame_circles, mask, (0, 255, 0))
    cam.pinpoint_cirlce(frame_circles, frame, (0, 255, 0))

    cv.imshow(frame_name, mask)
    cv.imshow(f"{frame_name}-norm", frame)

def main():
    cam01 = Maskinator("./3DCameras/cam_01/recording03_Trim.mp4")
    cam02 = Maskinator("./3DCameras/cam02/recording01_Trim.mp4")


    while True:
        ShowFrame("cam01", cam01)
        ShowFrame("cam02", cam02)
        if cv.waitKey(0) & 0xFF == ord("q"):
            break


if "__main__" == __name__:
    main()

