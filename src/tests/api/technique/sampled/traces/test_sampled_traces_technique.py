from api.experiment.cache import Cache
from api.technique.definitions.sampled.traces.technique import SampledTracesTechnique, SAMPLED_TRACED_COMMAND_SYMBOL
from api.tracer import Tracer
from tests.res.test_technique_helper import TestTechniqueHelper


class TestSampledTracesTechnique(TestTechniqueHelper):

    def test_use_case(self):
        technique = SampledTracesTechnique(self.sampled_parameters,
                                           self.sampled_components)
        data = technique.calculate_technique_data(self.dataset)

        self.assertEqual(technique.definition, data.technique)
        self.assertEqual(self.dataset, data.dataset)

    def test_get_symbol(self):
        self.assertEqual(SAMPLED_TRACED_COMMAND_SYMBOL, SampledTracesTechnique.get_symbol())

    def test_combined_sampled(self):
        dataset = "EasyClinic"
        tracer = Tracer()
        Cache.cleanup(dataset)
        Cache.CACHE_ON = True

        metrics_a = tracer.get_metrics(dataset, self.combined_sampled_traces_technique_name)
        metrics_b = tracer.get_metrics(dataset, self.combined_sampled_traces_technique_name)

        self.assertEqual(1, len(metrics_a))
        self.assertNotEqual(metrics_a[0].ap, metrics_b[0].ap)
        self.assertNotEqual(metrics_a[0].auc, metrics_b[0].auc)

        Cache.cleanup(dataset)
