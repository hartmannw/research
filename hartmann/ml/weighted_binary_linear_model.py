import math
import re
import random
import copy

class WeightedBinaryLinearModel:
    def __init__(self):
        self.model_type = "averaged_perceptron"
        self.weight = []
        self.data = []
        self.target = []
        self.learning_rate = 1.0
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
        for x in self.data[self.train_id[0]]:
            self.weight.append(random.uniform(-1.0, 1.0) * magnitude)

    def TrainModel(self, max_iterations=20):
        if self.model_type == "perceptron":
            self.TrainModelPerceptron(False, max_iterations)
        elif self.model_type == "averaged_perceptron":
            self.TrainModelPerceptron(True, max_iterations)


    def TrainIterationPerceptron(self, update_count=1, averaged=True):
        avgweight = copy.copy(self.weight)
        for i in self.train_id:
            guess = self.EvaluateItem(self.weight, self.data[i])
            if not self.SignMatch(self.target[i], guess):
                for wi, w in enumerate(self.weight):
                    self.weight[wi] = w + (self.target[i] * self.learning_rate * self.data[i][wi])
            for wi, w in enumerate(self.weight):
                inc = abs(self.target[i])
                avgweight[wi] = (((update_count-inc) / update_count) * avgweight[wi]) + (
                        (inc / update_count) * self.weight[wi])
            update_count = update_count + inc
        if averaged:
            self.weight = copy.copy(avgweight)
        return update_count

    def TrainModelPerceptron(self, averaged=True, max_iterations=20):
        if len(self.cv_id):
            evalset = self.cv_id
        else: # We have no CV set.
            evalset = self.train_id
        weight = copy.copy(self.weight)
        update_count = 1
        prev_llh = -1000000000
        llh = self.ScoreSubset(evalset, self.weight)
        iteration = 0
        while iteration < max_iterations and llh > prev_llh:
            weight = copy.copy(self.weight)
            update_count = self.TrainIterationPerceptron(update_count, averaged)
            prev_llh = llh
            llh = self.ScoreSubset(evalset, self.weight)
            print "Iteration", iteration, ": ", llh 
            iteration = iteration + 1
        if prev_llh > llh: # Last iteration was better
            self.weight = copy.copy(weight)

    # Instead of splitting the data into the folds evenly, the data is randomly
    # divided each time. The weights of the final model are averaged evenly
    # over each fold.
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
            for wi, w in enumerate(self.weight):
                weight[wi] = weight[wi] + ( (1.0 / num_folds) * w)
        self.weight = copy.copy(weight)

    def EvaluateData(self, idx, weight):
        ret = []
        for i in idx:
            score = self.EvaluateItem(weight, self.data[i])
            ret.append(math.exp(score) / (1 + math.exp(score)) )
        return ret

    # Scores are in terms of conditional log likelihood.
    def ScoreSubset(self, idx, weight):
        total_llh = 0.0
        for i in idx:
            guess = self.EvaluateItem(weight, self.data[i])
            if self.target[i] < 0:
                llh = math.log(1.0 / (1 + math.exp(guess)))
            else:
                llh = math.log(math.exp(guess) / (1 + math.exp(guess)))
            total_llh = total_llh + (abs(self.target[i]) * llh)
        return total_llh

    def ScoreCV(self):
        return self.ScoreSubset(self.cv_id, self.weight)
    
    def ScoreTrain(self):
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
