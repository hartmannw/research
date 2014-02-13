#!/usr/bin/python

# Computes the similarity matrix for a HMM stored in the Kaldi format.

import sys, string, re, codecs, argparse
import hartmann.kaldi
import numpy as np

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Create HMM similarity matrix')
    parser.add_argument("--model", "-m", help='Kaldi model file stored in text.')
    parser.add_argument("--ctx", "-c", help='Kaldi context file stored in text.')
    parser.add_argument("--first_phone", "-f", type=int, default=0, 
            help='Index of first non-silence phone.')
    parser.add_argument("--sm", "-s", help='Name of the file to write the ' +
            'similarity matrix to.')
    parser.add_argument("--tiedlist", "-t", help='Name of the file to write' +
            ' the tiedlist to.')
    args = parser.parse_args()

   
    print "Reading Kaldi Model from files " + args.model + " and " + args.ctx
    model = hartmann.kaldi.model.load_gmm_hmm(args.ctx, args.model)
    print model.information()
    model.reduce_transitions()
    model.verify()
    print model.information()
    tiedlist = model.create_hmm_tiedlist()
    print len(tiedlist)
    model.remove_hmms(range(0,args.first_phone))
    print model.information()
    model.verify()
    tiedlist = model.create_hmm_tiedlist()
    print len(tiedlist)
    #model.convert_to_monophone()
    tiedlist = model.create_hmm_tiedlist()
    print model.information()
    model.verify()
    
    # Write the tiedlist. Each model on the line is equivalent.
    with open(args.tiedlist, 'w') as fout:
        for t in tiedlist:
            output = []
            for idx in t:
                output.append(model.hmm[idx].context_id())
            fout.write("|".join(output) + "\n")

    sm = model.compute_hmm_similarity(tiedlist)
    np.save(args.sm, sm)

if __name__ == "__main__":
    main()
