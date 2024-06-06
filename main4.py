import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
import datetime
import socket as s
from skeleton.protocol import Protocol


from main3 import *

from typing import List
#
# def ShowFrame(cam:Maskinator):
#     frame, mask = cam.get_frame()
#     frame_circles = cam.locate_circles(mask)
#     # cam.pinpoint_cirlce(frame_circles, mask, (0, 255, 0))
#     # cam.pinpoint_cirlce(frame_circles, frame, (0, 255, 0))
#
#     return frame, mask
#
# def locate_circles(frame) -> List[List[float]] or None:
#     circles = []
#
#     cnts = cv.findContours(frame.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
#     cnts = imutils.grab_contours(cnts)
#
#     for c in cnts:
#
#         ((x, y), radius) = cv.minEnclosingCircle(c)
#         supposed_area = radius ** 2 * np.pi * 0.5
#
#         if supposed_area < cv.contourArea(c) < supposed_area * 1.5 and radius > 12:
#             circles.append([x, y, radius, time.time()])
#
#     return circles
#
# def delta_calculation(old_frame, new_frame):
#     color_type = cv.COLOR_BGR2GRAY
#     old_frame = cv.cvtColor(old_frame, color_type)
#     new_frame = cv.cvtColor(new_frame, color_type)
#
#     delta = np.absolute(new_frame - old_frame)
#
#
#     threshold = 230
#     min_amount = 10
#     delta[delta > threshold] = 0
#     delta[delta < min_amount] = 0
#     return delta

def calculate_distance(cam01:Maskinator, cam02:Maskinator, found_circs1, found_circs2):
    width1 = 1240
    width2 = 1240
    height = 1080
    height1 = width1 / 2
    height2 = width2 / 2

    dist_from_middle1 = found_circs1[0][0] - height1
    dist_from_middle2 = found_circs2[0][0] - height2

    height_dist1 = (height / 2) - found_circs1[0][1]
    height_dist2 = (height / 2) - found_circs2[0][1]

    tan_of1 = np.absolute(dist_from_middle1) / height1
    tan_of2 = np.absolute(dist_from_middle2) / height2
    print(f"the tans are: {tan_of1}, {tan_of2}")
    distance_between_cameras = 0.16
    z_distance = 0

    # h = X1 / [ tan(a) + tan(b) ]
    # dist = h / cos(a)
    if dist_from_middle1 <= 0 <= dist_from_middle2:
        z_distance = distance_between_cameras / (tan_of1 + tan_of2)
    elif dist_from_middle1 <= 0 and dist_from_middle2 <= 0:
        z_distance = distance_between_cameras / (tan_of1 - tan_of2)
    elif dist_from_middle1 >= 0 and dist_from_middle2 >= 0:
        z_distance = distance_between_cameras / (tan_of2 - tan_of1)

    distance_of_cam1 = z_distance / np.cos(np.tanh(tan_of1))
    distance_of_cam2 = z_distance / np.cos(np.tanh(tan_of2))

    height_of_cam1 = z_distance * np.sin(np.tanh(height_dist1 / height1))
    height_of_cam2 = z_distance * np.sin(np.tanh(height_dist2 / height2))
    print(f"TTTTTThe y is {height_of_cam1}")








class Linkudo:
    def __init__(self, value, nextt=None, found_circles=[]):
        self.value = value
        self.found_circles = found_circles
        self.nextt = nextt



