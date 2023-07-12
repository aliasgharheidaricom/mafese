#!/usr/bin/env python
# Created by "Thieu" at 08:38, 25/05/2023 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

"""
Refs:
1. https://docs.scipy.org/doc/scipy/reference/stats.html#correlation-functions
2. https://scikit-learn.org/stable/modules/classes.html#module-sklearn.feature_selection
"""

import numpy as np
from sklearn.feature_selection import chi2, f_classif, mutual_info_classif
from sklearn.feature_selection import r_regression, f_regression, mutual_info_regression
from scipy import stats
# from skrebate import ReliefF, SURF, MultiSURF, SURFstar


def select_bests(importance_scores=None, n_features=3):
    """
    Select features according to the k highest scores or percentile of the highest scores.

    Parameters
    ----------
    importance_scores : array-like of shape (n_features,)
        Scores of features.

    n_features : int, float. default=3
        Number of selected features.

        - If `float`, it should be in range of (0, 1). That represent the percentile of the highest scores.
        - If `int`, it should be in range of (1, N-1). N is total number of features in your dataset.

    Returns
    -------
    mask: Number of top features to select.

    """
    max_features = len(importance_scores)
    if type(n_features) in (int, float):
        if type(n_features) is float:
            if 0 < n_features < 1:
                n_features = int(n_features * max_features) + 1
            else:
                raise ValueError("n_features based on percentile should has value in range (0, 1).")
        if n_features < 1 or n_features > max_features:
            raise ValueError("n_features should has value in range (1, max_feature).")
    else:
        raise ValueError("n_features should be int if based on k highest scores, or float if based on percentile of highest scores.")
    mask = np.zeros(importance_scores.shape, dtype=bool)
    # Request a stable sort. Mergesort takes more memory (~40MB per megafeature on x86-64).
    mask[np.argsort(importance_scores, kind="mergesort")[-n_features:]] = 1
    return mask


def kendall_func(X, y):
    return np.array([stats.kendalltau(X[:, f], y).correlation for f in range(X.shape[1])])


def spearman_func(X, y):
    return np.array([stats.spearmanr(X[:, f], y).correlation for f in range(X.shape[1])])


def point_func(X, y):
    return np.array([stats.pointbiserialr(X[:, f], y).correlation for f in range(X.shape[1])])


def relief_func(X, y, n_neighbors=5, n_bins=10, **kwargs):
    """
    Performs Relief feature selection on the input dataset X and target variable y.
    Returns a vector of feature importance scores.

    Parameters:
    X : numpy array
        Input dataset of shape (n_samples, n_features).
    y : numpy array
        Target variable of shape (n_samples,).
    n_neighbors : int
        Number of neighbors to use for computing feature importance scores.
        Default is 5.
    n_bins : int
        Number of bins to use for discretizing the target variable in regression problems.
        Default is 10.

    Returns:
    numpy array
        Vector of feature importance scores, with shape (n_features,).
    """
    # Initialize feature importance scores to zero
    importance_scores = np.zeros(X.shape[1])

    # Discretize the target variable into n_bins classes
    if len(np.unique(y)) > 2:
        # Regression problem: discretize the target variable into n_bins classes
        y_bins = np.linspace(np.min(y), np.max(y), n_bins)
        y = np.digitize(y, y_bins) - 1

    # Compute distance matrix between instances in the dataset
    dist_matrix = np.sqrt(np.sum((X[:, np.newaxis, :] - X[np.newaxis, :, :]) ** 2, axis=-1))

    # Loop over instances in the dataset
    for i in range(X.shape[0]):
        # Get the target value of the current instance
        target_value = y[i]

        # Find the indices of the n_neighbors nearest instances with different target labels
        indices = np.argsort(dist_matrix[i])
        neighbors = []
        for j in range(len(indices)):
            if len(neighbors) == n_neighbors:
                break
            if y[indices[j]] != target_value:
                neighbors.append(indices[j])

        # Update feature importance scores based on the distances to the nearest neighbors
        for j in range(X.shape[1]):
            diff = np.abs(X[i, j] - X[neighbors, j])
            importance_scores[j] += np.sum(diff) / n_neighbors

    # Normalize feature importance scores by the number of instances in the dataset
    importance_scores /= X.shape[0]

    return importance_scores
