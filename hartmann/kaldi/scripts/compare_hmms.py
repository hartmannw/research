#!/usr/bin/python

# Compares two specific HMMs within the same HMM set.

import sys, string, re, codecs, argparse
import hartmann.kaldi
import numpy as np

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Compares two HMMs.')
    parser.add_argument("--model", "-m", help='Kaldi model file stored in text.')
    parser.add_argument("--ctx", "-c", help='Kaldi context file stored in text.')
    parser.add_argument("--first", "-f", help='ID of first HMM.')
    parser.add_argument("--second", "-s", help='ID of second HMM.')
    args = parser.parse_args()

   
    print "Reading Kaldi Model from files " + args.model + " and " + args.ctx
    model = hartmann.kaldi.model.load_gmm_hmm(args.ctx, args.model)
    print model.information()

    print "Model Statistics after Tying"
    model.reduce_transitions()
    model.verify()
    print model.information()
    tiedlist = model.create_hmm_tiedlist()
    model.verify()

    # Find the true model ids.
    fid = model.cd_index[ args.first ]
    sid = model.cd_index[ args.second ]

    for hmmset in tiedlist:
        if fid in hmmset:
            firstset = hmmset
        if sid in hmmset:
            secondset = hmmset


    print "Comparing " + args.first + " and " + args.second

    print args.first + " is a member of the tiedset: " + "--".join([ model.hmm[i].context_id() for i in firstset])
    print "With GMM ids: (" + ", ".join([str(x) for x in model.hmm[fid].modelid]) + ") and transition ids (" + ", ".join([str(x) for x in model.hmm[fid].transitionid]) + ")"
    print "The actual transition (exit) probabilities are: (" + ", ".join([ str(model.transition[x]) for x in model.hmm[fid].transitionid ]) + ")"
    
    print "-----------------------------"
    print args.second + " is a member of the tiedset: " + "--".join([ model.hmm[i].context_id() for i in secondset])
    print "With GMM ids: (" + ", ".join([str(x) for x in model.hmm[sid].modelid]) + ") and transition ids (" + ", ".join([str(x) for x in model.hmm[sid].transitionid]) + ")"
    print "The actual transition (exit) probabilities are: (" + ", ".join([ str(model.transition[x]) for x in model.hmm[sid].transitionid ]) + ")"

    print "\nThe Cauchy Schwartz Divergence matrix for the two sets of GMMs:"

    for a in model.hmm[fid].modelid:
        row = []
        for b in model.hmm[sid].modelid:
            row.append(str( model.model[a].csd(model.model[b]) ))
        print " ".join(row)

    # Modify the model such that only the necessary HMMs exist.
    hmmlist = []
    hmmlist.append(fid)
    hmmlist.append(sid)
    model.make_subset(hmmlist)
    print model.information()
    model.verify()
    tiedlist = model.create_hmm_tiedlist()
    

    for t in tiedlist:
        output = []
        for idx in t:
            output.append(model.hmm[idx].context_id())
        print "|".join(output)

    sm = model.compute_hmm_similarity(tiedlist)
    print sm

        
if __name__ == "__main__":
    main()
