import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from api.technique.variationpoints.algebraicmodel.calculate_similarity_matrix import (
    calculate_similarity_matrix_for_nlp_technique,
    create_term_frequency_matrix,
    calculate_similarity_matrix_from_term_frequencies,
    calculate_lsi_similarity_matrix,
    calculate_similarity_matrix,
)
from api.technique.variationpoints.algebraicmodel.models import AlgebraicModel
from tests.res.smart_test import SmartTest


class TestSimilarityMatrixCalculator(SmartTest):
    words = ["hello", "goodbye", "world"]
    words_a = pd.Series(["%s %s" % (words[0], words[2])])
    words_b = pd.Series(["%s %s" % (words[1], words[2])])

    upper = pd.DataFrame()
    upper["text"] = words_a
    upper["id"] = ["RE-8"]

    lower = pd.DataFrame()
    lower["text"] = words_b
    lower["id"] = ["RD-350"]

    """
    calculate_similarity_matrix_for_nlp_technique
    """

    def test_calculate_similarity_matrix_for_nlp_technique(self):
        similarity_matrix = calculate_similarity_matrix_for_nlp_technique(
            AlgebraicModel.VSM, self.upper, self.lower, False
        )
        self.assertEqual((1, 1), similarity_matrix.shape)
        self.assertGreater(similarity_matrix[0][0], 0)

    def test_calculate_similarity_matrix_for_nlp_technique_with_vocab(self):
        similarity_matrix, vocab = calculate_similarity_matrix_for_nlp_technique(
            AlgebraicModel.VSM, self.upper, self.lower, True
        )
        self.check_vocab(vocab)
        self.assertEqual((1, 1), similarity_matrix.shape)
        self.assertGreater(similarity_matrix[0][0], 0)

    """
    calculate_similarity_matrix
    """

    def test_calculate_similarity_matrix(self):
        similarity_matrix, vocab = calculate_similarity_matrix(
            self.words_a, self.words_b
        )

        self.assertEqual((1, 1), similarity_matrix.shape)
        self.assertGreater(similarity_matrix[0][0], 0)

    """
    calculate_lsa_similarity_matrix
    """

    def test_calculate_lsa_similarity_matrix(self):
        similarity_matrix, vocab = calculate_lsi_similarity_matrix(
            self.words_a, self.words_b
        )

        self.assertEqual((1, 1), similarity_matrix.shape)
        self.assertGreater(similarity_matrix[0][0], 0)

    """
    calculate_similarity_matrix_from_term_frequencies
    """

    def test_calculate_similarity_matrix_from_term_frequencies(self):
        raw_a, raw_b = self.words_a, self.words_b
        set_a, set_b, vocab = create_term_frequency_matrix(raw_a, raw_b)
        distance_matrix = calculate_similarity_matrix_from_term_frequencies(
            set_a, set_b
        )
        self.assertEqual((1, 1), distance_matrix.shape)
        self.assertGreater(distance_matrix[0][0], 0)

    """
    create_term_frequency_matrix
    """

    def test_create_term_frequency_matrix(self):
        raw_a, raw_b = self.words_a, self.words_b
        set_a, set_b, vocab = create_term_frequency_matrix(raw_a, raw_b)

        self.assertEqual(3, len(vocab.keys()))
        self.assertEqual((1, 3), set_a.shape)
        self.assertEqual((1, 3), set_b.shape)

        self.assertGreater(set_a[0, vocab["hello"]], set_a[0, vocab["world"]])
        self.assertGreater(set_b[0, vocab["goodbye"]], set_b[0, vocab["world"]])

    def test_create_term_frequency_matrix_with_count_vectorizer(self):
        raw_a, raw_b = self.words_a, self.words_b
        set_a, set_b, vocab = create_term_frequency_matrix(
            raw_a, raw_b, CountVectorizer
        )

        self.check_vocab(vocab)
        self.assertEqual((1, 3), set_a.shape)
        self.assertEqual(set_a[0, vocab["hello"]], set_a[0, vocab["world"]])

        self.assertEqual((1, 3), set_b.shape)
        self.assertEqual(set_b[0, vocab["goodbye"]], set_b[0, vocab["world"]])

    def check_vocab(self, vocab: dict):
        self.assertEqual(3, len(vocab.keys()))
        self.assertTrue(all([v_word in self.words for v_word in vocab.keys()]))
