""" A set of experiments which generate a matrix indiciating which
users are active in which subreddits, and clustering or embedding the membership matrix
"""

import numpy as np
import pickle
import sys
import time
from util import *
from scrape_members import get_authors
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA, KernelPCA
from sklearn.cluster import SpectralClustering, k_means, KMeans
from scipy.spatial.distance import cdist
import networkx as nx

subreddits = load_set_from_list_of_files(['subreddits/big_list_of_subreddits.txt'])


def intersection_over_union(a, b):
    return len(a & b) / len(a | b)


# Generated a matrix where each row is a subreddit and each column is a users.
# ones are placed when a user has posted in a subreddit recently
def generate_matrix(subreddits):
    m_list = {}
    authors = set()

    for s in subreddits:
        print('Pulling authors for {}'.format(s))
        a = get_authors(s, endpoint='submission', max_num_authors=2000)
        authors.update(a)
        m_list[s] = a

    authors = sorted(authors)
    n_subreddits = len(subreddits)
    n_authors = len(authors)
    M = np.zeros([n_subreddits, n_authors], dtype=int)

    for i, s in enumerate(subreddits):
        for j, a in enumerate(authors):
            M[i,j] = a in m_list[s]

    data = (subreddits, authors, M)
    return data

def save(output_filename, data):
    with open(output_filename, 'wb') as f:
        pickle.dump(data, f)

def load(input_filename):
    with open(input_filename, 'rb') as f:
        return pickle.load(f)

# project the membership matrix down into fewer dimensions
# and plot points for each of the subreddits
# subreddits can colored using the y label vector
def pca_matrix(data, y=None):
    subreddits, authors, M = data

    pca = KernelPCA(n_components=2)
    pca.fit(M)
    projected = pca.transform(M)

    fig, ax = plt.subplots()
    ax.scatter(*projected.T, c=y)
    for i, s in enumerate(subreddits):
        ax.annotate(s, projected[i])

    plt.show()

# sort all the subreddits by how similar they are to the
# given subreddit. return the sorted matrix and subreddits list
def sort_by_similarity(data, subreddit):
    subreddits, authors, M = data

    # sort by similarity
    d = cdist(M, M)
    i = list(subreddits).index(subreddit)
    dists = np.abs(M[None, i] - M).sum(axis=1)
    indices = np.argsort(dists)
    print()
    for idx in indices[:15]:
        print("{0:.4f}\t{1:s}".format(dists[idx]/M.shape[1], subreddits[idx]))
    print()

    subreddits = np.array(subreddits)[indices]
    M = M[indices]

    return subreddits, authors, M

# create and plot an adjacency where the distance between two subreddits is
# the euclidean distance between their membership vectors
def visualize_matrix(data):
    subreddits, authors, M = data

    d = cdist(M, M)
    d+= np.eye(d.shape[0]) * np.mean(d)

    plt.matshow(d)
    ax = plt.gca()
    ax.set_xticklabels([''] + list(subreddits))
    ax.set_yticklabels([''] + list(subreddits))
    plt.show()

# find the cliques in the graph contining a certain subreddit
# since cliques rely on unweighted graphs, we remove edges which are below
# the mean weight
def cliques(data, subreddit):
    subreddits, authors, M = data
    d = cdist(M, M)
    adj = d  < np.mean(d)
    G = nx.convert_matrix.from_numpy_matrix(adj)
    cliques = nx.cliques_containing_node(G, list(subreddits).index(subreddit))
    for c in cliques:
        print(np.array(subreddits)[c])

# project the graph down into two dimensions where nodes with greater
# edge weights are drawn closer together
def draw_flat_graph(data):
    subreddits, authors, M = data
    d = cdist(M, M)
    G = nx.from_numpy_matrix(np.max(d) - d)
    pos=nx.spring_layout(G)
    labels = {}
    for i,s in enumerate(subreddits):
        labels[i] = s
    nx.draw_networkx_nodes(G,pos)
    nx.draw_networkx_edges(G, pos, G.edges)
    nx.draw_networkx_labels(G,pos,labels)
    plt.show()

# use kmeans to cluster the subreddits based on their membership vectors
def cluster_matrix(data, n=2):
    subreddits, authors, M = data

    cluster = KMeans(n_clusters=n)
    y = cluster.fit_predict(M)

    return y

# remove subreddits from the matrix which have too few contributers
def remove_too_small(data, n):
    subreddits, authors, M = data
    keep = M.sum(axis=1) > n

    return np.array(subreddits)[keep], authors, M[keep]



if __name__ == '__main__':
    data = generate_matrix(subreddit)
    save('data/big_matrix.pkl', data)

    data = load('data/big_matrix.pkl')
    data = remove_too_small(data, 900)
    data = sort_by_similarity(data, sys.argv[1])

    y = cluster_matrix(data, 5)
    pca_matrix(data, y)

    # using intersection over union to examine subreddit similarity
    # a = set(get_authors('climateskeptics'))
    # b = set(get_authors('environmental_science'))
    # c = set(get_authors('conservative'))

    # print('r/climateskeptics with r/environmental_science', intersection_over_union(a, b))
    # print('r/climateskeptics with r/conservative', intersection_over_union(a, c))
