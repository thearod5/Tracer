import pandas as pd
from scipy.sparse import vstack
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

from api.datasets.multi_level_artifacts import ArtifactLevel
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix

"""
A DistanceMatrix is a 

multi-dimensional matrix containing similarity scores calculated
via cosine_similarity.
"""

"""
A TermFrequencyMatrix is a 

multi-dimensional matrix containing as rows a set of 
textual documents and as CACHE_COLUMNS each word appearing in the aggregate vocabulary of
the documents. Each entry in the matrix is a number meant to represent how much
"weight" a given column (word) has in each row (text doc).
"""
from scipy.sparse import csr_matrix

DocumentTermMatrix = csr_matrix


def calculate_similarity_matrix_for_nlp_technique(nlp_type: AlgebraicModel,
                                                  upper_level: ArtifactLevel,
                                                  lower_level: ArtifactLevel,
                                                  return_vocab=False) -> SimilarityMatrix:
    similarity_matrix_calculators = {
        AlgebraicModel.VSM: calculate_similarity_matrix,
        AlgebraicModel.LSI: calculate_lsa_similarity_matrix,
    }
    similarity_matrix, vocab = similarity_matrix_calculators[nlp_type](upper_level["text"], lower_level["text"])
    if return_vocab:
        return similarity_matrix, vocab
    return similarity_matrix


def calculate_similarity_matrix(raw_a, raw_b) -> (SimilarityMatrix, dict):
    """
    Calculates DistanceMatrix by transforming given documents into
    term frequency technique_matrices (weighted via TF-IDF).

    :param raw_a: {Listof String} - docs representing the rows of the matrix
    :param raw_b: {Listof String} - docs representing the CACHE_COLUMNS of the matrix
    :return: {DistanceMatrix} From A to B
    """
    set_a, set_b, vocab = create_term_frequency_matrix(raw_a, raw_b)
    similarity_matrix = calculate_similarity_matrix_from_term_frequencies(set_a, set_b)
    return similarity_matrix, vocab


def calculate_lsa_similarity_matrix(raw_a, raw_b) -> (SimilarityMatrix, dict):
    """
    Creates a Distance Matrix (calc. via cosine-similarity)
    where the given matrix is first reduced via lsa.

    Note, the resulting dimensions of the singular value decomposition is (a, a) where
    a = min(number of documents, number components, number of features). In our case,
    requirements + designs normally will not satisfy 100 records. In means that our
    number of resulting components varying between the upper and lower technique_matrices.

    :param raw_a {Listof String} - Represents the rows of the matrix
    :param raw_b {Listof String} - Represents the cols of the matrix
    :return {Experiment.Technique.AlgebraicModel} From every doc in A to B
    """
    matrix_a, matrix_b, vocab = create_term_frequency_matrix(raw_a, raw_b)
    n_components = min(len(raw_a), len(raw_b), 100)  # average number of documents

    # Singular Value Decomposition on Term Frequencies = LSI
    lsa_model = TruncatedSVD(n_components=n_components, random_state=42)
    lsa_model.fit(vstack([matrix_a, matrix_b]))  # essentially appending docs vectorized
    matrix_a_lsa = lsa_model.transform(matrix_a)
    matrix_b_lsa = lsa_model.transform(matrix_b)

    similarity_matrix = calculate_similarity_matrix_from_term_frequencies(matrix_a_lsa, matrix_b_lsa)

    return similarity_matrix, vocab


def calculate_similarity_matrix_from_term_frequencies(tf_a: DocumentTermMatrix,
                                                      tf_b: DocumentTermMatrix) -> SimilarityMatrix:
    return 1 - pairwise_distances(tf_a, Y=tf_b, metric="cosine", n_jobs=-1)


def create_term_frequency_matrix(raw_a: pd.Series,
                                 raw_b: pd.Series,
                                 vectorizer=TfidfVectorizer) -> (DocumentTermMatrix, DocumentTermMatrix, dict):
    """
    Creates 2 TermFrequencyMatrices (one for A another for B) where the weight of
    each (row, col) pair is calculated via TF-IDF
    :param vectorizer: vectorizer for assigning weights to words, must be one of sklearn.text.extraction
    :param raw_a : The documents whose matrix is the first element
    :param raw_b : The documents whose matrix is the second element
    :return: CountMatrix for raw_a and raw_b, and also the vocabulary used
    """
    model = vectorizer()
    combined = pd.concat([raw_a, raw_b], axis=0)

    model.fit(combined)  # creates vocabulary with features from both A and B
    set_a: DocumentTermMatrix = model.transform(raw_a)
    set_b: DocumentTermMatrix = model.transform(raw_b)

    return set_a, set_b, model.vocabulary_
