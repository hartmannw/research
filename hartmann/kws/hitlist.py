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
        self.max_overlap = 0.01

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

    def InitializeScoreSet(self, id):
        for kw in self.hitlist:
            for hit in self.hitlist[kw]:
                hit.score_set[id] = hit.score

    # Merges the hits in the hitlist. Adds the score into the score set.
    def MergeHitlist(self, hitlist):
        # Get a list of all keywords.
        keywords = sorted(set(self.keywords + hitlist.keywords))

        for kw in keywords:
            self.hitlist[kw] = self.CompactKWHits(self.hitlist.get(kw, []) + hitlist.hitlist.get(kw,[]))

    def CompactKWHits(self, hits):
        ret = []
        hits = sorted(hits, key=attrgetter('filename', 'channel', 'tbeg'))
        for a in hits:
            if len(ret) > 0:
                b = ret[-1]
                if a.Overlap(b) > self.max_overlap:
                    for k, val in a.score_set.iteritems(): # Should only be 1.
                        if val > max(b.score_set.values()):
                            b.tbeg = a.tbeg
                            b.dur = a.dur
                        b.score_set[k] = max([val, b.score_set.get(k,0)])
                else:
                    ret.append(a)
            else:
                ret.append(a)
        return ret

    # Update the real score based on the score set.
    def UpdateScore(self, merge_type, score_set_size, threshold=0.5, unscored=False):
        for kw in self.keywords:
            for i,hit in enumerate(self.hitlist[kw]):
                if unscored: # Add score of 0 for any missing scores in score_set.
                    for idx in range(score_set_size):
                        hit.score_set[idx] = hit.score_set.get(idx, 0.0)
                if merge_type == "min":
                    self.hitlist[kw][i].score = min(hit.score_set.values())
                elif merge_type == "max" or merge_type == "fast":
                    self.hitlist[kw][i].score = max(hit.score_set.values())
                elif merge_type == "mean":
                    self.hitlist[kw][i].score = float( sum(hit.score_set.values()) / 
                        len(hit.score_set) )
                elif args.merge == "gmean":
                    self.hitlist[kw][i].score = float(math.exp( 
                        sum( [math.log(x) / len(hit.score_set) for x in hit.score_set.values()])))
                elif args.merge == "rank":
                    self.hitlist[kw][i].score = hit.score_set[min(hit.score_set.keys())]
                if self.hitlist[kw][i].score >= threshold:
                    self.hitlist[kw][i].decision = "YES"
                else:
                    self.hitlist[kw][i].decision = "NO"


    # Search the current list of hits. If an overlapping hit exists, add the 
    # likelihood. If it does not exist, just append to the end.
    def AppendSum(self, kwid, kwhit):
        found = False
        for x in self.hitlist.get(kwid, []):
            if x.Overlap(kwhit) > self.max_overlap:
                found = True
                if kwhit.score > x.score:
                    x.tbeg = kwhit.tbeg
                    x.dur = kwhit.dur
                x.score = x.score + kwhit.score
                break
        if not found:
            self.hitlist[kwid].append(kwhit)

    # Search the hitlist, return True if an overlapping hit exists.
    def OverlapExist(self, kwhit, kwid):
        for x in self.hitlist.get(kwid, []):
            if x.Overlap(kwhit) > self.max_overlap:
                return True
        return False


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
