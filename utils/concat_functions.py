import numpy as np
from utils import cosine_similarity

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
    concatenated_indexes = []
    # concatenated_indexes.append( [same indexes list] )
    
    raise concatenated_indexes

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
    
    raise concatenated_indexes

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
    
    raise concatenated_indexes

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
    
    raise concatenated_indexes