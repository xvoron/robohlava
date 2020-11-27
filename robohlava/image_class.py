import os
import numpy as np
import cv2
import pytesseract
import re
import platform
from PIL import Image


from robohlava.camera import Camera
from robohlava.person_class import Persons_class
from robohlava.detected_objects import DetectedObjects
import robohlava.config as conf


class ImageProcessing:
    """Represent class for Image capturing processing
    """

    def __init__(self):
        self.width = conf.WIDTH
        self.height = conf.HEIGHT

        self.centroid_to_arduino = None

        self.detected_objects = DetectedObjects()

        self.camera = Camera()

        self.PersonsObjects = None

        self.blank_image = None
        self.rgb_original = None
        self.rgb_copy_cv = None
        self.depth = None
        self.depth_colorized = None

        self.final_image = None
        self.book_text = None

        self.img_mini_persons_objects = None

        self.TIMER = 0
        self.info = {}

        if __name__ == "__main__":
            if platform.system() == "Windows":
                self.base_dir = os.getcwd() + "\\.."
            else:
                self.base_dir = os.getcwd() + "/.."
        else:
            self.base_dir = os.getcwd()  # + "\\.."

        print("[INFO] Base dir is ", self.base_dir)

        print("[INFO] Starting load models ...")

        if platform.system() == "Windows":

            """Define path and load face_detector"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'\models\face_detector\deploy.prototxt')
            weights_path = os.path.join(self.base_dir +
                                        r'\models\face_detector\weights.caffemodel')

            self.face_net = cv2.dnn.readNetFromCaffe(prototxt_path, weights_path)
            self.face_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.face_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

            """Define path and load YOLO object detection model"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'\models\yolo\yolov3.cfg')
            weights_path = os.path.join(self.base_dir +
                                        r'\models\yolo\yolov3.weights')

            self.yolo_net = cv2.dnn.readNetFromDarknet(prototxt_path, weights_path)
            self.yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

            """Define path and load face_detector2"""
            #prototxt_path = os.path.join(self.base_dir +
            #                             r'\models\face_detector_new\deploy.prototxt')
            #weights_path = os.path.join(self.base_dir +
            #                            r'\models\face_detector_new\res10_300x300_ssd_iter_140000.caffemodel')

            #self.face_net2 = cv2.dnn.readNet(prototxt_path, weights_path)

            """Define path and load age detector"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'\models\age_detector\age_deploy.prototxt')
            weights_path = os.path.join(self.base_dir +
                                        r'\models\age_detector\age_net.caffemodel')

            self.age_net = cv2.dnn.readNetFromCaffe(prototxt_path, weights_path)
            self.age_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.age_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

            """Define path and load gender detector"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'\models\gender_detector\deploy_gender.prototxt')
            weights_path = os.path.join(self.base_dir +
                                        r'\models\gender_detector\gender_net.caffemodel')

            self.gender_net = cv2.dnn.readNetFromCaffe(prototxt_path, weights_path)
            self.gender_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.gender_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        else:

            """Define path and load face_detector"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'/models/face_detector/deploy.prototxt')
            weights_path = os.path.join(self.base_dir +
                                        r'/models/face_detector/weights.caffemodel')

            self.face_net = cv2.dnn.readNetFromCaffe(prototxt_path, weights_path)

            """Define path and load YOLO object detection model"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'/models/yolo/yolov3.cfg')
            weights_path = os.path.join(self.base_dir +
                                        r'/models/yolo/yolov3.weights')

            self.yolo_net = cv2.dnn.readNetFromDarknet(prototxt_path, weights_path)

            """Define path and load face_detector2"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'/models/face_detector_new/deploy.prototxt')
            weights_path = os.path.join(self.base_dir +
                                        r'/models/face_detector_new/res10_300x300_ssd_iter_140000.caffemodel')

            self.face_net2 = cv2.dnn.readNet(prototxt_path, weights_path)

            """Define path and load age detector"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'/models/age_detector/age_deploy.prototxt')
            weights_path = os.path.join(self.base_dir +
                                        r'/models/age_detector/age_net.caffemodel')

            self.age_net = cv2.dnn.readNet(prototxt_path, weights_path)

            """Define path and load gender detector"""
            prototxt_path = os.path.join(self.base_dir +
                                         r'/models/gender_detector/deploy_gender.prototxt')
            weights_path = os.path.join(self.base_dir +
                                        r'/models/gender_detector/gender_net.caffemodel')

            self.gender_net = cv2.dnn.readNet(prototxt_path, weights_path)

        print("[INFO] Models was load")

        """Person class + tracker algorithm"""
        self.tracker = Persons_class()

    def book_read(self):
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

        # print("[img_processing.pytessaract_book] Started to search text from image.")
        text = pytesseract.image_to_string(Image.fromarray(self.rgb_original), lang="ces")
        text_new = re.sub('[^.,:!?\w]', ' ', text)
        if not text_new is None:
            #print("[Text from image]" + text_new)
            pass
        self.book_text = None

        if bool(text_new.strip()) and len(text_new) > 70:
            if platform == "Windows":
                text_rur = open(self.base_dir + r'\txt_file\rur.txt', 'r', encoding="utf8").read()
            else:
                text_rur = open(self.base_dir + r'/txt_file/rur.txt', 'r', encoding="utf8").read()

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
                    self.book_text = re.sub('[^,.\w]', ' ', text_rur[a:a + 200])
                    print("[Text to voice] " + self.book_text)
                    a = None
                    break
                x = y
                y = y + 20
                if y > delka:
                    break
        return self.book_text

    def obj_det_yolo(self):
        text = []
        # Load Yolo
        classes = []
        if platform.system() == "Windows":
            coco_names_path = os.path.join(self.base_dir +
                                           r'\models\yolo\coco.names')
        else:
            coco_names_path = os.path.join(self.base_dir +
                                           r'/models/yolo/coco.names')
        with open(coco_names_path, "r") as f:
            classes = [line.strip() for line in f.readlines()]
        layer_names = self.yolo_net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.yolo_net.getUnconnectedOutLayers()]
        #colors = np.random.uniform(0, 255, size=(len(classes), 3))
        # Loading image
        # img = cv2.resize(self.rgb_original, None, fx=0.4, fy=0.4)
        height, width, channels = self.rgb_original.shape
        # Detecting objects
        blob = cv2.dnn.blobFromImage(self.rgb_original, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.yolo_net.setInput(blob)
        outs = self.yolo_net.forward(output_layers)
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
                color_yolo = conf.color_yolo
                cv2.rectangle(self.rgb_copy_cv, (x, y), (x + w, y + h),
                        color_yolo, 2)
                cv2.putText(self.rgb_copy_cv, label, (x, y + 30), font, 2,
                        color_yolo, 2)
                text.append(label)
                obj_img = self.rgb_original[y:y+h, x:x+w]
                self.detected_objects.append(label, boxes[i], confidences[i], obj_img)
        self.objects_yolo.append(text)
        return

    def get_frames(self):
        self.rgb_original, self.depth, self.depth_colorized = self.camera.take_frame()
        self.rgb_copy_cv = np.copy(self.rgb_original)

    def centroid(self, persons_data_collection):
        self.PersonsObjects = self.tracker.update(persons_data_collection)

    def person_tracking(self, change_person=False):
        if len(list(self.PersonsObjects.values())) > 0:
            for person in list(self.PersonsObjects.values()):
                if person.tracking_person:
                    if change_person:
                        person.tracking_person = False
                    else:
                        return person
            max_area_index = np.argmax([person.area for person in list(self.PersonsObjects.values())])
            list(self.PersonsObjects.values())[max_area_index].tracking_person = True
            return list(self.PersonsObjects.values())[max_area_index]

    def face_age_gender_detector(self, age_flag=False, gender_flag=False):
        AGE_BUCKETS = ["(0-2)", "(4-6)", "(8-12)", "(15-20)", "(25-32)",
                       "(38-43)", "(48-53)", "(60-100)"]
        GENDER_BUCKETS = ["Male", "Female"]
        persons_data_collection = []
        model_mean_values = (78.4263377603, 87.7689143744, 114.895847746)

        (h, w) = self.rgb_original.shape[:2]

        face_blob = cv2.dnn.blobFromImage(cv2.resize(self.rgb_original,
                (300, 300)), 1.0, (300, 300), model_mean_values)
        self.face_net.setInput(face_blob)
        detections = self.face_net.forward()

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence < 0.5:
                continue
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            if self.rgb_original is not None:
                face_img = np.copy(self.rgb_original[startY:endY, startX:endX])
            else:
                continue
            if face_img.shape[0] < 15 or face_img.shape[1] < 15:
                continue

            try:
                face_img = cv2.resize(face_img, (227, 227), interpolation=cv2.INTER_CUBIC)
            except:
                continue
            
            if age_flag:
                age_blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227),
                                                 model_mean_values,
                                                 swapRB=True)
                self.age_net.setInput(age_blob)
                predictions = self.age_net.forward()

                i = predictions[0].argmax()
                age = AGE_BUCKETS[i]
                age_confidence = predictions[0][i]
            else:
                age = None
                age_confidence = None

            if gender_flag:
                gender_blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227),
                                                    model_mean_values, swapRB=False)
                self.gender_net.setInput(gender_blob)
                gender_preds = self.gender_net.forward()
                gender = GENDER_BUCKETS[gender_preds[0].argmax()]
            else:
                gender = None

            d = {
                "box": (startX, startY, endX, endY),
                "age": (age, age_confidence),
                "gender": gender,
                "img": np.asarray(face_img)
            }
            persons_data_collection.append(d)

        self.centroid(persons_data_collection)
        return self.centroid_to_arduino

    def draw_objects_persons(self):
        #TODO img to qt_label
        """ 640 x 480
            480/2 = 240 is height
            640/4 = 160 is width
            Frame:
            +---+---+---+---+
            |   |   |   |   |
            +---+---+---+---+
            |   |   |   |   |
            +---+---+---+---+
        """
        color_mini = conf.color_mini
        width = int(conf.WIDTH / 4)
        height = int(conf.HEIGHT / 2)
        if self.PersonsObjects == None:
            return np.zeros(1)
        else:
            img_mini = np.zeros(np.shape(self.rgb_original), np.uint8)
            if len(list(self.PersonsObjects.values())):
                for i, person in enumerate(list(self.PersonsObjects.values())):
                    if i > 4: # where 4 is maximum images per width frame
                        break
                    sX, sY, eX, eY = person.box
                    face_img = self.rgb_original[sY:eY, sX:eX]
                    face_img = cv2.resize(face_img, (width, height), interpolation=cv2.INTER_CUBIC)
                    img_mini[0:height, i*width:(i+1)*width] = face_img[0:height, 0:width]

        if not self.detected_objects.objects_list == []:
            i = 0
            for obj in (self.detected_objects.objects_list):
                if i > 4:   # where 4 is maximum images per width frame
                    break
                if obj.label == "person":
                    continue
                try:
                    obj_img = cv2.resize(obj.image, (width, height), interpolation=cv2.INTER_CUBIC)
                    cv2.putText(obj_img, str(str(obj.label) + "{:.2f}%".format(obj.confidence)), (5, 30),
                                cv2.FONT_HERSHEY_PLAIN, 2, color_mini, 2)
                    img_mini[height:2*height, i*width:(i+1)*width] = obj_img[0:height, 0:width]
                    i += 1
                except:
                    pass
        return img_mini

    def persons_draw(self):
        for person in list(self.PersonsObjects.values()):
            text = "ID: "
            for data in person.print_data:
                text += data + " "

            if person.tracking_person:
                color = conf.color_tracking_person
                text_tracking = "Tracking person"
            else:
                color = conf.color_person
                text_tracking = ""

            cv2.rectangle(self.rgb_copy_cv, (person.box[0], person.box[1]),
                          (person.box[2], person.box[3]), color, 2)
            cv2.circle(self.rgb_copy_cv, tuple(person.centroid), 2, color)
            cv2.putText(self.rgb_copy_cv, text, (person.box[0], person.box[1] - 15),
                        cv2.FONT_HERSHEY_PLAIN, 1, color, 1)
            cv2.putText(self.rgb_copy_cv, text_tracking, (person.box[0], person.box[1] - 35),
                        cv2.FONT_HERSHEY_PLAIN, 1, color, 1)

    def distance_process(self, box):
        (xmin_depth, ymin_depth, xmax_depth, ymax_depth) = box

        depth = self.depth[xmin_depth:xmax_depth,
                                 ymin_depth:ymax_depth].astype(float)
        depth_scale = self.camera.profile.get_device().first_depth_sensor().get_depth_scale()
        depth = depth * depth_scale
        dist, _, _, _ = cv2.mean(depth)
        return dist

    def show_frame(self):
        # legacy
        cv2.imshow("rgb", self.rgb_copy_cv)
        cv2.imshow("depth", self.depth_colorized)

    def draw_center_circle(self):
        cv2.circle(self.rgb_copy_cv, (int(self.width/2),
            int(self.height/2)), 50, conf.color_center_circle, 2)

    def draw_book_rectangle(self):
        cv2.rectangle(self.rgb_copy_cv,(50, 100), (int(self.width-50),
            int(self.height-30)), (0, 0, 139), 2)

    def return_image(self):
        return self.rgb_copy_cv

    def terminate(self):
        cv2.destroyAllWindows()
        self.camera.terminate()

    def show_init_window(self):
        if platform.system == "Windows":
            self.final_image = cv2.imread(self.base_dir + r"\images\looser.png")
        else:
            self.final_image = cv2.imread(self.base_dir + r"/images/looser.png")
        self.final_image = cv2.resize(self.final_image, (1920, 1080), interpolation=cv2.INTER_CUBIC)

    def update(self, flags):
        """Main update function
        flags:
            - track
            - face
            - age
            - gender
            - book
            - yolo
            - change_person
        return:
            - images:
                - final_img ???
                - rgb_copy_cv2
                - depth_colorized
                - rgb_original
            - persons
            - objects
        """

        self.objects_yolo = []
        self.get_frames()
        mini = self.blank_image = np.zeros(self.rgb_original.shape, np.uint8)

        if flags["track"] or flags['img_face']:
            self.face_age_gender_detector(flags['img_age'], flags['img_gender'])
            self.persons_draw()
            if flags["change_person"]:
                self.person_tracking(change_person=True)
            else:
                self.person_tracking(change_person=False)
            persons = list(self.PersonsObjects.values())
        else:
            persons = []
        if flags["img_yolo"]:
            self.obj_det_yolo()

        self.final_image = np.hstack((self.rgb_copy_cv, self.depth_colorized))
        if flags["img_book"]:
            self.book_read()
            self.book_text
            self.draw_book_rectangle()
        else:
            self.draw_center_circle()   # Draw center circle when its not a "book-mode"

        objects = self.objects_yolo
        #objects = self.detected_objects.objects_list

        if flags["disp_show_main"]:
            pass
        else:
            pass

        if flags["track"] or flags["img_yolo"]:
            mini = self.draw_objects_persons()

        if self.TIMER >= 300:
            self.detected_objects.clear()
            self.TIMER = 0


        self.TIMER += 1
        return (self.rgb_copy_cv, self.depth_colorized, mini, persons, objects, self.book_text)


if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))
    image_process = ImageProcessing()
    flags = {"img_arduino_track" : True,
            "img_yolo" : True,
            "change_person" : False,
            "img_book": False,
            "disp_show_main": False}
    while True:
        image_process.update(flags)
        image_process.draw_objects_persons()
        image_process.show_frame()

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            image_process.camera.terminate()
            cv2.destroyAllWindows()
            break

else:
    print("Modul  | {0} | ---> imported".format(__name__))
