"""
The Cache module is intended to be used to speed up technique calculations. Namely, transitive techniques utilize
component similarity matrices that can be reused to avoid redundant calculation. It is beneficial to turn
on the Cache when calculating a lot of techniques, note, by default caching is turned off.

:TODO: create a unique key for item in cache and only delete those so parallel runs do not interfere.
"""
import os

import numpy as np
import pandas as pd

from api.constants.paths import PATH_TO_CACHE_TEMP
from api.datasets.dataset import Dataset
from api.technique.parser.itechnique_definition import ITechniqueDefinition
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix

CACHE_COLUMNS = ["dataset", "technique", "file_name"]
DEFAULT_IS_CACHE_ENABLED = False


def load_previous_caches(path_to_data: str) -> pd.DataFrame:
    """
    Returns DataFrame loaded with all saved entries in the cache folder.
    :param path_to_data:
    :return: DataFrame containing
    """
    previous_caches_df = pd.DataFrame(columns=CACHE_COLUMNS)
    for file_name in os.listdir(path_to_data):
        if file_name[0] == ".":
            continue
        path_to_file = os.path.join(path_to_data, file_name)
        file_parts = file_name.split("_")
        dataset = file_parts[0]
        technique_name = "_".join(file_parts[1:])[:-4]  # removes .npy
        entry = {"dataset": dataset, "technique": technique_name, "file_name": path_to_file}
        previous_caches_df = previous_caches_df.append(entry, ignore_index=True)
    return previous_caches_df


class Cache:
    """
    Represents a module to reading and storing SimilarityMatrix produced by techniques when applying them to specified
    Datasets. The cache folder is predetermined to be an ignored folder inside of the root directory. Its path can
    be found in api.constants.paths.

    Example:
        When running an experiment using intermediate techniques it is recommended to use the cache for performance
        boosts; namely, the sub-components of intermediate techniques can be reused and one can escape redundant
        calculation.

    """
    CACHE_ON = DEFAULT_IS_CACHE_ENABLED
    path_to_memory = PATH_TO_CACHE_TEMP
    stored_similarities_df = load_previous_caches(path_to_memory)

    @staticmethod
    def reload():
        """
        Reads cache folder and reloads the DataFrame storing the meta-data for each item.
        :return:
        """
        Cache.stored_similarities_df = load_previous_caches(Cache.path_to_memory)

    @staticmethod
    def query(dataset: Dataset, technique: ITechniqueDefinition) -> pd.DataFrame:
        """
        Returns a list of DataFrame containing items matching the given dataset and technique.
        :param dataset: The dataset which the technique was applied to.
        :param technique: The technique whose SimilarityMatrix we are querying for.
        :return: DataFrame
        """
        assert Cache.CACHE_ON
        return Cache.stored_similarities_df[(Cache.stored_similarities_df["dataset"] == dataset.name) &
                                            (Cache.stored_similarities_df["technique"] == technique.get_name())]

    @staticmethod
    def is_cached(dataset: Dataset, technique: ITechniqueDefinition):
        """
        Returns whether the given technique definition has been cached for given dataset.
        :param dataset: the dataset of whose artifacts would be represented by potentially stored similarity matrix
        :param technique: the technique of producing the potentially stored similarity matrix on given dataset
        :return:
        """
        if not Cache.CACHE_ON:
            return False
        query = Cache.query(dataset, technique)
        return len(query) == 1

    @staticmethod
    def store_similarities(dataset: Dataset, technique: ITechniqueDefinition, similarity_matrix: SimilarityMatrix):
        """
        Stored similarities in cache if never seen, updates cache otherwise
        :param dataset: The dataset the technique was applied to to get given similarity table
        :param technique: The technique used to calculate the similarities below
        :param similarity_matrix: The similarity to score in the cache
        :return:
        """
        assert isinstance(similarity_matrix, np.ndarray), type(similarity_matrix)
        if not Cache.CACHE_ON:
            return
        file_name = "_".join([dataset.name, technique.get_name()])
        export_path = os.path.join(Cache.path_to_memory, file_name) + ".npy"
        np.save(export_path, similarity_matrix)

        entry = {"dataset": dataset.name, "technique": technique.get_name(), "file_name": export_path}
        if not Cache.is_cached(dataset, technique):
            Cache.stored_similarities_df = Cache.stored_similarities_df.append(entry, ignore_index=True)

    @staticmethod
    def get_similarities(dataset: Dataset, technique: ITechniqueDefinition) -> SimilarityMatrix:
        """
        Returns similarity matrix for given technique on given Dataset
        :param dataset: dataset whose artifacts to compare
        :param technique: definition describing how to produce the similarity values
        :return: numpy.ndarray containing similarity values
        """
        assert Cache.is_cached(dataset, technique), "given technique has not been cached: %s" % technique.get_name()
        assert Cache.CACHE_ON
        query = Cache.query(dataset, technique)
        file_name = query.iloc[0]["file_name"]
        loaded_matrix = np.load(file_name, allow_pickle=True)
        return loaded_matrix

    @staticmethod
    def cleanup(dataset_name: str):
        """
        Removes all saved files in the cache. Currently, calling this method while parallel operations are ongoing on
        the same dataset have the potential to break their execution.
        same dataset.
        :param dataset_name:
        :return: None
        """
        for _, row in Cache.stored_similarities_df.iterrows():
            dataset, _, file_name = row
            if dataset == dataset_name:
                if os.path.exists(file_name):
                    os.remove(file_name)

        Cache.stored_similarities_df = Cache.stored_similarities_df[
            (Cache.stored_similarities_df["dataset"] != dataset_name)]
