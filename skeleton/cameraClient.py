import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
import datetime
import socket as s
from skeleton.protocol import Protocol


from typing import List


class Camera:
    def __init__(self, what_to_see):
        self.cam = cv.VideoCapture(what_to_see)

        # let the video file or camera to load
        time.sleep(2.0)

    def get_frame(self):
        ret, frame = self.cam.read()
        if ret:
            return frame
        return None


class Maskinator (Camera):

    @staticmethod
    def ret_args(file_path):
        # construct the argument parse and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video", default=file_path,
                        help="path to the (optional) video file")
        ap.add_argument("-b", "--buffer", type=int, default=64,
                        help="max buffer size")

        return vars(ap.parse_args())    # returns the args

    def __init__(self, cam_num=None, file_path=""):

        self.args = self.ret_args(file_path)
        self.is_not_camera = self.args.get("video", False)

        # Set the ranges of colours that will be masked
        self.red_lower = (0, 50, 70)
        self.red_upper = (10, 255, 255)
        self.red_lower2 = (160, 86, 6)
        self.red_upper2 = (179, 255, 255)

        if self.is_not_camera:
            super(Maskinator, self).__init__(self.args["video"])
        else:
            super(Maskinator, self).__init__(cam_num)

    def locate_circles(self, frame):
        """
        gets a mask of the frame and returns all of the circle-like objects in it
        :param frame: a masked frame
        :return: List[List[float]] or None
        """
        circles = []

        # grabs all of the white objects in the mask
        cnts = cv.findContours(frame.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for c in cnts:
            # get the position of the object and the longest straight line / 2 that can be inside it
            # calculate the supposed area of the object if the longest line / 2 was the radius
            ((x, y), radius) = cv.minEnclosingCircle(c)
            supposed_area = radius ** 2 * np.pi * 0.6

            # compare the actual size of the object with the hypothetical size if it was a circle
            if supposed_area < cv.contourArea(c) < supposed_area * 1.5 and radius > 6:
                circles.append([x, y, radius, time.time()])

        return circles

    def pinpoint_cirlce(self, circles, frame, color):
        for c in circles:

            center = (int(c[0]), int(c[1]))
            # only proceed if the radius meets a minimum size
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv.circle(frame, (center), int(c[2]), color, 2)
            cv.circle(frame, center, 5, (0, 0, 255), -1)

    # Gets 3 frames with circles detected in them, and identify which of these circles are the same


class Linkudo:
    def __init__(self, value, nextt=None, found_circles=[]):
        self.value = value
        self.found_circles = found_circles
        self.nextt = nextt


class Client:
    def __init__(self):
        self.s = s.socket()
        self.s.connect(("172.16.20.69", 8000))

    def send_message(self, message):
        self.s.send(message)


class SingleCamera (Maskinator):
    def __init__(self, cam_num=None, file_path=""):
        # Initialize the classes for the cam and the linked list of frames
        super().__init__(cam_num, file_path)
        self.x = 0
        self.y = 1.5
        self.z = 2

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

        threshold = 250
        minimum = 10

        delta[delta > threshold] = 0
        delta[delta < minimum] = 0


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
                print(linked_list.value)
                image_delta = self.delta_calculation(linked_list.value, pos1.value)

                found_circles = self.locate_circles(image_delta)
                pos1.found_circles = found_circles

                if found_circles:
                    # since the comparison is between 2 frames the program also finds the balls on the older frame
                    real_findings = self.remove_old_circles(found_circles, linked_list.found_circles)
                    self.pinpoint_cirlce(real_findings, image_delta, (255, 0, 0))

                    # send the server the coordinates that the camera recognized
                    if real_findings:
                        real_findings = [[1], real_findings]
                        message = Protocol.prepare_message("circCords")
                        message = message + Protocol.prepare_message(str(real_findings)) + Protocol.prepare_message(str(time.time())) + Protocol.prepare_message(str([self.x, self.y, self.z]))
                        client.send_message(message)
                print(len(latest_frame))
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
    single_cam = SingleCamera(file_path="../3DCameras/Cam01/rec01.mp4")
    single_cam.record_cam(client)


if "__main__" == __name__:
    main()