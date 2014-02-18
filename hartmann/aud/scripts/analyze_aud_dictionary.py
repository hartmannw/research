#!/usr/bin/python

# Analyze the new dictionary.

import sys, string, re, codecs, argparse
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from collections import defaultdict

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Analyze dictionary.')
    parser.add_argument("--original", "-o", help='Original dictionary.')
    parser.add_argument("--new", "-n", help='New dictionary.')
    parser.add_argument("--plot", default="plot.png", help="output image file")
    args = parser.parse_args()

    # Load the original dictionary
    lexicon = {}
    with codecs.open(args.original, mode='r', encoding='utf-8') as fin:
        for line in fin:
            data = line.strip().split()
            lexicon[data[0]] = data[1:]
    
    ophones = {}
    nphones = {}
    confusion = defaultdict(Counter)
    with codecs.open(args.new, mode='r', encoding='utf-8') as fin:
        for line in fin:
            data = line.strip().split()
            pron = data[1:]
            if len(lexicon.get(data[0], [])) == len(pron):
                for o, n in zip(lexicon[data[0]], pron):
                    ophones[o] = True
                    nphones[n] = True
                    confusion[o][n]+=1

    ophones=list(ophones.keys())
    nphones=list(nphones.keys())
    plot = np.zeros( (len(ophones), len(nphones)) , float)
    for r,o in enumerate(ophones):
        for c, n in enumerate(nphones):
            plot[r,c] = confusion[o][n]


    row_sums = plot.sum(axis=0)
    #plot = plot / row_sums[np.newaxis, :]

    max_indices = np.argmax(plot, axis=0)
    sort_indices = np.argsort(max_indices)
    plot = plot[:, sort_indices]
    
    imageplot = plt.imshow(plot, interpolation='nearest')
    plt.yticks(range(len(ophones)), ophones, fontsize=6)
    #plt.xticks([])
    plt.colorbar()
    plt.savefig(args.plot, dpi=96, bbox_inches=0)

if __name__ == "__main__":
    main()
