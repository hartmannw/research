import numpy as np
from hartmann.asr import HMMSet
from hartmann.asr import HMM

def load_gmm_hmm(ctxfile, modelfile):
    model = HMMSet()
    with open(ctxfile, 'r') as fin:
        for line in fin:
            data = [int(x) for x in line.strip().split()]
            hmm = HMM()
            while len(hmm.modelid) < data[1]: # Make sure we put the models in 
                hmm.modelid.append(None)      # the right place if presented 
            hmm.modelid.append(data[0])       # out of order.
            hmm.context = data[2:]
            hmm.center = np.floor(len(hmm.context))
            model.hmm.append(hmm)


