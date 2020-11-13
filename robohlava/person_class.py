from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


class Persons_class:
    #TODO Tracked using??
    def __init__(self, maxDisappeared=50):
        self.nextObjectID = 0
        self.objects = OrderedDict() # main information
        self.disappeared = OrderedDict()
        self.persons = [None] * 50

        self.maxDisappeared = maxDisappeared

        self.Person = Person_class

    def actual_number_of_person(self):
        return len(self.objects)

    def register(self, person):
        # when registering an object we use the next available object
        # ID to store the centroid
        self.objects[self.nextObjectID] = person
        self.objects[self.nextObjectID].ID = self.nextObjectID # TODO fungue?
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[objectID]
        del self.disappeared[objectID]

    def update(self, persons_data):
        # check to see if the list of input bounding box rectangles
        # is empty
        if self.nextObjectID >= 100:
            self.nextObjectID = 0

        if len(persons_data) == 0:
            # loop over any existing tracked objects and mark them
            # as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            return self.objects

        input_centroids = np.zeros((len(persons_data), 2), dtype="int")
        # initialize an array of input centroids for the current frame
        for (i, person_data) in enumerate(persons_data):
            startX, startY, endX, endY = person_data["box"]
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            input_centroids[i] = (cX, cY)
            person_data["centroid"] = (cX, cY)

            self.persons[i] = self.Person(person_data["box"],
                                          person_data["centroid"],
                                          person_data["age"],
                                          person_data["gender"],
                                          np.asarray(person_data["img"]))


        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):

                self.register(self.persons[i])

        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            objectIDs = list(self.objects.keys())
            objectCentroids = []
            for object in list(self.objects.values()):
                objectCentroids.append(object.centroid)

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            D = dist.cdist(np.array(objectCentroids), input_centroids)

            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value is at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in usedRows or col in usedCols:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                objectID = objectIDs[row]
                self.objects[objectID].update(
                                            persons_data[col]["box"],
                                            input_centroids[col],
                                            persons_data[col]["age"],
                                            persons_data[col]["gender"],
                                            persons_data[col]["img"]
                                            )
                self.disappeared[objectID] = 0

                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unusedRows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants deregistering the object
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            else:
                for col in unusedCols:
                    self.register(self.persons[col])    # .inputCentroids[col])

        # return the set of trackable objects
        return self.objects


class Person_class:
    """Represent data about person in frame.

                ID
           label + conf %
           age [n - n]
           gender [male/female]

        xmin +-------+ ymin
             |       |
             |   +   | centroid
             |       |
        xmax +-------+ ymax

    """
    def __init__(self, box, centroid, age, gender, img):

        self.xmin, self.ymin, self.xmax, self.ymax, = box
        self.box = box
        self.area = self.area_calc()
        self.centroid = centroid
        self.ID = None
        self.gender_list = [gender]
        self.age_list = [age[0]]
        self.age, self.age_confidence = age
        self.gender = gender
        self.image = img
        self.tracking_person = False

    def update(self, box, centroid, age, gender, img):
        self.box = box
        self.xmin, self.ymin, self.xmax, self.ymax = box
        self.centroid = centroid
        self.age_list.append(age[0])
        self.age_confidence = age[1]
        self.gender_list.append(gender)
        self.image = img
        self.age, self.gender = self.calc_average_data()
        self.area = self.area_calc()

        if len(self.age_list) > 10:
            self.age_list.pop(0)
            self.gender_list.pop(0)

    def get_image(self):
        pass

    def process_image(self):
        pass

    def area_calc(self):
        return int((self.xmax - self.xmin) * (self.ymax - self.ymin))

    def calc_average_data(self):
        return self.calc_mean(self.age_list), self.calc_mean(self.gender_list)

    def centroid_calc(self):
        return (int((self.xmax - self.xmin)/2) + self.xmin, int((self.ymax - self.ymin)/2) + self.ymin)

    def show(self):
        pass

    def attributes(self):
        """Some atributes for robohlava script
        """
        pass

    def calc_mean(self, list):
        return max(set(list), key=list.count)

if __name__ == "__main__":
    print("Modul  | {0} | ---> executed".format(__name__))
else:
    print("Modul  | {0} | ---> imported".format(__name__))
