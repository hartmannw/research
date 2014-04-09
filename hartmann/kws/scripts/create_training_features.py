#!/usr/bin/python

# Takes a set of hitlists and turns them into features for training.
# If a keyword feature file is also included, that is appended to the
# training features. If the gold hitlist is also included, the final
# feature is the target (either -1 or 1, or from the target file).

import sys
import string
import re
import codecs
import argparse
import math
from hartmann.kws import Hitlist
from hartmann.kws import KWHit

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Turn hitlists into training features.')
    parser.add_argument("kwlist", nargs='+', help="List of keyword hit lists")
    parser.add_argument("--codec", "-c", default='utf-8', help='Codec used for ' +
            'the output.')
    parser.add_argument("--output", "-o", default='-', help='Name of the' +
            ' file to write the merged hitlist.')
    parser.add_argument("--inverse", "-i", action='store_true', 
            help="Add the inverse of each score.")
    parser.add_argument("--duration", "-d", action='store_true', 
            help="Add the duration as a feature.")
    parser.add_argument("--bias", "-b", action='store_true', 
            help="Adds the count of non-zero probabilities as a bias.")
    parser.add_argument("--kwfeatures", "-k", help="File containing keyword features.")
    parser.add_argument("--target", "-t", help="File containing keyword specific target information.")
    parser.add_argument("--gold", "-g", help="Gold standard hitlist.")
    parser.add_argument("--filter-zero-target", "-f", action='store_true', 
            help="Remove entries with a target of 0.")
  
    args = parser.parse_args()

    kwfeatures = {}
    if args.kwfeatures:
        with codecs.open(args.kwfeatures, mode='r', encoding=args.codec) as fin:
            for line in fin:
                data = line.split()
                kwfeatures[data[0]] = " ".join(data[1:])
    target = {}
    if args.target:
        with codecs.open(args.target, mode='r', encoding=args.codec) as fin:
            for line in fin:
                data = line.split()
                target[data[0]] = data[1:]
    gold = Hitlist()
    if args.gold: 
        gold.LoadXML(args.gold)

    hitlist = Hitlist()
    for idx, kwfile in enumerate(args.kwlist):
        new_hitlist = Hitlist()
        new_hitlist.LoadXML(kwfile)
        new_hitlist.InitializeScoreSet(idx)
        hitlist.MergeHitlist(new_hitlist)
   
    # Write out the features.
    if args.output == "-":
        fout = codecs.getwriter(args.codec)(sys.stdout)
    else:
        fout = codecs.open(args.output, mode='w', encoding=args.codec)
    
    for k in sorted(hitlist.keywords):
        for hit in hitlist.hitlist[k]:
            item = []
            feature_target = "0"
            item.append(hit.filename)
            item.append(hit.channel)
            item.append(str(hit.tbeg))
            item.append(str(hit.dur))
            item.append(k)
            # Now add the actual features
            if args.kwfeatures:
                item.append(kwfeatures[k])
            count = 0
            for score_idx in range(len(args.kwlist)):
                item.append(str(hit.score_set.get(score_idx, 0.0)))
                if score_idx in hit.score_set:
                    count = count + 1
                if args.inverse:
                    if score_idx in hit.score_set:
                        item.append(str(1 - hit.score_set[score_idx]))
                    else:
                        item.append("0.0")
            if args.duration:
                item.append(str(hit.dur))
            if args.bias:
                item.append(str(count))
            if args.gold:
                feature_target = FindTarget(hit, k, gold, target)
            if feature_target != "0" or not args.filter_zero_target:
                item.append(feature_target)
                fout.write(" ".join(item) + "\n")
        
    fout.close()

def FindTarget(hit, keyword, gold, target):
    if keyword not in gold.hitlist: # We must not be interested in this keyword.
        return "0"
    if gold.OverlapExist(hit, keyword):
        return target.get(keyword, ["1", "-1"])[0]
    else:
        return target.get(keyword, ["1", "-1"])[1]

if __name__ == "__main__":
    main()
