import os

import numpy as np
import pandas as pd

from api.constants.paths import PATH_TO_CACHE_TEMP
from api.datasets.dataset import Dataset
from api.technique.parser.itechnique_definition import ITechniqueDefinition
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix

CACHE_COLUMNS = ["dataset", "technique", "file_name"]


def load_previous_caches(path_to_data) -> pd.DataFrame:
    df = pd.DataFrame(columns=CACHE_COLUMNS)
    for file_name in os.listdir(path_to_data):
        if file_name[0] == ".":
            continue
        path_to_file = os.path.join(path_to_data, file_name)
        file_parts = file_name.split("_")
        dataset = file_parts[0]
        technique_name = "_".join(file_parts[1:])[:-4]  # removes .npy
        entry = {"dataset": dataset, "technique": technique_name, "file_name": path_to_file}
        df = df.append(entry, ignore_index=True)
    return df


class Cache:
    CACHE_ON = False
    path_to_memory = PATH_TO_CACHE_TEMP
    stored_similarities_df = load_previous_caches(path_to_memory)

    @staticmethod
    def reload():
        Cache.stored_similarities_df = load_previous_caches(Cache.path_to_memory)

    @staticmethod
    def query(dataset: Dataset, technique: ITechniqueDefinition) -> pd.DataFrame:
        assert Cache.CACHE_ON
        return Cache.stored_similarities_df[(Cache.stored_similarities_df["dataset"] == dataset.name) &
                                            (Cache.stored_similarities_df["technique"] == technique.get_name())]

    @staticmethod
    def is_cached(dataset: Dataset, technique: ITechniqueDefinition):
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
        assert Cache.is_cached(dataset, technique), "given technique has not been cached: %s" % technique.get_name()
        assert Cache.CACHE_ON
        query = Cache.query(dataset, technique)
        file_name = query.iloc[0]["file_name"]
        loaded_matrix = np.load(file_name, allow_pickle=True)
        return loaded_matrix

    @staticmethod
    def cleanup(dataset_name: str):
        for index, row in Cache.stored_similarities_df.iterrows():
            dataset, _, file_name = row
            if dataset == dataset_name:
                if os.path.exists(file_name):
                    os.remove(file_name)

        Cache.stored_similarities_df = Cache.stored_similarities_df[
            (Cache.stored_similarities_df["dataset"] != dataset_name)]