# def main():
#     cam01 = Maskinator("./3DCameras/cam01/new_rec1.mp4")
#     cam02 = Maskinator("./3DCameras/cam02/new_rec1.mp4")
#
#     lasto_framo, _ = ShowFrame(cam01)
#     lasto_framo, _ = ShowFrame(cam01)
#     lasto_framo, _ = ShowFrame(cam01)
#     lasto_framo, _ = ShowFrame(cam01)
#     lasto_framo, _ = ShowFrame(cam01)
#     lasto_framo2, _ = ShowFrame(cam02)
#
#     list1 = Linkudo(lasto_framo)
#     pos1 = list1
#     count = 0
#
#     list2 = Linkudo(lasto_framo2)
#     pos2 = list2
#     count2 = 0
#
#
#     delay = True
#
#
#     while True:
#         curr_frame, _ = ShowFrame(0)
#         # curr_frame2, _ = ShowFrame(cam02)
#         shown_frame = curr_frame
#
#
#
#         pos1.nextt = Linkudo(curr_frame)
#         pos1 = pos1.nextt
#
#         # pos2.nextt = Linkudo(curr_frame2)
#         # pos2 = pos2.nextt
#
#         circ_of_1 = None
#         circ_of_2 = None
#
#         found_in_both = 0
#
#         if count > 3:
#             list1 = list1.nextt
#
#             delt = delta_calculation(list1.value, pos1.value)
#             found_circs = locate_circles(delt)
#
#             if found_circs:
#                 cam01.pinpoint_cirlce(found_circs, delt, (255, 0, 0))
#                 found_in_both += 1
#                 circ_of_1 = found_circs
#
#             #   It is currently finding the old circle too
#             #   i need to program it to ignore the old frame or to use it for detection
#             cv.imshow("dult", delt)
#         # if count2 > 3:
#         #     list2 = list2.nextt
#         #
#         #     delt = delta_calculation(list2.value, pos2.value)
#         #     found_circs = locate_circles(delt)
#         #
#         #     if found_circs:
#         #         cam02.pinpoint_cirlce(found_circs, delt, (255, 0, 0))
#         #         found_in_both += 1
#         #         circ_of_2 = found_circs
#         #
#         #     #   It is currently finding the old circle too
#         #     #   i need to program it to ignore the old frame or to use it for detection
#         #     cv.imshow("dult2", delt)
#         #
#         # if found_in_both == 2:
#         #     calculate_distance(cam01, cam02, circ_of_1, circ_of_2)
#
#         count += 1
#         count2 += 1
#         cv.imshow("furam", shown_frame)
#         # cv.imshow("turam", curr_frame2)
#
#         key = cv.waitKey(int(delay))
#         if key & 0xFF == ord("q"):
#             break
#         elif key & 0xFF == ord("k"):
#             delay = not delay

class Client:
    def __init__(self):
        self.s = s.socket()
        self.s.connect(("127.0.0.1", 8000))

    def send_message(self, message):
        self.s.send(message)



class SingleCamera (Maskinator):
    def __init__(self, cam_num=None, file_path=""):
        # Initialize the classes for the cam and the linked list of frames
        super().__init__(cam_num, file_path)

    def remove_old_circles(self, compared_circles: List[List[int]], old_circles):
        for i in old_circles:
            for j in compared_circles:
                if np.absolute(i[0] - j[0]) <= 20 >= np.absolute(i[1] - j[1]):
                    compared_circles.remove(j)
                    break
        return compared_circles

    def delta_calculation(self, old_frame, new_frame):
        color_type = cv.COLOR_BGR2GRAY
        old_frame = cv.cvtColor(old_frame, color_type)
        new_frame = cv.cvtColor(new_frame, color_type)

        delta = np.absolute(new_frame - old_frame)

        threshold = 230
        min_amount = 10
        delta[delta > threshold] = 0
        delta[delta < min_amount] = 0
        return delta

    def record_cam(self, client: Client):
        _, old_frame = self.cam.read()

        linked_list = Linkudo(old_frame)
        pos1 = linked_list

        frame_count = 0

        delay = False
        while True:
            _, latest_frame = self.cam.read()

            # add the latest frame to the frame list
            pos1.nextt = Linkudo(latest_frame)
            pos1 = pos1.nextt

            if frame_count > 2:
                linked_list = linked_list.nextt

                image_delta = self.delta_calculation(linked_list.value, pos1.value)

                found_circles = self.locate_circles(image_delta)
                pos1.found_circles = found_circles

                if found_circles:
                    # since the comparison is between 2 frames the program also finds the balls on the older frame
                    real_findings = self.remove_old_circles(found_circles, linked_list.found_circles)
                    self.pinpoint_cirlce(real_findings, image_delta, (255, 0, 0))

                    # send the server the coordinates that the camera recognized
                    if real_findings:
                        message = Protocol.prepare_message("circCords")
                        message = message + Protocol.prepare_message(str(real_findings) + Protocol.prepare_message(str(time.time())))
                        client.send_message(message)

                cv.imshow("v", image_delta)
                cv.imshow("n", latest_frame)

            frame_count += 1

            key = cv.waitKey(int(delay))
            if key & 0xFF == ord("q"):
                break
            elif key & 0xFF == ord("k"):
                delay = not delay



def main():
    client = Client()
    single_cam = SingleCamera(file_path="./3DCameras/cam01/new_rec1_Trim.mp4")
    single_cam.record_cam(client)


if "__main__" == __name__:
    main()