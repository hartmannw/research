
# The assumption is that all actual information is stored elsewhere. This HMM 
# just contains indexes into the list of state models and transition models.
class HMM:
    def __init__(self, context = [], center = None, modelid = [], 
            transitionid = []):
        self.initialize(context, center, modelid, transitionid)

    def initialize(self,context, center, modelid, transitionid):
        self.context = context
        self.center = center
        self.modelid = modelid
        self.transitionid = transitionid

    # Make the number of transitions equal the number of states
    def fill_transitions(self):
        if len(self.transitionid) != len(self.modelid):
            self.transitionid = [None] * len(self.modelid)

    def context_id(self):
        return " ".join([str(x) for x in self.context])

    def model_id(self):
        return " ".join([str(x) for x in self.modelid]) + "&" + " ".join(
                [str(x) for x in self.transitionid])

