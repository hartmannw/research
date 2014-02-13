import numpy as np
import math

class Gaussian:
    def __init__(self, mean = np.array([]), variance = np.array([])):
        self.initialize(mean, variance)

    def __str__(self):
        return str(self.mean) + '\n' + str(self.variance)

    @classmethod
    def with_dimension(cls, dim):
        mean = np.zeros(dim)
        variance = np.ones(dim)
        return cls(mean, variance)

    def initialize(self, mean, variance):
        self.mean = mean
        self.variance = variance
        self._constant_valid = False
        self.dimension_check()

    # Determinant of a diagonal matrix is the product of the diagonal elements.
    def determinant(self):
        return self.variance.prod()

    def likelihood(self, point):
        if self.dimension != len(point):
            raise ValueError('dimension of point vector does not match ' +
                    'dimension of Gaussian.')
        #for x,m,v in zip(point, self.mean, self.variance):
        #    result += math.pow(m - x, 2.0) / v
        result = np.sum(np.divide(np.square(np.subtract(self.mean, point)), self.variance))
        return self.constant * math.exp(-0.5 * result)

    # Quickly generates the likelihood required by the CSD calculation.
    def csd_likelihood(self, g):
        variance = self.variance + g.variance
        result = np.sum(np.divide(np.square(np.subtract(self.mean, g.mean)), variance))
        return self.constant * math.exp(-0.5 * result) * self.variance.prod() / variance.prod()
    
    def log_likelihood(self, point):
        return np.log(self.likelihood(point))

    def dimension_check(self):
        if len(self.mean) != len(self.variance):
            raise ValueError('mean and variance not same dimension.')

    def verify(self):
        self.dimension_check()
        for v in self.variance:
            if v <= 0:
                raise ValueError(' invalid variance.')

    
    def set_mean(self, mean):
        self._constant_valid = False
        self.mean = mean
        self.dimension_check()
    
    def get_mean(self):
        return mean
    
    def set_variance(self, variance):
        self._constant_valid = False
        self.variance = variance
        self.dimension_check()

    def get_variance(self):
        return variance

    variance = property( get_variance, set_variance )
    mean = property( get_mean, set_mean )

    @property
    def constant(self):
        if not self._constant_valid:
            self.constant = 1 / (self.variance.prod() * math.pow(
                    2*np.pi, self.dimension / 2.0 ))
            self._constant_valid = True
        return self.constant

    @property
    def dimension(self):
        self.dimension_check()
        return len(self.mean)
