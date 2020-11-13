"""
TEST Intel RealSense support with Jetson Nano

"""
import cv2
import numpy as np
import pyrealsense2 as rs


print("Import lib Done")
# inicialization Intel Realsense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# Start streaming
pipeline.start(config)
camera_str = "Intel RealSence"
print("Init camera: {0}".format(camera_str))
width = 640
height = 480

classes = []
with open("labels/class_labels.txt", "r") as f:
    classes = [line.strip() for line in f.readlines()]

print("Starting program...")
while True:
    """RealSence capture frame"""
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    if not depth_frame or not color_frame:
        continue
    
    # Convert images to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    image_to_yolo = color_image.copy()
    colorizer = rs.colorizer()
    colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
    
    img = cv2.cvtColor(color_image, cv2.COLOR_RGB2RGBA)

    color_depth_img = np.hstack((color_image, colorized_depth))
    cv2.imshow("Frame", color_depth_img)
    """Wait a key signal"""
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


cv2.destroyAllWindows()
pipeline.stop()
