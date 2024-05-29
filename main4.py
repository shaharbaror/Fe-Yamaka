import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
import datetime




from main3 import *

from typing import List

def ShowFrame(cam:Maskinator):
    frame, mask = cam.get_frame()
    frame_circles = cam.locate_circles(mask)
    cam.pinpoint_cirlce(frame_circles, mask, (0, 255, 0))
    cam.pinpoint_cirlce(frame_circles, frame, (0, 255, 0))

    return frame, mask

def locate_circles(frame) -> List[List[float]] or None:
    circles = []

    cnts = cv.findContours(frame.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:

        ((x, y), radius) = cv.minEnclosingCircle(c)
        supposed_area = radius ** 2 * np.pi * 0.5

        if supposed_area < cv.contourArea(c) < supposed_area * 1.5 and radius > 6:
            circles.append([x, y, radius, time.time()])

    return circles

def delta_calculation(old_frame, new_frame):
    color_type = cv.COLOR_BGR2GRAY
    old_frame = cv.cvtColor(old_frame, color_type)
    new_frame = cv.cvtColor(new_frame, color_type)

    delta = np.absolute(new_frame - old_frame)


    threshold = 230
    min_amount = 10
    delta[delta > threshold] = 0
    delta[delta < min_amount] = 0
    return delta


class Linkudo:
    def __init__(self, value, nextt=None):
        self.value = value
        self.nextt = nextt


def main():
    cam01 = Maskinator("./3DCameras/cam01/recording01.mp4")
    cam00 = Maskinator("./3DCameras/cam02/recording02.mp4")

    lasto_framo, _ = ShowFrame(cam01)

    list1 = Linkudo(lasto_framo)
    pos1 = list1
    count = 0


    while True:
        curr_frame, _ = ShowFrame(cam01)
        shown_frame = curr_frame



        pos1.nextt = Linkudo(curr_frame)
        pos1 = pos1.nextt

        if count > 3:
            list1 = list1.nextt

            delt = delta_calculation(list1.value, pos1.value)
            found_circs = locate_circles(delt)
            print(found_circs)
            cam01.pinpoint_cirlce(found_circs, delt, (255, 0, 0))
            #   It is currently finding the old circle too
            #   i need to program it to ignore the old frame or to use it for detection
            cv.imshow("dult", delt)



        count += 1
        cv.imshow("furam", shown_frame)

        if cv.waitKey(0) & 0xFF == ord("q"):
            break


if "__main__" == __name__:
    main()

