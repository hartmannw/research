import numpy as np
from hartmann.asr import MOG
from hartmann.asr import HMM

class HMMSet:
    def __init__(self, hmm = [], model = [], transition = []):
        self.hmm = hmm
        self.model = model
        self.transition = transition
        self.ci_index = {}
        self.cd_index = {}

    def build_ci_index(self):
        for i,h in enumerate(self.hmm):
            idx = h.context[h.center]
            if idx not in self.ci_index:
                self.ci_index[idx] = []
            self.ci_index.get(idx, []).append(i)

    # We assume the context is a unique identifier of an HMM.
    def build_cd_index(self):
        for i,h in enumerate(self.hmm):
            self.cd_index[ h.context_id() ] = i

    # Any transitions which are currently the same value will be tied together.
    def reduce_transitions(self):
        tset = {}
        tindex = {}
        for i,t in enumerate(self.transition):
            if t not in tset:
                tset[t] = []
            tset[t].append(i)
        
        # Create the reduced set of transition models.
        self.transition = []
        for key, value in tset.items():
            self.transition.append(key)
            idx = len(self.transition) - 1
            for v in value:
                tindex[v] = idx
        for hi,h in enumerate(self.hmm):
            for ti,t in enumerate(h.transitionid):
                newval = tindex[t]
                self.hmm[hi].transitionid[ti] = tindex[t]

    def create_hmm_tiedlist(self):
        tiedlist = {}
        for i,h in enumerate(self.hmm):
            idx = h.model_id()
            if idx not in tiedlist:
                tiedlist[idx] = []
            tiedlist[idx].append(i)
        ret = []
        for key, value in tiedlist.items():
            ret.append(value)
        return ret


    def information(self):
        total_gaussians = 0
        for mog in self.model:
            total_gaussians += mog.components
        info = "Total HMMs: {:d}\nTotal Models: {:d}\n"
        info += "Total Transitions: {:d}\n"
        info += "Total Guassians: {:d}\n"
        info += "Gaussians per Model: {:f}\n"
        return info.format(len(self.hmm), len(self.model), 
                len(self.transition), total_gaussians, 
                (total_gaussians * 1.0) / len(self.model))


    def verify(self):
        # Check that all transition probabilities are >= 0 and <= 1.
        for t in self.transition:
            if t < 0 or t > 1:
                raise ValueError(' invalid transition probability.')

        # Check that all models are valid.
        for m in self.model:
            m.verify()

        # Confirm that all HMM information indices are valid.
        for h in self.hmm:
            for t in h.transitionid:
                if t < 0 or t >= len(self.transition):
                    print len(self.transition)
                    raise IndexError('invalid transition id {:d} for HMM {:s}.'
                            .format(t, h.context_id() + "x" + h.model_id()))
            for m in h.modelid:
                if m < 0 or m >= len(self.model):
                    raise IndexError(' invalid model id.')
