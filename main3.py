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
        frame, ret = self.cam.read()
        if ret:
            return frame
        return None


# The class that defines a circle for use
class Circle:
    def __init__(self, x=None, y=None, radius=None, velocity=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity = velocity

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
        # mask the frame here and return the masked version
        return frame

    # Get a frame and return all the circles that are in it
    def locate_circles(self, frame) -> List[Circle]:
        circles = []
        return circles


def main():
    cam = Maskinator("./ball2.png")

    while True:
        frame = cam.get_frame(False)
        circles = cam.locate_circles(frame)

        cv.imshow("frame", frame)
        # if the user pressed "Q" end the program
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cv.destroyAllWindows()



if __name__ == "__main__":
    main()