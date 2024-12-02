import numpy as np
from .utils import cosine_similarity
from .segment_embedding import *
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN

"""
    this file is for concatenate functions
    you can implement your own concatenate functions here

    *** main method is based on similarity between embeddings ***

    function signature:
        args: text segments (list), any other arguments if needed
        returns: concatenated indexes (list)--> should be the final theme indexes

"""

# concatenate based on time line
def concate_time_based(segments:list, threshold=0.6)->list:
    """
    concatinate based on time line

    Args:
    - segments: segment list
    - threshold: similarity threshold

    Returns:
    - list: concatenated indexes
    """
     
    embeddings = encode_segments(segments)
    if not isinstance(embeddings, np.ndarray):
        raise ValueError("Input embeddings must be a numpy array.")
    if len(embeddings) == 0:
        return []

    concatenated_indexes = [[0]]

    for i in range(1, len(embeddings)):
        if cosine_similarity(embeddings[i-1], embeddings[i]) > threshold:
            concatenated_indexes[-1].append(i)
        else:
            concatenated_indexes.append([i])        

    return concatenated_indexes

# concatenate based on clustering
def concate_clustering(segments: list, eps: float = 0.15, min_samples: int = 3) -> list:
    """
    Concatenate based on DBSCAN clustering.

    Args:
    - segments: segment list
    - eps: Maximum distance between two samples for them to be considered as in the same cluster.
    - min_samples: Minimum number of samples in a neighborhood for a point to be considered a core point.

    Returns:
    - list: Concatenated indexes as groups.
    """
    embeddings = encode_segments(segments)
    if not isinstance(embeddings, np.ndarray):
        raise ValueError("Input embeddings must be a numpy array.")
    if len(embeddings) == 0:
        return []

    # Perform DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    cluster_labels = dbscan.fit_predict(embeddings)

    # Group indexes by cluster
    concatenated_indexes = []
    unique_labels = set(cluster_labels)

    for label in unique_labels:
        if label == -1:  # Noise points are labeled as -1
            continue
        cluster_indexes = np.where(cluster_labels == label)[0].tolist()
        concatenated_indexes.append(cluster_indexes)

    return concatenated_indexes

# concatenate based on knn
def concate_knn(segments: list, k: int = 20, threshold: float = 0.6) -> list:
    """
    Concatenate based on k-NN similarity.

    Args:
    - segments: segment list
    - k: Number of nearest neighbors to consider.
    - threshold: Similarity threshold to group embeddings.

    Returns:
    - list: Concatenated indexes as groups.
    """
    embeddings = encode_segments(segments)
    if not isinstance(embeddings, np.ndarray):
        raise ValueError("Input embeddings must be a numpy array.")
    if len(embeddings) == 0:
        return []

    # Initialize Nearest Neighbors model
    nn_model = NearestNeighbors(n_neighbors=k, metric='cosine')
    nn_model.fit(embeddings)

    # Find k nearest neighbors for each embedding
    distances, indices = nn_model.kneighbors(embeddings)

    # Grouping based on the threshold
    concatenated_indexes = []
    visited = set()

    for idx, neighbors in enumerate(indices):
        if idx in visited:
            continue
        
        group = [idx]
        visited.add(idx)

        for neighbor_idx, distance in zip(neighbors[1:], distances[idx][1:]):  # Skip self (first neighbor)
            if neighbor_idx not in visited and distance <= threshold:
                group.append(neighbor_idx)
                visited.add(neighbor_idx)
        
        concatenated_indexes.append(sorted(group))

    return concatenated_indexes


# timline based + clustering
def concate_time_clustering(segments: list, threshold=0.6, eps: float = 0.15, min_samples: int = 3) -> list:
    """
    Concatenate based on time line and clustering.

    Args:
    - segments: segment list
    - threshold: similarity threshold
    - eps: Maximum distance between two samples for them to be considered as in the same cluster.
    - min_samples: Minimum number of samples in a neighborhood for a point to be considered a core point.

    Returns:
    - list: Concatenated indexes as groups.
    """
    embeddings = encode_segments(segments)
    if not isinstance(embeddings, np.ndarray):
        raise ValueError("Input embeddings must be a numpy array.")
    if len(embeddings) == 0:
        return []

    concatenated_indexes = [[0]]

    for i in range(1, len(embeddings)):
        if cosine_similarity(embeddings[i-1], embeddings[i]) > threshold:
            concatenated_indexes[-1].append(i)
        else:
            concatenated_indexes.append([i])

    # based on time line make new segments and embeddings
    new_segments = []
    for group in concatenated_indexes:
        new_segments.append(" ".join([segments[gi] for gi in group]))
    new_embeddings = encode_segments(new_segments)

    # Perform DBSCAN clustering
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    cluster_labels = dbscan.fit_predict(new_embeddings)

    # Group indexes by cluster
    concatenated_indexes = []
    unique_labels = set(cluster_labels)

    for label in unique_labels:
        if label == -1:
            continue
        cluster_indexes = np.where(cluster_labels == label)[0].tolist()
        concatenated_indexes.append(cluster_indexes)


    return concatenated_indexes


# TODO: Implement your own concatenate function here
def concate_custom(segments: list, **kwargs) -> list:
    """
    Concatenate based on custom logic.

    Args:
    - segments: segment list
    - **kwargs: Additional arguments for custom logic.

    Returns:
    - list: Concatenated indexes as groups.
    """
    raise NotImplementedError("Please implement your own concatenate function.")
