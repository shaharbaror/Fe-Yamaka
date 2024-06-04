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
    # cam.pinpoint_cirlce(frame_circles, mask, (0, 255, 0))
    # cam.pinpoint_cirlce(frame_circles, frame, (0, 255, 0))

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
    min_amount = 40
    delta[delta > threshold] = 0
    delta[delta < min_amount] = 0
    return delta

def calculate_distance(cam01:Maskinator, cam02:Maskinator, found_circs1, found_circs2):
    width1 = cam01.cam.get(3)
    width2 = cam02.cam.get(3)
    height1 = width1 / 2
    height2 = width2 / 2
    dist_from_middle1 = np.absolute(found_circs1[0][0] - height1)
    dist_from_middle2 = np.absolute(found_circs2[0][0] - height2)

    # h = X1 / [ tan(a) + tan(b) ]
    # dist = h / cos(a)

    print(f"cam-width:{width1}, distance from the middle:{dist_from_middle1}")
    print(f"cam-width*****2:{width2}, distance from the middle:{dist_from_middle2}")




class Linkudo:
    def __init__(self, value, nextt=None):
        self.value = value
        self.nextt = nextt


def main():
    cam01 = Maskinator("./3DCameras/cam01/recording03_Trim.mp4")
    cam02 = Maskinator("./3DCameras/cam02/recording01_Trim.mp4")

    lasto_framo, _ = ShowFrame(cam01)
    lasto_framo2, _ = ShowFrame(cam02)

    list1 = Linkudo(lasto_framo)
    pos1 = list1
    count = 0

    list2 = Linkudo(lasto_framo2)
    pos2 = list2
    count2 = 0


    while True:
        curr_frame, _ = ShowFrame(cam01)
        curr_frame2, _ = ShowFrame(cam02)
        shown_frame = curr_frame



        pos1.nextt = Linkudo(curr_frame)
        pos1 = pos1.nextt

        pos2.nextt = Linkudo(curr_frame2)
        pos2 = pos2.nextt

        circ_of_1 = None
        circ_of_2 = None

        found_in_both = 0

        if count > 3:
            list1 = list1.nextt

            delt = delta_calculation(list1.value, pos1.value)
            found_circs = locate_circles(delt)

            if found_circs:
                cam01.pinpoint_cirlce(found_circs, delt, (255, 0, 0))
                found_in_both += 1
                circ_of_1 = found_circs

            #   It is currently finding the old circle too
            #   i need to program it to ignore the old frame or to use it for detection
            cv.imshow("dult", delt)
        if count2 > 3:
            list2 = list2.nextt

            delt = delta_calculation(list2.value, pos2.value)
            found_circs = locate_circles(delt)

            if found_circs:
                cam02.pinpoint_cirlce(found_circs, delt, (255, 0, 0))
                found_in_both += 1
                circ_of_2 = found_circs

            #   It is currently finding the old circle too
            #   i need to program it to ignore the old frame or to use it for detection
            cv.imshow("dult2", delt)

        if found_in_both == 2:
            calculate_distance(cam01, cam02, circ_of_1, circ_of_2)

        count += 1
        count2 += 1
        cv.imshow("furam", shown_frame)
        cv.imshow("turam", curr_frame2)

        if cv.waitKey(0) & 0xFF == ord("q"):
            break


if "__main__" == __name__:
    main()

