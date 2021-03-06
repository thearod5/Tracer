"""
TODO
"""
from typing import List

from api.datasets.dataset import Dataset
from api.metrics.calculator import calculate_metrics_for_scoring_table
from api.tables.metric_table import Metrics
from api.technique.definitions.combined.technique import create_technique_from_name
from api.technique.parser.data import TechniqueData


class Tracer:
    """
    Proxy class for parsing technique definitions and evaluating them on given datasets.
    """

    def __init__(self):
        self.datasets: [Dataset] = []

    def get_dataset(self, name: str):
        """
        TODO
        :param name:
        :return:
        """
        query = list(filter(lambda d: d.name == name, self.datasets))
        if len(query) == 0:
            dataset = Dataset(name)
            self.datasets.append(dataset)
            return dataset
        return query[0]

    def get_technique_data(
        self, dataset_name: str, technique_name: str
    ) -> TechniqueData:
        """
        TODO
        :param dataset_name:
        :param technique_name:
        :return:
        """
        dataset: Dataset = self.get_dataset(dataset_name)
        technique = create_technique_from_name(technique_name)

        return technique.calculate_technique_data(dataset)

    def get_metrics(
        self, dataset_name: str, technique_name: str, summary_metrics=True
    ) -> List[Metrics]:
        """
        Returns list of metrics of technique per query in dataset.
        :param dataset_name: name of dataset
        :param technique_name: technique definition to evaluate
        :param summary_metrics: if true metrics of all queries are taken, otherwise individual queries are used
        :return: list of metrics, one per query. If summary_metrics is True, then list will contain a single item.
        """
        dataset: Dataset = self.get_dataset(dataset_name)
        technique = create_technique_from_name(technique_name)

        technique_data = technique.calculate_technique_data(dataset)
        scoring_table = technique_data.get_scoring_table()

        n_queries = len(dataset.artifacts[technique.definition.source_level])
        return calculate_metrics_for_scoring_table(
            scoring_table, n_queries, summary_metrics=summary_metrics
        )
