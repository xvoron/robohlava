import cv2
import os
import winsound

# from robohlava.image_class import Image
import robohlava.config as config
from robohlava.img_processing import age_gender_prediction
import pyrealsense2 as rs
import imutils
import numpy as np


base_dir = os.getcwd() + "\\.."
# base_dir = r'C:\Users\karas\Desktop\robohlava'
print("[INFO] Base dir is ", base_dir)
# load our serialized face detector model from disk
print("[INFO] loading face detector model...")
prototxtPath = os.path.join(base_dir + r'\models\face_detector_new\deploy.prototxt')
weightsPath = os.path.join(base_dir + r'\models\face_detector_new\res10_300x300_ssd_iter_140000.caffemodel')
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

# load our serialized age detector model from disk
print("[INFO] loading age detector model...")
prototxtPath = os.path.join(base_dir +
                            r'\models\age_detector\age_deploy.prototxt')
weightsPath = os.path.join(base_dir + r'\models\age_detector\age_net.caffemodel')
ageNet = cv2.dnn.readNet(prototxtPath, weightsPath)


prototxtPath = os.path.join(base_dir + r'\models\gender_detector\deploy_gender.prototxt')
weightsPath = os.path.join(base_dir + r'\models\gender_detector\gender_net.caffemodel')

genderNet = cv2.dnn.readNet(prototxtPath, weightsPath)
# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")

# image = Image(config.WIDTH, config.HEIGHT)

pipeline = rs.pipeline()
config_ = rs.config()
config_.enable_stream(rs.stream.depth, config.WIDTH, config.HEIGHT, rs.format.z16, 30)
config_.enable_stream(rs.stream.color, config.WIDTH, config.HEIGHT, rs.format.bgr8, 30)
# Start streaming
profile = pipeline.start(config_)
camera = "Intel RealSence"

r"""
mean_filename= base_dir + r'\models\age_detector\age_gender_mean.binaryproto'
proto_data = open(mean_filename, "rb").read()
a = cv2.caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
mean  = cv2.caffe.io.blobproto_to_array(a)[0]
"""

while True:
    frame = pipeline.wait_for_frames()
    depth_frame = frame.get_depth_frame()
    color_frame = frame.get_color_frame()
    if not depth_frame or not color_frame:
        continue
    color_image = np.asanyarray(color_frame.get_data())
    frame = imutils.resize(color_image, width=300)
    results = age_gender_prediction(frame, faceNet, ageNet, genderNet)

    for r in results:
        # draw the bounding box of the face along with the associated
        # predicted age
        text = "{} {}: {:.2f}%".format(r["gender"], r["age"][0], r["age"][1] * 100)
        (startX, startY, endX, endY) = r["loc"]
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),
                      (0, 0, 255), 2)
        cv2.putText(frame, text, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("p"):

        winsound.PlaySound(base_dir + r"\sound\snoring1.mp3", winsound.SND_ASYNC | winsound.SND_ALIAS)

    if key == ord("s"):
        winsound.PlaySound(None, winsound.SND_ASYNC)

    if key == ord("q"):
        break

