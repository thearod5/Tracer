import warnings

import numpy as np
from sklearn.decomposition import PCA

from api.technique.variationpoints.aggregation.pca_aggregation import get_weights, aggregate_pca
from tests.res.smart_test import SmartTest


class TestPCA(SmartTest):

    def test_weights_na(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            x_train = np.array([[1, 2, 3],
                                [1, 2, 3],
                                [1, 2, 3],
                                [1, 2, 3]])
            weights = get_weights(x_train)
            self.assertEqual(3, len(weights))
            self.assertEqual(.33, round(weights[0], 2))
            self.assertEqual(.33, round(weights[1], 2))
            self.assertEqual(.33, round(weights[2], 2))
            self.assertEqual(1, sum(weights), "Sum of weights")

    def test_weights_use_case(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            x_train = np.array([[1, 2, 3],
                                [2, 2, 3],
                                [3, 2, 3]])
            weights = get_weights(x_train)
            self.assertEqual(1, sum(weights))
            self.assertGreater(weights[0], weights[1])

    def test_pca_na(self):
        x_train = np.array([[1, 2, 3], [3, 4, 5], [6, 7, 8]])
        predictions = aggregate_pca(x_train)
        assert len(predictions) == 3, predictions
        assert predictions[0] == 1
        assert predictions[1] == 3
        assert predictions[2] == 6

    def test_inverse_needed(self):
        x_train = np.array([[1, 2, 3], [2, 5, 6], [7, 8, 9], [1, 2, 2]])
        pca = PCA(n_components=2)
        pca.fit(x_train)
        assert pca.n_components_ == 2
        assert pca.n_features_ == 3, pca.n_features_
