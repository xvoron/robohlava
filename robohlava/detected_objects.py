class DetectedObjects:
    def __init__(self):
        self.objects_list = []

    def append(self, label, box, confidence, image):
        if label not in [obj.label for obj in self.objects_list]:
            self.objects_list.append(DetectedObject(label, box, confidence, image))
        else:
            for obj in self.objects_list:
                if obj.label == label:
                    obj.update(box, confidence, image)

    def clear(self):
        del self.objects_list
        self.objects_list = []


class DetectedObject:
    def __init__(self, label, box, confidence, image):
        self.label = label
        self.box = box
        self.confidence = confidence
        self.image = image

    def update(self, box, confidence, image):
        self.box = box
        self.confidence = confidence
        self.image = image

    def __del__(self):
        pass

