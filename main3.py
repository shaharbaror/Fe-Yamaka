import cv2 as cv
import numpy as np
from imutils.video import VideoStream
import argparse
import imutils
import time
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
    def __init__(self, x=None, y=None, radius=None, velocity=None, pure_object=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity = velocity
        self.pure_object = pure_object

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
    def locate_circles(self, frame) -> List[Circle]:
        circles = []

        cnts = cv.findContours(frame.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for c in cnts:
            ((x, y), radius) = cv.minEnclosingCircle(c)
            # c = max(cnts, key=cv2.contourArea)
            supposed_area = radius ** 2 * np.pi * 0.75
            if supposed_area < cv.contourArea(c) and cv.contourArea(c) < supposed_area * 1.5 and radius > 6:
                print("not a circle")
                print(cv.contourArea(c), " + ", supposed_area)
                circles.append(Circle(x=x, y=y, radius=radius, pure_object=c))

        return circles

    def pinpoint_cirlces(self, circles:  List[Circle], frame):
        for c in circles:

            center = (int(c.x), int(c.y))
            # only proceed if the radius meets a minimum size
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv.circle(frame, (center), int(c.radius), (0, 255, 255), 2)
            cv.circle(frame, center, 5, (0, 0, 255), -1)


def main():
    cam = Maskinator("./yus.mp4")

    while True:
        frame, mask = cam.get_frame()
        circles = cam.locate_circles(mask)
        cam.pinpoint_cirlces(circles, frame)

        cv.imshow("frame", frame)
        # if the user pressed "Q" end the program
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cv.destroyAllWindows()



if __name__ == "__main__":
    main()