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


    c = subreddits.index('climateskeptics')
    dists = ((M - M[None, c])**2).sum(axis=1)
    idx = np.argsort(dists)
    print(np.array(subreddits)[idx])


    data = (subreddits, authors, M)
    return data

def save(output_filename, data):
    with open(output_filename, 'wb') as f:
        pickle.dump(data, f)

def load(input_filename):
    with open(input_filename, 'rb') as f:
        return pickle.load(f)

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

def visualize_matrix(data):
    # data = sort_by_similarity(data, 'climateskptics')
    subreddits, authors, M = data

    d = cdist(M, M)
    d+= np.eye(d.shape[0]) * np.mean(d)

    plt.matshow(d)
    ax = plt.gca()
    ax.set_xticklabels([''] + list(subreddits))
    ax.set_yticklabels([''] + list(subreddits))
    plt.show()


def cliques(data, subreddit):
    subreddits, authors, M = data
    d = cdist(M, M)
    adj = d  < np.mean(d)
    G = nx.convert_matrix.from_numpy_matrix(adj)
    cliques = nx.cliques_containing_node(G, list(subreddits).index(subreddit))
    for c in cliques:
        print(np.array(subreddits)[c])


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

def cluster_matrix(data, n=2):
    subreddits, authors, M = data

    cluster = KMeans(n_clusters=n)
    y = cluster.fit_predict(M)

    return y


def remove_too_small(data, n):
    subreddits, authors, M = data
    keep = M.sum(axis=1) > n

    return np.array(subreddits)[keep], authors, M[keep]

def get_similar_reddits(subreddit, data):
    subreddits, authors, M = data
    if subreddit not in subreddits:
        print('Couldnt find subreddit {}'.format(subreddit))
        return None


    d = cdist(M, M)
    i = list(subreddits).index(subreddit)
    distances = d[i]
    print
    indices = np.argsort(distances)
    return np.array(subreddits)[indices]




if __name__ == '__main__':
    data = load('generated_data/big_matrix.pkl')
    data = remove_too_small(data, 900)

    data = sort_by_similarity( data, sys.argv[1])
    y = cluster_matrix(data, 5)
    pca_matrix(data, y)
