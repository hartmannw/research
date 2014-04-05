#!/usr/bin/python

# Takes a set of keywords. Depending on the options, creates a new keyword
# definition file containing a specific subset of the features.

import sys
import string
import argparse
import codecs
from hartmann.kws import Hitlist
from hartmann.kws import KWHit

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Return a subset of the keyword definition file.')
    parser.add_argument("kwdefinition", help="Keyword definition file.")
    parser.add_argument("transcript", help="Training transcript.")
    parser.add_argument("--codec", "-c", default='utf-8', help='Codec used for ' +
            'the input and output.')
    parser.add_argument("--lowercase", "-l", action='store_true', 
            help='Convert all text to lowercase.')
    parser.add_argument("--iv", action='store_true', 
            help='In-vocabulary feature is written.')
    parser.add_argument("--oov", action='store_true', 
            help='Out-of-vocabulary feature is written.')
    parser.add_argument("--exact", action='store_true', 
            help='Feature that is 1 only if the exact sequence of keywords is in the transcript.')
    parser.add_argument("--percentage-oov", type=float, 
            help='Keeps keywords >= the given value.')
    parser.add_argument("--percentage-iv", type=float, 
            help='Keeps keywords >= the given value.')
    parser.add_argument("--words", type=int, 
            help='Keep only keywords with a specific number of words.')
    parser.add_argument("--characters", type=int, 
            help='Keep only keywords with a specific number of characters.')
    parser.add_argument("--output", "-o", default="-", help='Name of the' +
            ' file to write the keyword features.')
    args = parser.parse_args()

    words = {} # Set of in-vocabulary words.
    transcript = []
    # Load the transcipt
    with codecs.open(args.transcript, mode='r', encoding=args.codec) as fin:
        for line in fin:
            if args.lowercase:
                line = line.lower()
            transcript.append(line)
            data = line.split()
            for word in data:
                words[word] = True

    header = GetKeywordDefinitionHeader(args)

    if args.output == "-":
        fout = codecs.getwriter(args.codec)(sys.stdout)
    else:
        fout = codecs.open(args.output, mode='w', encoding=args.codec)
    fout.write(header + "\n")

    hitlist = Hitlist()
    kwdef = hitlist.LoadKeywordDefinition(args.kwdefinition)
    for id, keyword in sorted(kwdef.items()):
        keep = True
        original_kw = keyword
        if args.lowercase:
            keyword = keyword.lower()
        # Make our tests to remove keywords
        if args.iv:
            if FeatureIV(keyword, words) == 0:
                keep = False
        if args.oov:
            if FeatureOOV(keyword, words) == 0:
                keep = False
        if args.exact:
            if FeatureExact(keyword, words, transcript) == 0:
                keep = False
        if args.percentage_oov:
            if FeaturePercentageOOV(keyword, words) < args.percentage_oov:
                keep = False
        if args.percentage_iv:
            if FeaturePercentageIV(keyword, words) < args.percentage_iv:
                keep = False        
        if args.words:
            if FeatureWords(keyword) != args.words:
                keep = False
        if args.characters:
            if FeatureCharacters(keyword) != args.characters:
                keep = False
        if keep:
            fout.write('<kw kwid="' + id + '">\n')
            fout.write('<kwtext>' + original_kw + '</kwtext>\n')
            fout.write('</kw>\n')

    fout.write('</kwlist>\n')
    fout.close()


def GetKeywordDefinitionHeader(args):
    with codecs.open(args.kwdefinition, mode='r', encoding=args.codec) as fin:
            return fin.readline().strip()
    return ""


def FeatureIV(keyword, words):
    data = keyword.split()
    for w in data:
        if w not in words:
            return 0
    return 1    

def FeatureOOV(keyword, words):
    return 1 - FeatureIV(keyword, words)

def FeatureExact(keyword, words, transcript):
    if FeatureOOV(keyword, words) > 0:
        return 0
    for line in transcript:
        if line.find(keyword) > 0:
            return 1
    return 0

def FeaturePercentageOOV(keyword, words):
    data = keyword.split()
    total = float(len(data))
    return sum([FeatureOOV(w, words) for w in data]) / total

def FeaturePercentageIV(keyword, words):
    data = keyword.split()
    total = float(len(data))
    return sum([FeatureIV(w, words) for w in data]) / total

def FeatureWords(keyword):
    return len(keyword.split())

def FeatureCharacters(keyword):
    return sum([len(list(w)) for w in keyword.split()])

if __name__ == "__main__":
    main()
