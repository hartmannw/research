import math
import numpy as np
from  hartmann.asr import Gaussian

class MOG:
    def __init__(self, gaussian = [], weight = np.array([])):
        self.initialize(gaussian, weight)

    def initialize(self, gaussian, weight):
        self.gaussian = gaussian
        self.weight = weight
        self.check_components()
        self.csd_st_ = None

    def clear(self):
        self.gaussian = []
        self.weight = np.array([])
        self.csd_st_ = None

    def add_gaussian(self, gaussian, weight):
        self.gaussian.append(gaussian)
        self.weight = np.append(self.weight,weight)
        self.csd_st_ = None

    def normalize_weights(self):
        total = self.weight.sum()
        self.weight = self.weight / total
        self.csd_st_ = None

    def likelihood(self, point):
        result = 0
        for w, g in zip(self.weight, self.gaussian):
            result += w * g.likelihood(point)
        return result

    def log_likelihood(self, point):
        return np.log(self.likelihood(point))

    def csd(self, mog):
        first_term = 0
        second_term = 0
        third_term = 0
        for i in range(0, len(self.weight)):
            for j in range(0, len(mog.weight)):
                csd_term = mog.gaussian[j].csd_likelihood(self.gaussian[i])
                first_term += csd_term * self.weight[i] * mog.weight[j]
        #for w1, g1 in zip(self.weight, self.gaussian):
        #    for w2, g2, in zip(mog.weight, mog.gaussian):
                #g = Gaussian(g2.mean, g2.variance + g1.variance)
                #first_term += w1 * w2 * g.likelihood(g1.mean)
        #        first_term += w1 * w2 * g2.csd_likelihood(g1)
        #    for w2, g2, in zip(self.weight, self.gaussian):
        #        g = Gaussian(g2.mean, g2.variance + g1.variance)
        #        second_term += w1 * w2 * g.likelihood(g1.mean)
        #for w1, g1 in zip(mog.weight, mog.gaussian):
        #    for w2, g2, in zip(mog.weight, mog.gaussian):
        #        g = Gaussian(g2.mean, g2.variance + g1.variance)
        #        third_term += w1 * w2 * g.likelihood(g1.mean)
        second_term = self.csd_selfterm()
        third_term = mog.csd_selfterm()
        first_term = - np.log(first_term)
        second_term = 0.5 * np.log(second_term)
        third_term = 0.5 * np.log(third_term)
        return (first_term + second_term + third_term)

    # A portion of the CSD equation only relies on the data within the MOG. We 
    # store that result so we only have to compute it once.
    def csd_selfterm(self):
        if not self.csd_st_:
            self.csd_st_ = 0
            for w1, g1 in zip(self.weight, self.gaussian):
                for w2, g2, in zip(self.weight, self.gaussian):
                    g = Gaussian(g2.mean, g2.variance + g1.variance)
                    self.csd_st_ += w1 * w2 * g.likelihood(g1.mean)
        return self.csd_st_


    def verify(self):
        self.check_components()
        for g in self.gaussian:
            g.verify()

    def check_components(self):
        if len(self.weight) != len(self.gaussian):
            raise ValueError('length of weight vector does not match number' +
                    ' of Gaussians.')

    @property
    def components(self):
        self.check_components()
        return len(self.weight)

    @property
    def dimension(self):
        if self.components == 0:
            return 0
        return self.gaussian[0].dimension
