import numpy as np
from .utils import cosine_similarity

"""
    this file is for concatenate functions
    you can implement your own concatenate functions here

    *** main method is based on similarity between embeddings ***

    function signature:
        args: embeddings (np.ndarray), any other arguments if needed
        returns: concatenated indexes (list)--> should be the final theme indexes

"""


# concatenate based on time line
def concate_time_based(embeddings:np.ndarray, threshold=0.6)->list:
    """
    concatinate based on time line

    Args:
    - embeddings: segment embeddings
    - threshold: similarity threshold

    Returns:
    - list: concatenated indexes
    """

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
def concate_clustering(embeddings:np.ndarray)->list:
    """
    concatinate based on clustering

    Args:
    - embeddings: segment embeddings

    Returns:
    - list: concatenated indexes
    """

    concatenated_indexes = []
    # concatenated_indexes.append( [same indexes list] )
    
    return concatenated_indexes

# concatenate based on knn
def concate_knn(embeddings:np.ndarray)->list:
    """
    concatinate based on knn

    Args:
    - embeddings: segment embeddings

    Returns:
    - list: concatenated indexes
    """
    concatenated_indexes = []
    # concatenated_indexes.append( [same indexes list] )
    
    return concatenated_indexes

# your best concatenate function
def concate_custom(embeddings:np.ndarray)->list:
    """
    concatinate based on custom

    Args:
    - embeddings: segment embeddings

    Returns:
    - list: concatenated indexes
    """
    concatenated_indexes = []
    # concatenated_indexes.append( [same indexes list] )
    
    return concatenated_indexes