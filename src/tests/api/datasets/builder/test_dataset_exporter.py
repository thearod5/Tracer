import os
import time

from api.constants.paths import PATH_TO_DATASETS
from api.datasets.builder.dataset_builder import DatasetBuilder
from api.datasets.builder.dataset_exporter import export_dataset
from tests.res.smart_test import SmartTest

TIME_DELTA = 2  # tolerable time since last update


class TestDatasetExporter(SmartTest):
    """
    export_dataset
    """

    def test_export_dataset(self):
        # Setup
        dataset_name = "MockDataset"
        builder = DatasetBuilder(dataset_name, create=True)

        # Work
        export_dataset(builder)
        folders = ["Artifacts", "Oracles"]
        for folder_rel_path in folders:
            path_to_folder = os.path.join(
                PATH_TO_DATASETS, dataset_name, folder_rel_path
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
        assert time_since_update < TIME_DELTA
