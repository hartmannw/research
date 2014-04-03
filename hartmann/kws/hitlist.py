from  hartmann.kws import KWHit
import codecs
import re
from operator import attrgetter

class Hitlist:
    def __init__(self):
        self.hitlist = {}
        self.filename = None
        self.language = None
        self.systemid = None

    # Loads the XML formatted definition file. For each keyword, creates an 
    # empty list of hits in self.hitlist. Returns a dictionary mapping the 
    # keyword ID to the actual keyword.
    def LoadKeywordDefinition(self, filename):
        kwmap = {}
        kwid = ""
        kwtext = ""
        inkeyword = False
        with codecs.open(filename, mode='r', encoding='utf-8') as fin:
            for line in fin:
                if inkeyword:
                    if "</kw>" in line:
                        kwmap[kwid] = kwtext
                        self.hitlist[ kwid ] = []
                        inkeyword = False
                    elif "<kwtext>" in line:
                        kwtext = re.search('<kwtext>(.+)</kwtext>', line).group(1).strip()
                elif "<kw " in line:
                    inkeyword = True
                    kwid = re.search('kwid=\"([0-9A-Z\-\.]+)\"', line).group(1)
        return kwmap



    def LoadXML(self, filename):
        self.filename = filename
        self.hitlist = {} # Reset hitlist.
        kw = ""
        with codecs.open(filename, mode='r', encoding='utf-8') as fin:
            for line in fin:
                if "<detected_kwlist" in line:
                    kw = re.search('kwid=\"([0-9A-Z\-\.]+)\"', line).group(1)
                    self.hitlist[ kw ] = []
                elif "<kw " in line:
                    self.hitlist[kw].append(KWHit.From_XMLLine(line))
                elif "</detected_kwlist>" in line:
                    kw = ""

    def WriteXML(self, fout):
        #fout = codecs.getwriter('utf-8')(filename)
        fout.write('<kwslist system_id="{:s}" language="{:s}" kwlist_filename="{:s}">\n'.
                format(self.systemid, self.language, self.filename))
        for k in sorted(self.hitlist):
            fout.write('  <detected_kwlist kwid="' + k + '" search_time="1" oov_count="0">\n' )
            self.hitlist[k] = sorted(self.hitlist[k], key=attrgetter("score"), reverse=True)
            for x in self.hitlist.get(k, []):
                fout.write("    " + x.GetXMLLine() + "\n")
            fout.write("  </detected_kwlist>\n")
        fout.write('</kwslist>\n')

    # Search the current list of hits. If an overlapping hit exists, add the 
    # likelihood. If it does not exist, just append to the end.
    def AppendSum(self, kwid, kwhit):
        found = False
        for x in self.hitlist.get(kwid, []):
            if x.Overlap(kwhit) > 0.01:
                found = True
                if kwhit.score > x.score:
                    x.tbeg = kwhit.tbeg
                    x.dur = kwhit.dur
                x.score = x.score + kwhit.score
                break
        if not found:
            self.hitlist[kwid].append(kwhit)


    def PruneByCount(self, max_count):
        for k in self.hitlist:
            self.hitlist[k] = sorted(self.hitlist[k], key=attrgetter("score"), reverse=True)[:max_count]
    
    def PruneByScore(self, min_score):
        for k in self.hitlist:
            self.hitlist[k] = [hit for hit in self.hitlist[k] if hit.score >= min_score]
    
    def PruneByDecision(self):
        for k in self.hitlist:
            self.hitlist[k] = [hit for hit in self.hitlist[k] if hit.decision == "YES"]

    def MakeDecision(self, threshold):
        for k in self.hitlist:
            for x in self.hitlist[k]:
                if x.score >= threshold:
                    x.decision = "YES"
                else:
                    x.decision = "NO"

    def LinearScale(self, scale, offset):
        for k in self.hitlist:
            for x in self.hitlist[k]:
                x.score = (x.score * scale) + offset

    @property
    def keywords(self):
        return sorted(self.hitlist.keys())
