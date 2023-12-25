import cv2
import numpy as np


class Cam:
    def __init__(self, cam_number):
        self.cam_number = cam_number
        self.cam = cv2.VideoCapture(cam_number)

    @staticmethod
    def mask_red(frame):

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # lower boundary RED color range values; Hue (0 - 10)
        lower1 = np.array([0, 70, 50])
        upper1 = np.array([20, 255, 255])

        # upper boundary RED color range values; Hue (160 - 180)
        lower2 = np.array([160, 70,50])
        upper2 = np.array([179, 255, 255])

        lower_mask = cv2.inRange(hsv_frame, lower1, upper1)
        upper_mask = cv2.inRange(hsv_frame, lower2, upper2)

        full_mask = lower_mask + upper_mask
        return full_mask    # returns the mask of the color red

    @staticmethod
    def get_optical_flow(current_frame, last_frame):
        mask = np.absolute(current_frame - last_frame)
        lower1 = np.array([100, 100, 100])
        upper1 = np.array([255, 255, 255])
        first_mask = cv2.inRange(mask, lower1, upper1)


        return first_mask


def main():
    cam = Cam(0)
    res, frame = cam.cam.read()
    while res:
        last_frame = frame  # get the last frame for movement detection
        res, frame = cam.cam.read()
        optical_mask = cam.get_optical_flow(frame, last_frame)
        masked_red = cam.mask_red(frame)    # get only the red parts in the frame
        cv2.imshow("optical_mask", optical_mask)
        cv2.imshow("red_masked", masked_red)    # show the frame masked to read
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
