#!/usr/bin/python

# Takes a set of hitlists and merges them depending on the options.
# Should eventually update to use hitlist and kwhit classes.

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
            description='Merge a set of hit list files into a single hit list.')
    parser.add_argument("kwlist", nargs='+', help="List of keyword hit lists")
    parser.add_argument("--prune", "-b", default=0.0, type=float, 
            help='Only hits >= prune are printed.')
    parser.add_argument("--codec", "-c", default='utf-8', help='Codec used for ' +
            'the output.')
    parser.add_argument("--merge", "-m", default="max", 
            choices=["min", "max", "mean", "rank", "majority", "gmean"], 
            help='Sets the method for merging hits from multiple hit lists.\n' +
                 'Note that the unscored option is important because it sets ' +
                 'whether a missing item in a hit list is just treated as ' +
                 'missing, or as a score of 0.\n' +
                 'min - minimum score in all hitlists.\n' + 
                 'max - maximum score in all hitlists.\n' + 
                 'mean - average score in all hitlists.\n' +
                 'gmean - geometric mean of score in all hitlists.\n' +
                 'rank - takes the score from the first hitlist that has a ' + 
                 'score for that hit.\n')
    parser.add_argument("--output", "-o", default='-', help='Name of the' +
            ' file to write the merged hitlist.')
    parser.add_argument("--threshold", "-t", default=0.5, type=float, 
            help="Minimum score for a hit to be considered a keyword.")
    parser.add_argument("--unscored", "-u", action='store_true', 
            help="Treat all hits not in the hitlist as having a score of 0.")
  
    args = parser.parse_args()

    hitlist = Hitlist()
    for idx, kwfile in enumerate(args.kwlist):
        new_hitlist = Hitlist()
        new_hitlist.LoadXML(kwfile)
        new_hitlist.InitializeScoreSet(idx)
        hitlist.MergeHitlist(new_hitlist)

    hitlist.UpdateScore(args.merge, len(args.kwlist), args.threshold, args.unscored)
   
    # Write merged hitlist.
    if args.output == "-":
        fout = codecs.getwriter(args.codec)(sys.stdout)
    else:
        fout = codecs.open(args.output, mode='w', encoding=args.codec)
    hitlist.WriteXML(fout)
    fout.close()

if __name__ == "__main__":
    main()
