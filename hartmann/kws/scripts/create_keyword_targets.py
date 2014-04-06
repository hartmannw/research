#!/usr/bin/python

# Given a hitlist, it creates the training targets for each keyword. This
# assumes every entry in the hitlist is a correct hit. The resulting output
# contains three columns: 1) keyword id, 2) benefit of a true detection, and
# 3) cost of a false alarm.
# If there exists no entries for a particular keyword, then the values will be
# 0 for both targets.

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
    parser.add_argument("kwfile", help="Keyword hitlist.")
    parser.add_argument("--codec", "-c", default='utf-8', help='Codec used for ' +
            'the input and output.')
    parser.add_argument("--beta", default=999.9, type=float,
            help='The beta term used in the TWV calculation.')
    parser.add_argument("--seconds", "-s", default=36000.0, type=float, 
            help='Number of seconds in the audio file. Typically defined in the ecf file.')
    parser.add_argument("--output", "-o", default="-", help='Name of the' +
            ' file to write the keyword features.')
    args = parser.parse_args()

    if args.output == "-":
        fout = codecs.getwriter(args.codec)(sys.stdout)
    else:
        fout = codecs.open(args.output, mode='w', encoding=args.codec)

    hitlist = Hitlist()

    hitlist.LoadXML(args.kwfile)
    for kwid in hitlist.keywords:
        total = len(hitlist.hitlist[kwid])
        if total == 0:
            fout.write(kwid + " 0 0\n")
        else:
            positive = 1.0 / total
            negative = -args.beta / (args.seconds - total)
            fout.write(kwid + " " + str(positive) + " " + str(negative) + "\n")
    fout.close()

if __name__ == "__main__":
    main()
