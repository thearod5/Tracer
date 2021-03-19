import os

import numpy as np

from api.cache.cache import Cache
from api.datasets.dataset import Dataset
from api.metrics.models import SIMILARITY_MATRIX_EXTENSION
from api.tracer import Tracer
from tests.res.test_technique_helper import TestTechniqueHelper


class TestCache(TestTechniqueHelper):

    def test_direct(self):
        Cache.cleanup(self.dataset.name)
        original_cache_value = Cache.CACHE_ON
        Cache.CACHE_ON = True
        self.assertFalse(Cache.is_cached(self.dataset, self.get_direct_definition()))

        scores = np.array([[.1, .2, .3]])
        # VP 2. Storing similarities makes files and makes entry
        Cache.store_similarities(self.dataset, self.get_direct_definition(), scores)
        files_written = list(filter(lambda f: SIMILARITY_MATRIX_EXTENSION in f, os.listdir(Cache.path_to_memory)))
        self.assertTrue(Cache.is_cached(self.dataset, self.get_direct_definition()))
        self.assertEqual(1, len(files_written))

        # VP 3. Able to read from similarities
        similarities = Cache.get_similarities(self.dataset, self.get_direct_definition())
        self.assertEqual(scores[0, 0], similarities[0, 0])
        self.assertEqual(scores[0, 1], similarities[0, 1])
        self.assertEqual(scores[0, 2], similarities[0, 2])

        # VP 4. All files are deleted
        Cache.cleanup(self.dataset.name)
        extra_files = list(filter(lambda f: SIMILARITY_MATRIX_EXTENSION in f, os.listdir(Cache.path_to_memory)))
        self.assertEqual(0, len(extra_files))
        Cache.CACHE_ON = original_cache_value

    def test_transitive(self):
        original_cache_value = Cache.CACHE_ON
        Cache.CACHE_ON = True
        Cache.cleanup(self.dataset.name)
        self.assertFalse(Cache.is_cached(self.dataset, self.get_transitive_definition()))

        tracer = Tracer()
        tracer.get_metrics(self.dataset.name, self.transitive_technique_name)

        files_in_cache = list(filter(lambda f: SIMILARITY_MATRIX_EXTENSION in f, os.listdir(Cache.path_to_memory)))

        self.assertEqual(3, len(files_in_cache))

        def create_name(name: str):
            return self.dataset.name + "_" + name + ".npy"

        self.assertIn(create_name(self.transitive_upper_comp), files_in_cache)
        self.assertIn(create_name(self.transitive_component_b_name), files_in_cache)
        self.assertIn(create_name(self.transitive_technique_name), files_in_cache)

        Cache.cleanup(self.dataset.name)
        Cache.CACHE_ON = original_cache_value

    def test_cleanup_deletes_on_dataset(self):
        original_cache_value = Cache.CACHE_ON
        Cache.CACHE_ON = True

        dataset_other_name = "EasyClinic"
        dataset_other = Dataset(dataset_other_name)

        tracer = Tracer()
        tracer.get_metrics(dataset_other_name, self.direct_technique_name)
        tracer.get_metrics(self.dataset.name, self.direct_technique_name)

        self.assertTrue(Cache.is_cached(dataset_other, self.get_direct_definition()))
        self.assertTrue(Cache.is_cached(self.dataset, self.get_direct_definition()))

        Cache.cleanup(self.dataset.name)

        self.assertTrue(Cache.is_cached(dataset_other, self.get_direct_definition()))
        self.assertFalse(Cache.is_cached(self.dataset, self.get_direct_definition()))

        Cache.cleanup(dataset_other_name)

        self.assertFalse(Cache.is_cached(dataset_other, self.get_direct_definition()))
        self.assertFalse(Cache.is_cached(self.dataset, self.get_direct_definition()))

        Cache.CACHE_ON = original_cache_value
