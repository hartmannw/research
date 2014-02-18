#!/usr/bin/python

# Convert a dictionary to new units using discovered units.

import sys, string, re, codecs, argparse
import numpy as np
from collections import Counter
from collections import defaultdict

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Convert dictionary.')
    parser.add_argument("--labels", "-l", help='File containing new labels.')
    parser.add_argument("--tiedlist", "-t", 
            help='File containing the hmm tiedlist.')
    parser.add_argument("--phonelist", "-p", 
            help='List of original phone ids.')
    parser.add_argument("--monophone", "-m", 
            help='File to write the monophone translations.')
    parser.add_argument("--dictionary", "-d", 
            help='Original dictionary.')
    parser.add_argument("--output", "-o", help='Name of the file to write' +
            ' the dictionary to.')
    args = parser.parse_args()

    args.position_dependent = True

    # Build a set of possible AUD units.
    letters = string.letters
    aud = [x + y for x in letters for y in letters]

    # Load the phones.
    phonemap = {}
    with codecs.open(args.phonelist, mode='r', encoding='utf-8') as fin:
        for line in fin:
            data = line.strip().split()
            phonemap[ int(data[1]) ] = data[0]

    # Load the new labels
    labels = []
    with open(args.labels, 'r') as fin:
        for line in fin:
            labels.append(int(line.strip()))
   
    # Load the tiedlist
    lstat = defaultdict(Counter)
    mono_stat = defaultdict(Counter)
    index = 0
    with open(args.tiedlist, 'r') as fin:
        for line in fin:
            data = line.strip().split('|')
            for hmm in data:
                ctx = [phonemap[int(x)] for x in hmm.split()]
                if not args.position_dependent:
                    ctx = [x.split('_')[0] for x in ctx]
                # Add counts to stats
                mono_stat[ctx[1].split('_')[0]][labels[index]]+=1
                lstat[ ctx[0] + "-" + ctx[1] + "+" + ctx[2] ][labels[index]]+=1
                lstat[ ctx[1] + "+" + ctx[2] ][labels[index]]+=1
                lstat[ ctx[0] + "-" + ctx[1] ][labels[index]]+=1
                lstat[ ctx[1] ][labels[index]]+=1
            index=index + 1

    # Build map to new labels
    lmap = {}
    for ctx, counts in lstat.iteritems():
        lmap[ctx] = aud[counts.most_common(1)[0][0]]

    fout = codecs.open(args.output, mode='w', encoding='utf-8')
    with codecs.open(args.dictionary, mode='r', encoding='utf-8') as fin:
        for line in fin:
            data = line.strip().split()
            word = data[0]
            pron = data[2:]
            if not args.position_dependent:
                pron = [x.split('_')[0] for x in pron]
            fout.write(word + "\t" + 
                    " ".join(translate_pronunciation(pron, lmap)) + "\n")
    fout.close()
   
    with codecs.open(args.monophone, mode='w', encoding='utf-8') as fout:
        for phone, counts in mono_stat.iteritems():
            fout.write(phone + " " + str(counts.most_common(1)[0][0]) + '\n')

def translate_pronunciation(pron, lmap):
    pron.insert(0, 'SIL')
    pron.append('SIL')
    ret = []
    for i in range(1, len(pron)-1):
        if pron[i-1] + "-" + pron[i] + "+" + pron[i+1] in lmap:
            ret.append(lmap[pron[i-1] + "-" + pron[i] + "+" + pron[i+1]])
        elif pron[i-1] + "-" + pron[i] + "+" in lmap:
            ret.append(lmap[pron[i-1] + "-" + pron[i]])
        elif pron[i] + "+" + pron[i+1] in lmap:
            ret.append(lmap[pron[i] + "+" + pron[i+1]])
        elif pron[i] in lmap:
            ret.append(lmap[pron[i]])
        else:
            ret.append(pron[i])
    return ret


if __name__ == "__main__":
    main()
