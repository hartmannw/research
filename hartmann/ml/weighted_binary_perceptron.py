import re
import random

class WeightedBinaryPerceptron:
    def __init__(self):
        self.weight = []
        self.data = {}
        self.learning_rate = 1.0
        self.update_count = 0
        self.cv_id = []
        self.train_id = []

    def LoadTrainingData(self, filename):
        index = 0
        with open(filename) as fin:
            for line in fin:
                # Load training data + bias.
                self.data[index] = [1] + [float(x) for x in data.split()]
                index = index + 1
        self.train_id = self.data.keys()
        random.shuffle(self.train_id)

    def MakeTrainingCVSplit(self, cv_percentage):
        if cv_percentage < 0 or cv_percentage >= 1:
            raise ValueError('CV Percentage must be between 0 and 1.')
        self.train_id = []
        self.cv_id = []
        id_set = self.data.keys()
        cv_count = int(len(id_set))
        random.shuffle(id_set)
        self.train_id = id_set[cv_count:]
        self.cv_id = id_set[:cv_count]

    def InitializeWeights(self, magnitude=1.0):
        if magnitude < 0:
            raise ValueError('The magnitude of the weight vector values must be non-negative.')
        if len(self.train_id) == 0:
            raise Exception('Cannot initialize weights without training data.')
        self.weight = 0
        for x in self.data[self.train_id[0]]:
            self.weight.append(random.uniform(-1.0, 1.0) * magnitude)
