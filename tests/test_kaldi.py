import unittest
import hartmann.kaldi as kaldi

class TestKaldi(unittest.TestCase):

    def setUp(self):
        self.model = None
        self.ctxfile = '/people/hartmann/research/kaldi/analysis/ctxinfo_10fr_10cr.txt'
        self.modelfile = '/people/hartmann/research/kaldi/analysis/35_mdl_10fr_10cr.txt'

    def test_load_gmm_hmm(self):
        self.model = kaldi.model.load_gmm_hmm(self.ctxfile, self.modelfile)


if __name__ == '__main__':
    unittest.main()
