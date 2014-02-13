#!/usr/bin/python

# List the nearest neightbors for each row in a similarity matrix.

import sys, string, re, codecs, argparse
import numpy as np

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='List the nearest neighbors for each row.')
    parser.add_argument("--tiedlist", "-t", 
            help='File containing the hmm tiedlist.')
    parser.add_argument("--phonelist", "-p", 
            help='List of original phone ids.')
    parser.add_argument("--sm", "-s", help='Similarity matrix.')
    parser.add_argument("--neighbors", "-n", default=1, type=int,
            help='Number of neighbors.')
    args = parser.parse_args()


    # Load the phones.
    phonemap = {}
    with open(args.phonelist, 'r') as fin:
        for line in fin:
            data = line.strip().split()
            phonemap[ int(data[1]) ] = data[0]

    # Load the tiedlist
    tiedlist = []
    with open(args.tiedlist, 'r') as fin:
        for line in fin:
            data = line.strip().split('|')
            hmmset = []
            for hmm in data:
                ctx = [phonemap[int(x)] for x in hmm.split()]
                hmmset.append(ctx[0] + "-" + ctx[1] + "+" + ctx[2])
            tiedlist.append(hmmset)

    sm = np.load(args.sm)
    neighbors = np.argsort(sm, axis=1)
    for r, row in enumerate(neighbors):
        output = []
        rev_row = row[::-1]
        for c in range(0, args.neighbors):
            output.append("(" + " ".join(tiedlist[rev_row[c]]) + "):" + str(sm[r,rev_row[c]]))
        print " ".join(output)


if __name__ == "__main__":
    main()
