import numpy as np
import pyrealsense2 as rs
import cv2
import robohlava.config as conf



class Camera:
    """Camera class represent a wrapper for RealSense camera.

    Provide initialization RealSense cam.
    Take and return processing frame as np.array by take_frame() function.
    Function frame_process() convert raw_frames from camera to np.array
    """

    def __init__(self):
        self.width = conf.WIDTH
        self.height = conf.HEIGHT
        self.real_sense_on = conf.flag_realsense

        """RealSence library and device initialization."""
        while True:
            if self.real_sense_on:
                try:
                    self.pipeline = rs.pipeline()
                    config = rs.config()
                    config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 30)
                    config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, 30)
                    self.profile = self.pipeline.start(config)
                    if self.pipeline:
                        break
                except:
                    continue
            else:
                self.cap = cv2.VideoCapture(-1)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                if not self.cap.isOpened():
                    raise IOError("Cannot open webcam")
                break

        self.rgb_frame = None
        self.depth_frame = None

        self.rgb_img = None
        self.depth_img = None
        self.colorized_depth = None
        print("[INFO] Camera initialization complete")

    def take_frame(self):
        while True:
            if self.real_sense_on:
                try:
                    frame = self.pipeline.wait_for_frames()
                    self.depth_frame = frame.get_depth_frame()
                    self.rgb_frame = frame.get_color_frame()
                    if not self.depth_frame or not self.rgb_frame:
                        """Return last image"""
                        continue
                    else:
                        """frames"""
                        self.frame_process()
                        break
                except:
                    continue
            else:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                else:
                    self.rgb_img = frame
                    self.depth_img = frame
                    self.colorized_depth = frame
                    break

        return self.rgb_img, self.depth_img, self.colorized_depth

    def frame_process(self):
        self.depth_img = np.asanyarray(self.depth_frame.get_data())
        self.rgb_img = np.asanyarray(self.rgb_frame.get_data())
        colorizer = rs.colorizer()
        self.colorized_depth = np.asanyarray(
            colorizer.colorize(self.depth_frame).get_data())

    def terminate(self):
        if self.real_sense_on:
            self.pipeline.stop()
            cv2.destroyAllWindows()
        else:
            self.cap.release()
            cv2.destroyAllWindows()
        print("[TERM] Camera is stoped")


if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))
    camera = Camera(640, 480)
    while True:
        img, _, _ = camera.take_frame()
        cv2.imshow("frame", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    camera.terminate()
else:
    print("Modul  | {0} | ---> imported".format(__name__))
