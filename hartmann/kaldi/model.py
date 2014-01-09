import copy
import numpy as np
import math
from hartmann.asr import HMMSet
from hartmann.asr import HMM
from hartmann.asr import MOG
from hartmann.asr import Gaussian

def load_gmm_hmm(ctxfile, modelfile):
    model = HMMSet()
    with open(ctxfile, 'r') as fin:
        for line in fin:
            # Prepare as if new HMM.
            data = [int(x) for x in line.strip().split()]
            hmm = HMM()
            hmm.context = data[2:]
            hmm.center = int(math.floor(len(hmm.context) / 2.0))
            # Check if this HMM already exists
            if hmm.context_id() in model.cd_index:
                idx = model.cd_index[hmm.context_id() ]
            else:
                model.hmm.append(copy.deepcopy(hmm))
                idx = len(model.hmm) - 1
                model.cd_index[hmm.context_id()] = idx
            hmm = model.hmm[idx]
            while len(hmm.modelid) <= data[1]: # Make sure we put the models in 
                hmm.modelid.append(None)       # the right place if presented 
            hmm.modelid[data[1]] = data[0]     # out of order.

    for h in model.hmm:
        h.fill_transitions()

    model.build_ci_index()
    model.build_cd_index()

    with open(modelfile, 'r') as fin:
        triple = []
        trans = []
        trans_count = {}
        line = fin.readline() # <TransitionModel>
        while '</Topology>' not in line:
            while '<ForPhones' not in line:
                line = fin.readline()
            phones = [int(x) for x in fin.readline().strip().split()]
            fin.readline() # </ForPhones>
            line = fin.readline() # First state
            state = 0
            while '<State>' in line:
                count = line.count('<Transition>')
                for p in phones:
                    trans_count[ str(p) + ' ' + str(state) ] = count
                state = state + 1
                line = fin.readline()
            line = fin.readline() # <Topology> or </TopologyEntry>
        while '<Triples>' not in line:
            line = fin.readline().strip()
        total = int(line.split()[1])
        for i in xrange(total):
            triple.append([int(x) for x in fin.readline().strip().split() ])
        fin.readline() # </Triples>
        fin.readline() # <LogProbs>
        line = fin.readline().strip()
        line = line.replace('[', '').replace(']', '')
        trans = [math.exp(float(x)) for x in line.strip().split()]
        idx = 1 # The transitions start counting at 1.
        for t in triple:
            model.transition.append( trans[idx] )
            # Add pointer to associated hmms (use reverse index)
            for hidx in model.ci_index.get(t[0], []):
                if t[1] < len(model.hmm[hidx].modelid) and model.hmm[hidx].modelid[t[1]] == t[2]:
                    model.hmm[hidx].transitionid[t[1]] = len(model.transition) - 1
            idx += trans_count[ str(t[0]) + ' ' + str(t[1]) ]

        # Now we read in the actual models (MOG).
        fin.readline()
        fin.readline() # </TransitionModel>
        line = fin.readline() # <DIMENSION> XX <NUMPDFS> XXXX <DiagGMM>
        data = line.split()
        dimension = int(data[1])
        numpdfs = int(data[3])
        mog = MOG()
        in_mean = False
        in_var = False
        mean = []
        var = []
        for line in fin:
            if "</DiagGMM>" in line:
                for g,m,v in zip(mog.gaussian, mean, var):
                    for i,x in enumerate(m):
                        g.variance[i] = 1 / v[i]
                        g.mean[i] = x * g.variance[i]
                model.model.append(copy.deepcopy(mog)) # Change mean/var ?
                mog.clear()
            elif "<WEIGHTS>" in line:
                weights = [float(x) for x in line.strip().split()[2:-1]]
                for w in weights:
                    mog.add_gaussian(Gaussian.with_dimension(dimension), w)
            elif "<MEANS_INVVARS>" in line:
                in_mean = True
                mean = []
            elif "<INV_VARS>" in line:
                in_var = True
                var = []
            elif in_mean:
                if ']' in line:
                    in_mean = False
                    mean.append([float(x) for x in line.strip().split()[:-1]])
                else:
                    mean.append([float(x) for x in line.strip().split()])
            elif in_var:
                if ']' in line:
                    in_var = False
                    var.append([float(x) for x in line.strip().split()[:-1]])
                else:
                    var.append([float(x) for x in line.strip().split()])

        model.verify()
        print model.information()
        model.reduce_transitions()
        model.verify()
        print model.information()
        tiedlist = model.create_hmm_tiedlist()
        print len(tiedlist)
        print model.hmm[0].model_id()
        print model.hmm[666].model_id()
        print model.hmm[43802].model_id()


