#!/usr/bin/python

# Perform spectral clustering

import sys, string, re, codecs, argparse
from sklearn.cluster import SpectralClustering
from sklearn import metrics
import numpy as np

def main():

    # Parse command line arguments
    parser = argparse.ArgumentParser(usage=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description='Perform spectral clustering.')
    parser.add_argument("--clusters", "-c", type=int, help='Number of clusters.')
    parser.add_argument("--knn", "-k", type=int, default=0, 
            help='Number of nearest neighbors, 0 means all.')
    parser.add_argument("--sm", "-s", 
            help='File containing similarity matrix')
    parser.add_argument("--iterations", "-i", type=int, default=10,
            help='Number of KMeans iterations.')
    parser.add_argument("--true_labels", "-t", 
            help='File containing the true labels.')
    parser.add_argument("--output", "-o", help='Name of the file to write' +
            ' the labels to.')
    parser.add_argument("--normalize", "-n", action='store_true', 
            help='Normalize each row so that the max value is one.')
    args = parser.parse_args()


    sm = np.load(args.sm)
    if args.normalize:
        sm /= sm.max(axis=1)[:, np.newaxis]
        # Ensure symmetric
        sm = (sm + sm.T) / 2
    labels = []
    if args.knn > 0:
        labels = SpectralClustering(n_clusters=args.clusters, 
                affinity='nearest_neighbors', n_neighbors=args.knn,
                n_init=args.iterations).fit(sm).labels_
    else:
        labels = SpectralClustering(n_clusters=args.clusters, 
                affinity='precomputed',
                n_init=args.iterations).fit(sm).labels_
    
    with open(args.output, 'w') as fout:
        for l in labels:
            fout.write(str(l) + '\n')

    # Load the true labels.
    if args.true_labels:
        true_labels = []
        with open(args.true_labels, 'r') as fin:
            for line in fin:
                true_labels.append(int(line.strip()))
        # Run the metrics.
        print("Homogeneity: %0.3f" % metrics.homogeneity_score(true_labels, labels))
        print("Completeness: %0.3f" % metrics.completeness_score(true_labels, labels))
        print("V-measure: %0.3f" % metrics.v_measure_score(true_labels, labels))
        print("Adjusted Rand Index: %0.3f"
                      % metrics.adjusted_rand_score(true_labels, labels))
        print("Adjusted Mutual Information: %0.3f"
                      % metrics.adjusted_mutual_info_score(true_labels, labels))
        print("Silhouette Coefficient: %0.3f"
                      % metrics.silhouette_score(sm, labels))

if __name__ == "__main__":
    main()
