#!/usr/bin/python

# Takes an RTTM file and a keyword definition file. Produces a hitlist
# containing all keywords found in the RTTM file. Should provide an ATWV
# and MTWV of 1.0.

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
            description='Generate the ideal hitlist from ')
    parser.add_argument("kwdefinition", help="Keyword definition file.")
    parser.add_argument("rttm", help="RTTM file.")
    parser.add_argument("--lowercase", "-l", action='store_true', 
            help='Convert all text to lowercase.')
    parser.add_argument("--codec", "-c", default='utf-8', help='Codec used for ' +
            'the output.')
    parser.add_argument("--max-silence", "-m", default=0.5, 
            help='Maximum amount of silence allowed between any two words.')
    parser.add_argument("--output", "-o", default='-', help='Name of the' +
            ' file to write the merged hitlist.')
  
    args = parser.parse_args()

    hitlist = Hitlist()
    kwtext = hitlist.LoadKeywordDefinition(args.kwdefinition)
    kwid = {}
    for id, kw in kwtext.iteritems():
        if args.lowercase:
            kw = kw.lower()
        kwid[kw] = id

    # Load the RTTM and search for matching keywords.
    last_file = ""
    last_channel = ""
    history_word = []
    history_start = []
    tend = 0.0
    with codecs.open(args.rttm, mode='r', encoding=args.codec) as fin:
        for line in fin:
            data = line.split()
            if data[0] == "LEXEME":
                fileid = data[1]
                channel = data[2]
                tstart = float(data[3])
                dur = float(data[4])
                word = data[5]

                if data[6] == "fp" or data[6] == "frag":
                    tend = tstart + dur
                    continue
                if args.lowercase:
                    word = word.lower()
                if channel != last_channel or last_file != fileid or (tstart - tend) > args.max_silence or data[6] != "lex":
                    history_word = [] # Clear history because the speech is not connected.
                    history_start = []
                last_file = fileid
                last_channel = channel
                tend = tstart + dur
                history_word.append(word)
                history_start.append(tstart)
                # Search over all words in the history and see if we have a match
                for i in range(len(history_word)):
                    if " ".join(history_word[i:]) in kwid:
                        hitlist.Append(kwid[" ".join(history_word[i:])], 
                            KWHit(1.0, history_start[i], tend-history_start[i], channel, fileid, "YES"))
   
    # Write merged hitlist.
    if args.output == "-":
        fout = codecs.getwriter(args.codec)(sys.stdout)
    else:
        fout = codecs.open(args.output, mode='w', encoding=args.codec)
    hitlist.WriteXML(fout)
    fout.close()



if __name__ == "__main__":
    main()
