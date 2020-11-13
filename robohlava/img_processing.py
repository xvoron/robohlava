"""
Module image processing

image processing functions and utilities

"""
import os
import cv2
import numpy as np
import collections
import robohlava.config as config

import pytesseract
from PIL import Image
import re


def object_detect_yolo(img, net, base_dir):
    # TODO
    text = ""
    # Load Yolo
    classes = []
    # base_dir = r'C:\Users\karas\PycharmProjects\robohlava_2020'
    coco_names_path = os.path.join(base_dir +
                                   # r'\models\yolo\coco.names')
                                    r'/models/yolo/coco.names')
    with open(coco_names_path, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    # Loading image
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape
    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y + 30), font, 3, color, 3)
            text = text + label + " , "
    cv2.imshow("Image", img)
    eng_text = ["person", "tie", "backpack", "bottle", "cup", "banana", "apple", "sandwich", "orange",
                "chair", "diningtable", "tvmonitor", "laptop", "mouse", "remote", "keyboard",
                "cell phone", "book", "clock" "pottedplant"]
    cz_text = ["človeka", "kravatu", "batoh", "lahev", "hrnek", "banan", "jabko", "chlebiček", "pomeranč",
               "židle", "stul", "obrazovku", "počitač", "myš", "dalkové ovladaní", "klavisnice",
               "telefon", "knihu", "hodinky", "květ"]
    dict_eng_cz = dict(zip(eng_text, cz_text))
    text_to_voice_cz = replace_all(text, dict_eng_cz)
    if len(text_to_voice_cz) < 3:
        text_to_voice_cz_final = "Nic nevidím"
    else:
        text_final = ""
        words = text_to_voice_cz.split()
        word_counts = collections.Counter(words)
        for word, count in sorted(word_counts.items()):
            if count > 1:
                if word == "človeka":
                    text_final = text_final  + str(count) +  " lidi "
                else:
                    text_final = text_final + " , " + word
            else:
                text_final = text_final +  " , " + word + " , "
        text_to_voice_cz_final = "Vidím před sebou " + text_final
    return text_to_voice_cz_final


def object_detect_yolo_realtime(img, net, base_dir):
    # TODO
    text = ""
    # Load Yolo
    classes = []
    # base_dir = r'C:\Users\karas\PycharmProjects\robohlava_2020'
    coco_names_path = os.path.join(base_dir +
                                   # r'\models\yolo\coco.names')
                                    r'/models/yolo/coco.names')
    with open(coco_names_path, "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    # Loading image
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape
    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y + 30), font, 3, color, 3)
    # cv2.imshow("Image", img)
    return img

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def remove_duplicates(text):
    s = []
    if len(text) > 1:
        for item in text:
            if item not in s:
                s.append(item)
    else:
        s = text
    return s



def obj_det_ssd_mobilenet(img,net,classes):
    pass

    # text_to_voice_eng = ""
    # colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # img_to_cuda = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
    # cuda_img = jetson.utils.cudaFromNumpy(img_to_cuda)
    # detections = net.Detect(cuda_img, 640, 480)

    # for detection in detections:
    #     box = (int(detection.Left),
    #            int(detection.Top),
    #            int(detection.Right),
    #            int(detection.Bottom))

    #     (startX, startY, endX, endY) = box
    #     text = (str(classes[detection.ClassID]) + " " +
    #             str(int(detection.Confidence*100)) + "%")

    #     text_to_voice_eng = text_to_voice_eng + str(classes[detection.ClassID]) + " , "

    #     cv2.rectangle(img, (startX, startY),(endX, endY),(255,0,0),2)
    #     cv2.putText(img, text, (startX, startY + 30),
    #                         cv2.FONT_HERSHEY_PLAIN,2,(0,255,0),2)
    #
    #
    # cv2.imshow("Image", img)

    # eng_text = ["person", "tie", "backpack", "bottle", "cup", "banana", "apple", "sandwich",
    #             "orange",
    #             "chair", "diningtable", "tvmonitor", "laptop", "mouse", "remote", "keyboard",
    #             "cell phone", "book", "clock"]
    # cz_text = ["človeka", "kravatu", "batoh", "lahev", "hrnek", "banan", "jabko", "chlebiček",
    #            "pomeranč",
    #            "židle", "stul", "obrazovku", "počitač", "myš", "dalkové ovladaní", "klavisnice",
    #            "telefon", "knihu", "hodinky"]
    # dict_eng_cz = dict(zip(eng_text, cz_text))
    # text_to_voice_cz = replace_all(text_to_voice_eng, dict_eng_cz)
    # print(text_to_voice_cz)
    # cv2.destroyWindow("Image")
    # return text_to_voice_cz



