import os
import sys
import unittest
from pathlib import Path  # Python 3.6+ only

from dotenv import load_dotenv

ENV_PATH = os.path.join(Path(__file__).parent.absolute(), "..", "..", ".env")
assert os.path.isfile(ENV_PATH), "Make sure .env file is configured"
load_dotenv(dotenv_path=ENV_PATH)
PATH_TO_ROOT = os.environ.get("PATH_TO_ROOT")

sys.path.remove(os.path.join(PATH_TO_ROOT, "src", "tests"))
sys.path.append(os.path.join(PATH_TO_ROOT, "src"))

from api.constants.paths import PATH_TO_CACHE_TEMP
from api.experiment.cache import Cache
from tests.api.datasets.builder.test_dataset_builder import TestDatasetBuilder
from tests.api.datasets.builder.test_dataset_exporter import TestDatasetExporter
from tests.api.datasets.builder.test_structure_definition_parser import TestStructureDefinitionParser
from tests.api.datasets.builder.test_trace_creator import TestTraceCreator
from tests.api.datasets.builder.test_transitive_traces import TestTransitiveTraceMatrixCreator
from tests.api.datasets.cleaning.test_clean_doc import TestCleanDoc
from tests.api.datasets.parser.test_java_parser import TestJavaParser
from tests.api.datasets.parser.test_source_code_parser import TestSourceCodeParser
from tests.api.experiment.test_cache import TestCache
from tests.api.metrics.test_lag_global import TestLag
from tests.api.metrics.test_map import TestMap
from tests.api.metrics.test_metric_table import TestMetricTable
from tests.api.technique.calculator.aggregation.test_pca import TestPCA
from tests.api.technique.calculator.aggregation.test_transitive_aggregation import TestIntermediateAggregation
from tests.api.technique.calculator.algebraicmodel.test_calculate_similarity_matrix import TestCalculateSimilarityMatrix
from tests.api.technique.calculator.algebraicmodel.test_similarity_matrix_calculator import \
    TestSimilarityMatrixCalculator
from tests.api.technique.calculator.scalers.test_scalers import TestScalers
from tests.api.technique.combined.test_combined_calculator import TestCombinedCalculationPipeline
from tests.api.technique.combined.test_combined_definition import TestCombinedDefinition
from tests.api.technique.combined.test_combined_technique import TestCombinedTechnique
from tests.api.technique.direct.test_direct_calculator import DirectCalculator
from tests.api.technique.direct.test_direct_definition import TestDirectDefinition
from tests.api.technique.direct.test_direct_technique import TestDirectTechnique
from tests.api.technique.sampled.artifacts.test_sampled_artifacts_calculator import TestSampledArtifactsCalculator
from tests.api.technique.sampled.artifacts.test_sampled_artifacts_technique import TestSampledArtifactsTechnique
from tests.api.technique.sampled.test_sampled_artifacts_definition import TestSampledArtifactsDefinition
from tests.api.technique.sampled.traces.test_sampled_traces_calculator import TestSampledTracesCalculator
from tests.api.technique.sampled.traces.test_sampled_traces_technique import TestSampledTracesTechnique
from tests.api.technique.test_definition_parser import TestTechniqueNameParser
from tests.api.technique.test_itechnique_definition import TestITechniqueDefinition
from tests.api.technique.test_technique import TestTechnique
from tests.api.technique.transitive.test_transitive_calculator import TestIntermediateCalculationPipeline
from tests.api.technique.transitive.test_transitive_definition import TestIntermediateDefinition
from tests.api.technique.transitive.test_transitive_technique import TestIntermediateTechnique
from tests.api.tracer.test_technique_aggregation_calculator import TestTechniqueAggregationCalculator
from tests.api.util.test_file_operations import TestFileOperations

if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    util_tests = [TestFileOperations, ]
    dataset_tests = [TestCleanDoc,
                     TestJavaParser,
                     TestSourceCodeParser,
                     TestStructureDefinitionParser,
                     TestTraceCreator,
                     TestTransitiveTraceMatrixCreator,
                     TestDatasetBuilder,
                     TestDatasetExporter, ]

    technique_tests = [TestTechniqueNameParser,
                       TestITechniqueDefinition,
                       TestTechnique,
                       TestDirectDefinition,
                       DirectCalculator,
                       TestDirectTechnique,
                       TestIntermediateDefinition,
                       TestIntermediateCalculationPipeline,
                       TestIntermediateTechnique,
                       TestCombinedDefinition,
                       TestCombinedCalculationPipeline,
                       TestCombinedTechnique,
                       TestSampledArtifactsDefinition,
                       TestSampledArtifactsCalculator,
                       TestSampledArtifactsTechnique,
                       TestSampledTracesTechnique,
                       TestSampledTracesCalculator,
                       ]

    calculator_tests = [TestSimilarityMatrixCalculator,
                        TestCalculateSimilarityMatrix,
                        TestPCA,
                        TestScalers,
                        TestIntermediateAggregation,
                        TestTechniqueAggregationCalculator
                        ]
    metric_tests = [TestLag,
                    TestMap,
                    TestMetricTable, ]
    experiment_tests = [TestCache]

    classes_to_test = util_tests + dataset_tests + technique_tests \
                      + calculator_tests + metric_tests + experiment_tests

    for c_to_test in classes_to_test:
        test_suite.addTest(c_to_test())

    # RUN
    Cache.path_to_memory = os.path.join(PATH_TO_CACHE_TEMP, ".test")
    Cache.reload()
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
