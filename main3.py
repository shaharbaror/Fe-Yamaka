import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
import datetime

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


# The class that defines a circle for use
class Circle:
    def __init__(self, x=None, y=None, radius=None, velocity_x=None, velocity_y=None, time_of_record=None, pure_object=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.pure_object = pure_object
        self.time_of_record = time_of_record

    def calc_velocity(self, x, y, time_between):
        # Calculate the distance between the given position and the last recorded position of the circle
        distance_traveled = np.sqrt(np.power(self.x - x, 2) - np.power(self.y - y, 2))

        # Set the ball velocity by dividing the distance it traveled by the time it took it
        self.velocity = distance_traveled / time_between


# A child of "Camera" that mask the frames and do some extra calculation
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


    def get_frame(self, is_masked=True):
        frame = super(Maskinator, self).get_frame()

        frame = frame[1] if self.is_not_camera else frame
        if frame is None:
            return frame
        frame = imutils.resize(frame, width=600)
        # mask the frame here and return the masked version
        if not is_masked:
            return frame
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv.inRange(hsv, self.red_lower, self.red_upper)
        mask2 = cv.inRange(hsv, self.red_lower2, self.red_upper2)
        mask += mask2
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        return frame, mask

    # Get a frame and return all the circles that are in it
    def locate_circles(self, frame) -> List[List[float]]:
        circles = []

        cnts = cv.findContours(frame.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for c in cnts:

            ((x, y), radius) = cv.minEnclosingCircle(c)
            supposed_area = radius ** 2 * np.pi * 0.75

            if supposed_area < cv.contourArea(c) < supposed_area * 1.5 and radius > 6:
                circles.append([x, y, datetime.datetime.now()])

        return circles

    def pinpoint_cirlces(self, circles:  List[Circle], frame):
        for c in circles:

            center = (int(c.x), int(c.y))
            # only proceed if the radius meets a minimum size
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv.circle(frame, (center), int(c.radius), (0, 255, 255), 2)
            cv.circle(frame, center, 5, (0, 0, 255), -1)

    # Gets 3 frames with circles detected in them, and identify which of these circles are the same
    def identify_circles(self, circle_in_frame1, circle_in_frame2, circle_in_frame3, time_between1, time_between2):
        """
        :param circle_in_frame1: the list of all circles in the first frame
        :param circle_in_frame2: the list of all circles in the second frame
        :param circle_in_frame3: the list of all circles in the third frame
        :param time_between1: the time between the first and second frame
        :param time_between2: the time between the second and third frame

        :type circle_in_frame1: List[List[float]]
        :type circle_in_frame2: List[List[float]]
        :type circle_in_frame3: List[List[float]]
        :type time_between1: datetime.timedelta
        :type time_between2: datetime.timedelta

        :return: List[Circle]
        """

        def calc_next_pos(circle1, circle2):
            x_distance = circle1[0] - circle2[0]
            y_distance = circle1[1] - circle2[1]

            velocity_x = x_distance / time_between1
            velocity_y = y_distance / time_between1

            next_circle_x = circle2[0] + velocity_x * time_between2
            next_circle_y = circle2[1] + velocity_y * time_between2 - 5 * np.power(time_between2)
            next_circle = [next_circle_x, next_circle_y]

            if next_circle in circle_in_frame3:
                return Circle(x=next_circle_x,
                              y=next_circle_y,
                              radius=circle2[2],
                              velocity_x=velocity_x,
                              velocity_y=velocity_y,
                              time_of_record=datetime.datetime.now())
            return None

        returned_circles = []

        for i in range(len(circle_in_frame1)):
            for x in range(len(circle_in_frame2)):
                returned_circles.append(calc_next_pos(circle_in_frame1[i], circle_in_frame2[x]))

        return returned_circles


class P:
    def __init__(self, val=None, t=None, nexto=None):
        self.circ = val
        self.t = t
        self.next = nexto
def main():
    cam = Maskinator("./yus.mp4")
    circles = P()
    pos1 = circles
    done = 0
    while True:
        frame, mask = cam.get_frame()
        frame_circles = cam.locate_circles(mask)
        if 0 < done:

            pos1.next = P(frame_circles, datetime.datetime.now())
            pos1 = pos1.next
        if done > 4:

            circles = circles.next
            pos2 = circles.next
            print(circles.circ, pos2.circ, pos1.circ, pos2.t - circles.t, pos1.t - pos2.t)
            circle = cam.identify_circles(circles.circ, pos2.circ, pos1.circ, pos2.t - circles.t, pos1.t - pos2.t)
            print(circle)
            cam.pinpoint_cirlces(circle, frame)

        done += 1
        cv.imshow("frame", frame)
        # if the user pressed "Q" end the program
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cv.destroyAllWindows()



if __name__ == "__main__":
    main()