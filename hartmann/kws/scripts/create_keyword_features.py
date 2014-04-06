#!/usr/bin/python

# Takes a set of keywords. Depending on the options, writes features for each
# keyword.

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
            description='Generate keyword specific features.')
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
    parser.add_argument("--percentage-oov", action='store_true', 
            help='Percentage of words that are OOV in the keyword.')
    parser.add_argument("--percentage-iv", action='store_true', 
            help='Percentage of words that are IV in the keyword.')
    parser.add_argument("--words", action='store_true', 
            help='Number of individual words in the keyword.')
    parser.add_argument("--characters", action='store_true', 
            help='Number of individual non-whitespace characters in the keyword.')
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

    if args.output == "-":
        fout = codecs.getwriter(args.codec)(sys.stdout)
    else:
        fout = codecs.open(args.output, mode='w', encoding=args.codec)

    hitlist = Hitlist()
    kwdef = hitlist.LoadKeywordDefinition(args.kwdefinition)
    for id, keyword in sorted(kwdef.items()):
        features = []
        original_kw = keyword
        if args.lowercase:
            keyword = keyword.lower()
        # Now add all features that are requested.
        if args.iv:
            features.append(FeatureIV(keyword, words))
        if args.oov:
            features.append(FeatureOOV(keyword, words))
        if args.exact:
            features.append(FeatureExact(keyword, words, transcript))
        if args.percentage_iv:
            features.append(FeaturePercentageIV(keyword, words))
        if args.percentage_oov:
            features.append(FeaturePercentageOOV(keyword, words))
        if args.words:
            features.append(FeatureWords(keyword))
        if args.characters:
            features.append(FeatureCharacters(keyword))
        fout.write(id + " " + " ".join([str(f) for f in features]) + "\n")
    fout.close()


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
