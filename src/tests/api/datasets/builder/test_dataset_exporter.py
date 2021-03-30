import os
import time

from api.constants.paths import PATH_TO_SAMPLE_DATASETS
from api.datasets.builder.dataset_builder import DatasetBuilder
from tests.res.smart_test import SmartTest

MAXIMUM_TIME_SINCE_UPDATE = 2  # tolerable time since last update


class TestDatasetExporter(SmartTest):
    def test_export_dataset(self):
        """
        Tests that after MockDataset is exported all required folders have been updated.
        :return:
        """
        # Setup
        dataset_name = "MockDataset"
        dataset_builder = DatasetBuilder(dataset_name)
        dataset_builder.build()

        # Work
        dataset_builder.export()
        folders = ["Artifacts", "Oracles"]
        for folder_rel_path in folders:
            path_to_folder = os.path.join(
                PATH_TO_SAMPLE_DATASETS, dataset_name, folder_rel_path
            )
            check_folder_has_updated(path_to_folder)


def check_folder_has_updated(path_to_folder):
    """
    Checks that every file in folder has been modified in the last [TIME_DELTA] seconds
    :param path_to_folder:
    :return:
    """
    now = time.time()
    files = list(filter(lambda f: f[0] != ".", os.listdir(path_to_folder)))
    for file_name in files:
        path_to_file = os.path.join(path_to_folder, file_name)
        if os.path.isdir(path_to_file):
            check_folder_has_updated(path_to_file)
            continue
        file_update_time = os.path.getmtime(path_to_file)
        time_since_update = abs(file_update_time - now)
        assert time_since_update < MAXIMUM_TIME_SINCE_UPDATE, (
            "%s was not touched in export" % file_name
        )
