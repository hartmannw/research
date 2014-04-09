import re
import random
import copy

class WeightedBinaryPerceptron:
    def __init__(self):
        self.weight = []
        self.avgweight = []
        self.data = []
        self.target = []
        self.learning_rate = 1.0
        self.update_count = 1
        self.cv_id = []
        self.train_id = []

    def ClearData(self):
        self.data = []
        self.target = []
        self.train_id = []
        self.cv_id = []

    def LoadTrainingData(self, filename):
        self.ClearData()
        with open(filename) as fin:
            for line in fin:
                # Load training data + bias.
                data = line.split()
                self.data.append([1] + [float(x) for x in data[:-1]])
                self.target.append(float(data[-1]))
        self.train_id = range(len(self.data))
        random.shuffle(self.train_id)

    def MakeTrainingCVSplit(self, cv_percentage):
        if cv_percentage < 0 or cv_percentage >= 1:
            raise ValueError('CV Percentage must be between 0 and 1.')
        self.train_id = []
        self.cv_id = []
        id_set = range(len(self.data))
        cv_count = int(len(id_set) * cv_percentage)
        random.shuffle(id_set)
        self.train_id = id_set[cv_count:]
        self.cv_id = id_set[:cv_count]

    def InitializeWeights(self, magnitude=1.0):
        if magnitude < 0:
            raise ValueError('The magnitude of the weight vector values must be non-negative.')
        if len(self.train_id) == 0:
            raise Exception('Cannot initialize weights without training data.')
        self.weight = []
        self.avgweight = []
        self.update_count = 1
        for x in self.data[self.train_id[0]]:
            self.weight.append(random.uniform(-1.0, 1.0) * magnitude)
        self.avgweight = copy.copy(self.weight)

    def TrainIteration(self):
        for i in self.train_id:
            guess = self.EvaluateItem(self.weight, self.data[i])
            if not self.SignMatch(self.target[i], guess):
                for wi, w in enumerate(self.weight):
                    self.weight[wi] = w + (self.target[i] * self.learning_rate * self.data[i][wi])
                    #self.avgweight[wi] = (((self.update_count-abs(self.target[i])) / self.update_count) * self.avgweight[wi]) + (
                    #        (abs(self.target[i]) / self.update_count) * self.weight[wi])
                #self.update_count = self.update_count + abs(self.target[i])
                #print i, guess, self.target[i]
                #print self.weight
                #print self.avgweight
            for wi, w in enumerate(self.weight):
                inc = abs(self.target[i])
                self.avgweight[wi] = (((self.update_count-inc) / self.update_count) * self.avgweight[wi]) + (
                        (inc / self.update_count) * self.weight[wi])
            self.update_count = self.update_count + inc

    def TrainModel(self, max_iterations=20):
        if len(self.cv_id):
            evalset = self.cv_id
        else: # We have no CV set.
            evalset = self.train_id
        weight = copy.copy(self.avgweight)
        prev_accuracy = -1
        accuracy = self.ScoreSubset(evalset, self.avgweight)
        iteration = 0
        while iteration < max_iterations and accuracy > prev_accuracy:
            weight = copy.copy(self.avgweight)
            self.TrainIteration()
            prev_accuracy = accuracy
            accuracy = self.ScoreSubset(evalset, self.avgweight)
            print "Iteration", iteration, ": ", accuracy 
            iteration = iteration + 1
        if prev_accuracy > accuracy: # Last iteration was better
            self.avgweight = copy.copy(weight)

    # Instead of splitting the data into the folds evenly, the data randomly
    # divided each time.
    def TrainModelFolds(self, num_folds):
        if num_folds == 1:
            self.TrainModel()
            return
        self.InitializeWeights(0.0)
        weight = copy.copy(self.weight)
        for i in range(num_folds):
            print "Fold: ", i
            self.MakeTrainingCVSplit(1.0 / num_folds)
            self.InitializeWeights(0.0)
            self.TrainModel()
            for wi, w in enumerate(self.avgweight):
                weight[wi] = weight[wi] + ( (1.0 / num_folds) * w)
        self.avgweight = copy.copy(weight)

    def EvaluateData(self, idx, weight):
        ret = []
        for i in idx:
            ret.append(self.EvaluateItem(weight, self.data[i]))
        return ret

    def ScoreSubset(self, idx, weight):
        total = 0.0
        correct = 0.0
        for i in idx:
            guess = self.EvaluateItem(weight, self.data[i])
            if self.SignMatch(self.target[i], guess):
                correct = correct + abs(self.target[i])
            total = total + abs(self.target[i])
        return correct / total

    def ScoreCV(self, average=True):
        if average:
            return self.ScoreSubset(self.cv_id, self.avgweight)
        return self.ScoreSubset(self.cv_id, self.weight)
    
    def ScoreTrain(self, average=True):
        if average:
            return self.ScoreSubset(self.train_id, self.avgweight)
        return self.ScoreSubset(self.train_id, self.weight)

    def EvaluateItem(self, weight, data):
        if len(weight) != len(data):
            raise Exception('Weights and data must be the same length')
        return sum([w*d for w,d in zip(weight, data)])

    def SignMatch(self, a, b):
        if a < 0 and b < 0:
            return True
        if a > 0 and b > 0:
            return True
        if a == 0 and b == 0:
            return True
        return False
