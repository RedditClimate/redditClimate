import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import SpectralClustering, k_means
from matplotlib import pyplot as plt
import pickle
from util import *



def get_labels(users):
    skeptic_authors =\
        load_set_from_list_of_files(['comment_authors_climateskeptics.txt'])
    green_authors =\
        load_set_from_list_of_files(['comment_authors_green.txt'])

    skeptic_mask = np.array([u in skeptic_authors for u in users]).astype(int)
    green_mask = np.array([u in green_authors for u in users]).astype(int)

    return skeptic_mask - green_mask

    

if __name__ == '__main__':

    input_file = 'climateskeptics_and_green_membership.pkl'

    with open(input_file, 'rb') as f:
        users, subreddits, is_in = pickle.load(f)
        X = is_in
        y = get_labels(users)

        is_green = np.array(subreddits) == 'Green'
        is_skeptic = np.array(subreddits) == 'climateskeptics'

        mask = (1 - is_skeptic)
        print(np.array(subreddits))
        print(mask)
        # X = X[:, mask.astype(bool)]
        print(X.shape)

        # cluster = SpectralClustering(n_clusters=2)
        # y = cluster.fit_predict(X)

        pca = PCA(n_components=2)
        pca.fit(X)
        projected = pca.transform(X)
        # plt.hist(projected)
        plt.scatter(*projected.T, c=y)
        plt.show()

        y = y.astype(bool)
        print(np.array(users)[y])