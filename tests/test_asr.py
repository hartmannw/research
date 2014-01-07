import unittest
import random
import copy
import numpy as np
import hartmann.asr as asr

class TestASR(unittest.TestCase):

    def setUp(self):
        dim = random.randrange(5,15)
        self.gaussian = asr.Gaussian.with_dimension( dim )
        gset = [ asr.Gaussian.with_dimension( dim ) for x in range(10) ]
        weight = np.random.uniform(0, 1, size=10)
        self.mog = asr.MOG(gset, weight)

    def test_guassian_dimension(self):
        self.assertTrue( self.gaussian.dimension == 
                len(self.gaussian.mean) )
        self.assertTrue( self.gaussian.dimension == 
                len(self.gaussian.variance) )

    def test_gaussian_variance(self):
        for v in self.gaussian.variance:
            self.assertTrue( v > 0 )

    def test_gaussian_constant(self):
        self.assertTrue( self.gaussian.constant > 0 )

    def test_gaussian_likelihood(self):
        point = np.random.uniform(-1, 1, size=self.gaussian.dimension)
        self.assertTrue( self.gaussian.likelihood(point) > 0 )
    
    def test_gaussian_log_likelihood(self):
        point = np.random.uniform(-1, 1, size=self.gaussian.dimension)
        self.assertTrue( self.gaussian.log_likelihood(point) < 0 )

    def test_mog_components(self):
        self.assertTrue( self.mog.components == len(self.mog.gaussian) and
                len(self.mog.gaussian) == len(self.mog.weight))
    
    def test_mog_add_gaussian(self):
        components = self.mog.components
        self.mog.add_gaussian(self.gaussian, 0.5)
        self.assertTrue( (1 + components) == self.mog.components )

    def test_mog_normalize_weights(self):
        self.mog.normalize_weights()
        self.assertTrue( self.mog.weight.sum() == 1 )
    
    def test_mog_likelihood(self):
        point = np.random.uniform(-1, 1, size=self.mog.dimension)
        self.assertTrue( self.mog.likelihood(point) > 0 )
    
    def test_mog_log_likelihood(self):
        point = np.random.uniform(-1, 1, size=self.mog.dimension)
        self.assertTrue( self.mog.log_likelihood(point) < 0 )

    def test_mog_csd(self):
        mog1 = asr.MOG()
        mog1.add_gaussian(asr.Gaussian(np.array([0,0]), np.array([1,1])), 0.3)
        mog1.add_gaussian(asr.Gaussian(np.array([3,0]), np.array([1,1])), 0.3)
        mog1.add_gaussian(asr.Gaussian(np.array([8,0]), np.array([1,1])), 0.4)
        a = []
        b = []
        for x in xrange(-20, 21):
            mog2 = copy.deepcopy(mog1)
            for g in mog2.gaussian:
                g.mean[1] += x
            a.append(mog1.csd(mog2))
            b.append(mog2.csd(mog1))
        for x, y in zip(a,b):
            self.assertEqual(x, y)
        self.assertAlmostEqual(a[0], 100.0)
        self.assertAlmostEqual(a[10], 25.0)
        self.assertAlmostEqual(a[20], 0.0)
        self.assertAlmostEqual(a[32], 36.0)
        self.assertAlmostEqual(a[34], 49.0)

if __name__ == '__main__':
    unittest.main()
