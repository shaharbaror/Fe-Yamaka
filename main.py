import cv2
import numpy as np
import multiprocessing


class Cam:
    def __init__(self, cam_number):
        self.cam_number = cam_number
        self.cam = cv2.VideoCapture(cam_number)

    @staticmethod
    def mask_red(frame):

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # lower boundary RED color range values; Hue (0 - 10)
        lower1 = np.array([0, 70, 50])
        upper1 = np.array([10, 255, 255])

        # upper boundary RED color range values; Hue (160 - 180)
        lower2 = np.array([160, 70, 50])
        upper2 = np.array([179, 255, 255])

        lower_mask = cv2.inRange(hsv_frame, lower1, upper1)
        upper_mask = cv2.inRange(hsv_frame, lower2, upper2)

        full_mask = lower_mask + upper_mask
        return full_mask    # returns the mask of the color red

    @staticmethod
    def get_optical_flow_but_not_really(current_frame, last_frame):
        mask = np.absolute(current_frame - last_frame)
        lower1 = np.array([50, 50, 50])
        upper1 = np.array([255, 255, 255])
        first_mask = cv2.inRange(mask, lower1, upper1)


        return first_mask

    @staticmethod
    def get_optical_flow(current_frame, last_frame, mask_got):
        mask = mask_got
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(last_frame, gray,
                                           None,
                                           0.5, 3, 15, 3, 5, 1.2, 0)

        # Computes the magnitude and angle of the 2D vectors
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Sets image hue according to the optical flow
        # direction
        mask[..., 0] = angle * 180 / np.pi / 2

        # Sets image value according to the optical flow
        # magnitude (normalized)
        mask[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

        # # Converts HSV to RGB (BGR) color representation
        rgb = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)
        low = np.array([100,100,100])
        high = np.array([255,255,255])
        return cv2.inRange(rgb, low, high)

def main():
    cam = Cam(0)
    res, frame = cam.cam.read()
    mask = np.zeros_like(frame)
    with multiprocessing.Pool(8) as p:
        while res:
            last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # get the last frame for movement detection
            res, frame = cam.cam.read()

            optical_mask = p.apply_async( cam.get_optical_flow, args=(frame, last_frame, mask,))
            masked_red =p.apply_async(cam.mask_red, args=(frame,))    # get only the red parts in the frame

            cv2.imshow("h", cv2.multiply(optical_mask.get(), masked_red.get() ))  # shows only whats red and moving
            # cv2.imshow("optical_mask", optical_mask)
            # cv2.imshow("red_masked", masked_red)    # show the frame masked to read
            cv2.imshow("frame", frame)

            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()
    while res:
        last_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # get the last frame for movement detection
        res, frame = cam.cam.read()

        optical_mask = cam.get_optical_flow(frame, last_frame, mask,)
        masked_red = cam.mask_red(frame)  # get only the red parts in the frame

        cv2.imshow("h", cv2.multiply(optical_mask, masked_red))  # shows only whats red and moving
        # cv2.imshow("optical_mask", optical_mask)
        # cv2.imshow("red_masked", masked_red)    # show the frame masked to read
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) == 27:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
