#!/usr/bin/python

# Compares two hitlists

import sys
import string
import argparse
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from scipy import stats
from hartmann.kws import Hitlist
from hartmann.kws import KWHit

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Modify a single hitlist.')
    parser.add_argument("kwfile", nargs=2, help="Two keyword hitlists")
    parser.add_argument("--keywords", "-k", help='List of keywords ' +
            'to consider. Useful to write only certain keywords. Default is all' +
            ' keywords.')
    parser.add_argument("--plot", "-p", default='plot.png', 
            help='Output file for the plot.')
    args = parser.parse_args()

    hitlist = []
    hitlist.append(Hitlist())
    hitlist[0].LoadXML(args.kwfile[0])
    hitlist.append(Hitlist())
    hitlist[1].LoadXML(args.kwfile[1])

    x = []
    y = []

    keywords = hitlist[0].keywords
    for k in keywords:
        for hit in hitlist[0].hitlist[k]:
            for match in hitlist[1].hitlist.get(k, []):
                if hit.Overlap(match) > 0 and hit.score > 0.01 and match.score > 0.01:
                    y.append(hit.score)
                    x.append(match.score)

    #print len(x)
    #hist = plt.hist2d(x,y, bins=10, norm=LogNorm())
    #plt.colorbar()

    #plt.savefig(args.plot, dpi=96, bbox_inches=0)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

    print 'r value', r_value
    print  'p_value', p_value
    print 'standard deviation', std_err
    print 'slope', slope
    print 'intercept', intercept

    #line = slope*xi+intercept
    #plot(x,line,'r-',x,y,'o')

    
if __name__ == "__main__":
    main()
