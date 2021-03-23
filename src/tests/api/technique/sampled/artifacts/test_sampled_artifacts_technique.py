from api.extension.cache import Cache
from api.technique.definitions.sampled.artifacts.technique import (
    SampledIntermediateTechnique,
)
from api.technique.definitions.sampled.definition import SAMPLED_COMMAND_SYMBOL
from api.tracer import Tracer
from tests.res.test_technique_helper import TestTechniqueHelper


class TestSampledArtifactsTechnique(TestTechniqueHelper):
    def test_use_case(self):
        technique = SampledIntermediateTechnique(
            self.sampled_parameters, self.sampled_components
        )
        data = technique.calculate_technique_data(self.dataset)

        self.assertEqual(technique.definition, data.technique)
        self.assertEqual(self.dataset, data.dataset)

    def test_get_symbol(self):
        self.assertEqual(
            SAMPLED_COMMAND_SYMBOL, SampledIntermediateTechnique.get_symbol()
        )

    def test_combined_sampled(self):
        dataset = "EasyClinic"
        tracer = Tracer()
        Cache.CACHE_ON = True

        metrics_a = tracer.get_metrics(
            dataset, self.combined_sampled_artifacts_technique_name
        )
        metrics_b = tracer.get_metrics(
            dataset, self.combined_sampled_artifacts_technique_name
        )

        self.assertNotEqual(metrics_a[0].ap, metrics_b[0].ap)
        self.assertNotEqual(metrics_a[0].auc, metrics_b[0].auc)

        Cache.cleanup(dataset)