def pytessaract_book(image):
    """
    Search a text in rur.txt file.

    Take an input image, translate text to string with pytesserakt library.
    Search same string in file rur.txt.
    x and y are start and end points in text line.

    Example x = 5 y = 10
    Hello| how |are you?
         x     y
    and after iteration increase x and y.
    :param image:
    :return:
    """

    print("[img_processing.pytessaract_book] Started to search text from image.")
    text = pytesseract.image_to_string(Image.fromarray(image), lang="ces")
    text_new = re.sub('[^.,:!?\w]', ' ', text)
    print("[Text from image]" + text_new)
    result = None

    if bool(text_new.strip()) and len(text_new) > 70:
        text_rur = open(r'C:\Users\karas\PycharmProjects\robohlava_2020\txt_file\rur.txt', 'r', encoding="utf8").read()
        text_rur_new = re.sub('[^.,:!?\w]', ' ', text_rur)
        x = 10
        y = 30
        a = None
        delka = len(text_new)
        while True:
            a = text_rur_new.find(text_new[x:y])
            if a != -1 and a != 0:
                print("\n[Find]")
                print(a)
                x = 10
                y = 30
                result = re.sub('[^,.\w]', ' ', text_rur[a:a + 300])
                print("[Text to voice] " + result)
                a = None
                cv2.destroyWindow("Image_for_search")
                break
            x = y
            y = y + 20
            if y > delka:
                break
    return result


def age_gender_prediction(frame, faceNet, ageNet, genderNet, minConf=0.5):
    # define the list of age buckets our age detector will predict
    AGE_BUCKETS = ["(0-2)", "(4-6)", "(8-12)", "(15-20)", "(25-32)",
                   "(38-43)", "(48-53)", "(60-100)"]

    GENDER_BUCKETS = ["Male", "Female"]

    # initialize our results list
    results = []

    # grab the dimensions of the frame and then construct a blob
    # from it
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
                                 (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the face detections
    faceNet.setInput(blob)
    detections = faceNet.forward()


    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the confidence is
        # greater than the minimum confidence
        if confidence > minConf:
            # compute the (x, y)-coordinates of the bounding box for
            # the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # extract the ROI of the face
            face = frame[startY:endY, startX:endX]

            # ensure the face ROI is sufficiently large
            if face.shape[0] < 20 or face.shape[1] < 20:
                continue

            # construct a blob from *just* the face ROI
            faceBlob = cv2.dnn.blobFromImage(face, 1.0, (227, 227),
                                             (78.4263377603, 87.7689143744, 114.895847746),
                                             swapRB=False)

            # make predictions on the age and find the age bucket with
            # the largest corresponding probability
            ageNet.setInput(faceBlob)
            preds = ageNet.forward()
            i = preds[0].argmax()
            age = AGE_BUCKETS[i]
            ageConfidence = preds[0][i]

            blob = cv2.dnn.blobFromImage(face, 1, (227, 227),
                                         (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = GENDER_BUCKETS[genderPreds[0].argmax()]
            # construct a dictionary consisting of both the face
            # bounding box location along with the age prediction,
            # then update our results list
            d = {
                "loc": (startX, startY, endX, endY),
                "age": (age, ageConfidence),
                "gender": gender
            }
            results.append(d)

    # return our results to the calling function
    return results




if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))
else:
    print("Modul  | {0} | ---> imported".format(__name__))







