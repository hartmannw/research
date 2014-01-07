import numpy as np
from hartmann.asr import MOG
from hartmann.asr import HMM

class HMMSet:
    def __init__(self, hmm = [], model = [], transition = []):
        self.hmm = hmm
        self.model = model
        self.transition = transition
