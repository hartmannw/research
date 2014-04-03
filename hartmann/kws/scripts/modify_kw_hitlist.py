#!/usr/bin/python

# Takes a single hitlist a changes various properties.

import sys
import string
import argparse
from hartmann.kws import Hitlist
from hartmann.kws import KWHit

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Modify a single hitlist.')
    parser.add_argument("kwfile", help="Keyword hit list")
    parser.add_argument("--remove-no", "-r", action='store_true', 
            help='Only hits >= threshold are printed.')
    parser.add_argument("--keywords", "-k", help='List of keywords ' +
            'to consider. Useful to write only certain keywords. Default is all' +
            ' keywords.')
    parser.add_argument("--output", "-o", default=sys.stdout, help='Name of the' +
            ' file to write the hitlist.')
    parser.add_argument("--threshold", "-t", default=0.5, type=float, 
            help="Minimum score for a hit to be considered a keyword.")
    parser.add_argument("--scale", default=1.0, type=float, 
            help="Multiply each score by scale.")
    parser.add_argument("--offset", default=0.0, type=float, 
            help="Add the offset to each score.")
    parser.add_argument("--minimum_score", type=float, 
            help="Minimum score required to keep a hit.")
    parser.add_argument("--maximum_hits", default=-1, type=int, 
            help="Maximum number of hits per keyword. Negative value means no" +
            " restriction on number of hits.")
    args = parser.parse_args()

    hitlist = Hitlist()
    hitlist.LoadXML(args.kwfile)
    if args.threshold:
        hitlist.MakeDecision(args.threshold)

    hitlist.LinearScale(args.scale, args.offset)
    if args.maximum_hits > 0:
        hitlist.PruneByCount(args.maximum_hits)
    if args.minimum_score:
        hitlist.PruneByScore(args.minimum_score)
    if args.remove_no:
        hitlist.PruneByDecision()
    hitlist.WriteXML(args.output)

    
if __name__ == "__main__":
    main()
