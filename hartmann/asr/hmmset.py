import numpy as np
import random
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
    # If a value is given to bins, then the transition probability space will 
    # be split across those bins+1, giving that number of total transition
    # models.
    def reduce_transitions(self, bins = 0):
        tset = {}
        tindex = {}
        if bins == 0:
            for i,t in enumerate(self.transition):
                if t not in tset:
                    tset[t] = []
                tset[t].append(i)
        else:
            for i,t in enumerate(self.transition):
                # We cannot have a transition probability of 0.
                val = (round(t * (bins-1)) + 1) / bins
                if val not in tset:
                    tset[val] = []
                tset[val].append(i)

        
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

    # Remove any hmms which contain one of the given phones as its center 
    # context.
    def remove_hmms(self, phones):
        reduced_hmms = []
        for hmm in self.hmm:
            if hmm.context[hmm.center] not in phones:
                reduced_hmms.append(hmm)
        self.hmm = reduced_hmms
        self.build_ci_index()
        self.build_cd_index()

    # No real purpose to this function other than reducing the size of the model
    # for testing purposes. Creates a single hmm for each center context.
    def convert_to_monophone(self):
        monohmm = {}
        for hmm in self.hmm:
            monohmm[hmm.context[hmm.center]] = hmm
        self.hmm = []
        for key, hmm in monohmm.iteritems():
            self.hmm.append(hmm)

        # Now we need to reduce the states
        modelmap = {}
        model_count = 0
        for hmm in self.hmm:
            for m in hmm.modelid:
                if m not in modelmap:
                    modelmap[m] = model_count
                    model_count = model_count + 1
        model = [None] * model_count
        for key, val in modelmap.iteritems():
            model[val] = self.model[key]
        self.model = model
        for hmm in self.hmm:
            for i,m in enumerate(hmm.modelid):
                hmm.modelid[i] = modelmap[m]

        self.build_ci_index()
        self.build_cd_index()

    def make_subset(self, hmmlist):
        subset_hmm = []
        for hmmid in hmmlist:
            subset_hmm.append(self.hmm[hmmid])
        self.hmm = subset_hmm
       
        # Now we need to reduce the states
        modelmap = {}
        model_count = 0
        for hmm in self.hmm:
            for m in hmm.modelid:
                if m not in modelmap:
                    modelmap[m] = model_count
                    model_count = model_count + 1
        model = [None] * model_count
        for key, val in modelmap.iteritems():
            model[val] = self.model[key]
        self.model = model
        for hmm in self.hmm:
            for i,m in enumerate(hmm.modelid):
                hmm.modelid[i] = modelmap[m]

        self.build_ci_index()
        self.build_cd_index()

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

    def compute_hmm_similarity(self, tiedlist):
        state_similarity = np.zeros( (len(self.model), len(self.model)) )
        for (i, j), value in np.ndenumerate(state_similarity):
            #state_similarity[i,j] = random.random()
            if i == j:
                state_similarity[i,j] = 1
                print "State similarity row: " + str(i) + " of " + str(len(self.model))
            elif i > j:
                state_similarity[i,j] = state_similarity[j,i]
            else:
                state_similarity[i,j] = 1 / (self.model[i].csd(self.model[j]) + 1)
            #print i,j,state_similarity[i,j]

        # Generate the list of location matrices
        location = []
        elength = []
        for hmmset in tiedlist:
            hmm = self.hmm[ hmmset[0] ]
            location.append(self.generate_location_matrix(hmm, 100))
            elength.append(np.sum(location[-1]))

        # Compute the hmm_similarity
        sm = np.zeros( (len(tiedlist), len(tiedlist)) )
        for (r,c), val in np.ndenumerate(sm):
            i = tiedlist[r][0]
            j = tiedlist[c][0]
            if r == c:
                print "HMM similarity row: " + str(r) + " of " + str(len(tiedlist))
            statesi = len(self.hmm[i].transitionid)
            statesj = len(self.hmm[j].transitionid)
            cor = np.zeros( (statesi, statesj) )

            cor_norm = max([elength[r], elength[c]])
            for (cor_r, cor_c), val in np.ndenumerate(cor):
                cor[cor_r,cor_c] = np.sum( np.multiply(location[r][cor_r,:], location[c][cor_c,:]) ) / cor_norm
                sm[r,c] += cor[cor_r,cor_c] * (state_similarity[ self.hmm[i].modelid[cor_r], self.hmm[j].modelid[cor_c] ])
        return sm



    def generate_location_matrix(self, hmm, steps):
        states = len(hmm.modelid)
        ret = np.zeros((states, steps))
        ret[0,0] = 1
        for t in range(1, steps):
            ret[0,t] = ret[0,t-1] * (1-self.transition[hmm.transitionid[0]])
            for s in range(1, states):
                ret[s,t] = ret[s,t-1] * (1-self.transition[hmm.transitionid[s]])
                ret[s,t] += ret[s-1,t-1] * self.transition[hmm.transitionid[s-1]]
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
