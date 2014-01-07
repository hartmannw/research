
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

