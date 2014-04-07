import re

class KWHit:
    def __init__(self, score=-1, tbeg=0, dur=0, channel="1", filename=None, 
            decision=None):
        self.score = score
        self.tbeg = tbeg
        self.dur = dur
        self.channel = channel
        self.filename = filename
        self.decision = decision
        self.score_set = {}
        self.extra = {}

    @classmethod
    def From_XMLLine(cls, line):
        ret = cls()
        ret.ParseXMLLine(line)
        return ret

    def ParseXMLLine(self, line):
        self.extra["line"] = line
        self.score = float(re.search('score=\"([0-9\.\-e]+)\"', line).group(1))
        self.tbeg = float(re.search('tbeg=\"([0-9\.]+)\"', line).group(1))
        self.dur = float(re.search('dur=\"([0-9\.]+)\"', line).group(1))
        self.channel = re.search('channel=\"([0-9\.]+)\"', line).group(1)
        self.filename = re.search('file=\"([^\".]+)\"', line).group(1)
        self.decision = re.search('decision=\"([^\".]+)\"', line).group(1)

    def GetXMLLine(self):
        if self.score > 1:
            self.score = 1.0
        elif self.score < 0:
            self.score = 0
        ret = ("<kw tbeg=\"" + str(self.tbeg) + "\"" + 
                " dur=\"" + str(self.dur) + "\"" + 
                " file=\"" + self.filename + "\"" + 
                " score=\"" + "{:.6f}".format(self.score) + "\"" + 
                " channel=\"" + self.channel + "\"" + 
                " decision=\"" + self.decision + "\"" + 
                " />")
        return ret

    def Overlap(self, hit):
        if self.filename != hit.filename or self.channel != hit.channel:
            return 0 # Cannot overlap if from different files.

        starta = self.tbeg
        startb = hit.tbeg
        enda = starta + self.dur
        endb = startb + hit.dur
        overlap = max([min([enda, endb]) - max([starta, startb]), 0])
        return overlap

