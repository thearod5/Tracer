from api.datasets.dataset import Dataset
from api.technique.definitions.combined.technique import CombinedTechniqueDefinition
from api.technique.definitions.direct.definition import (
    DirectTechniqueDefinition,
    DIRECT_COMMAND_SYMBOL,
)
from api.technique.definitions.sampled.definition import (
    SAMPLED_COMMAND_SYMBOL,
    SampledTechniqueDefinition,
)
from api.technique.definitions.sampled.traces.technique import (
    SAMPLED_TRACED_COMMAND_SYMBOL,
)
from api.technique.definitions.transitive.definition import (
    TRANSITIVE_COMMAND_SYMBOL,
    TransitiveTechniqueDefinition,
)
from api.technique.parser.data import TechniqueData
from api.technique.variationpoints.aggregation.aggregation_method import (
    AggregationMethod,
)
from api.technique.variationpoints.algebraicmodel.models import (
    AlgebraicModel,
    SimilarityMatrix,
)
from api.technique.variationpoints.scalers.scaling_method import ScalingMethod
from api.technique.variationpoints.tracetype.trace_type import TraceType
from tests.res.smart_test import SmartTest


class SimilarityMatrixMock(object):
    pass


"""
Some predefined techniques that tests can share
"""


class TestTechniqueHelper(SmartTest):
    d_name = "MockDataset"
    dataset = Dataset(d_name)
    """
    Direct
    """
    direct_algebraic_model = AlgebraicModel.VSM
    direct_trace_type = TraceType.NOT_TRACED
    direct_parameters = [direct_algebraic_model.value, direct_trace_type.value]
    direct_components = ["0", "2"]
    direct_definition = [DIRECT_COMMAND_SYMBOL, direct_parameters, direct_components]

    """
    Intermediate
    """
    transitive_algebraic_model = AlgebraicModel.VSM
    transitive_aggregation_type = AggregationMethod.SUM
    transitive_component_scaling_type = ScalingMethod.GLOBAL
    transitive_component_trace_type = TraceType.NOT_TRACED

    transitive_component_a = [
        DIRECT_COMMAND_SYMBOL,
        [transitive_algebraic_model.value, transitive_component_trace_type.value],
        ["0", "1"],
    ]
    transitive_upper_comp = "(%s (%s %s) (%s %s))" % (
        DIRECT_COMMAND_SYMBOL,
        transitive_algebraic_model.value,
        transitive_component_trace_type.value,
        "0",
        "1",
    )
    transitive_component_b = [
        DIRECT_COMMAND_SYMBOL,
        [transitive_algebraic_model.value, transitive_component_trace_type.value],
        ["1", "2"],
    ]
    transitive_component_b_name = "(%s (%s %s) (%s %s))" % (
        DIRECT_COMMAND_SYMBOL,
        transitive_algebraic_model.value,
        transitive_component_trace_type.value,
        "1",
        "2",
    )

    transitive_parameters = [
        transitive_aggregation_type.value,
        transitive_component_scaling_type.value,
    ]
    transitive_components = [transitive_component_a, transitive_component_b]
    transitive_technique_definition = [
        TRANSITIVE_COMMAND_SYMBOL,
        transitive_parameters,
        transitive_components,
    ]

    """
    Traced Components
    """
    traced_component_type = TraceType.TRACED
    traced_aggregation_value = AggregationMethod.MAX
    traced_direct_component_a = [
        DIRECT_COMMAND_SYMBOL,
        [transitive_algebraic_model.value, traced_component_type.value],
        ["0", "1"],
    ]
    traced_direct_component_b = [
        DIRECT_COMMAND_SYMBOL,
        [transitive_algebraic_model.value, traced_component_type.value],
        ["1", "2"],
    ]
    traced_components = [traced_direct_component_a, traced_direct_component_b]
    traced_parameters = [
        traced_aggregation_value.value,
        transitive_component_scaling_type.value,
    ]
    """
    Sampled Artifacts
    """
    sample_percentage = 0.5
    sampled_parameters: [str] = transitive_parameters + [repr(sample_percentage)]
    sampled_components = transitive_components
    sampled_artifacts_definition = [
        SAMPLED_COMMAND_SYMBOL,
        sampled_parameters,
        sampled_components,
    ]
    sampled_traces_definition = [
        SAMPLED_TRACED_COMMAND_SYMBOL,
        sampled_parameters,
        sampled_components,
    ]

    """
    Combined
    """
    combined_aggregation_type = AggregationMethod.SUM
    combined_parameters = ["SUM"]
    combined_components = [direct_definition, transitive_technique_definition]

    """
    Combined (with sampled transitive)
    """
    combined_sampled_artifacts_components = [
        direct_definition,
        sampled_artifacts_definition,
    ]
    combined_sampled_traces_components = [direct_definition, sampled_traces_definition]

    direct_technique_name = "(. (VSM NT) (0 2))"
    transitive_technique_name = (
        "(x (SUM GLOBAL) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))"
    )
    transitive_sampled_artifacts_technique_name = (
        "(~ (SUM GLOBAL %f) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))"
        % sample_percentage
    )
    transitive_sampled_traces_technique_name = (
        "($ (SUM GLOBAL %f) ((. (VSM NT) (0 1)) (. (VSM NT) (1 2))))"
        % sample_percentage
    )
    combined_technique_name = "(o (%s) (%s %s))" % (
        "SUM",
        direct_technique_name,
        transitive_technique_name,
    )
    combined_sampled_artifacts_technique_name = "(o (%s) (%s %s))" % (
        "SUM",
        direct_technique_name,
        transitive_sampled_artifacts_technique_name,
    )
    combined_sampled_traces_technique_name = "(o (%s) (%s %s))" % (
        "SUM",
        direct_technique_name,
        transitive_sampled_traces_technique_name,
    )

    def get_direct_definition(self) -> DirectTechniqueDefinition:
        return DirectTechniqueDefinition(self.direct_parameters, self.direct_components)

    def get_transitive_definition(self) -> TransitiveTechniqueDefinition:
        return TransitiveTechniqueDefinition(
            self.transitive_parameters, self.transitive_components
        )

    def get_traced_transitive_definition(self) -> TransitiveTechniqueDefinition:
        return TransitiveTechniqueDefinition(
            self.traced_parameters, self.traced_components
        )

    def get_combined_definition(self) -> CombinedTechniqueDefinition:
        return CombinedTechniqueDefinition(
            self.combined_parameters, self.combined_components
        )

    def get_sampled_technique_definition(self) -> SampledTechniqueDefinition:
        return SampledTechniqueDefinition(
            self.sampled_parameters, self.sampled_components
        )

    def get_combined_sampled_artifacts_definition(self) -> CombinedTechniqueDefinition:
        return CombinedTechniqueDefinition(
            self.combined_parameters, self.combined_sampled_artifacts_components
        )

    def assert_valid_fake_dataset_similarity_matrix(
        self, similarity_matrix: SimilarityMatrix
    ):
        self.assertEqual((1, 3), similarity_matrix.shape)

    def create_counter_func(self, t_name: str):
        n_function_calls = {"value": 0}

        def counter_func(data: TechniqueData):
            self.assertEqual(self.d_name, data.dataset.name)
            self.assertEqual(t_name, data.technique.get_name())
            n_function_calls["value"] = n_function_calls["value"] + 1

        return counter_func, n_function_calls
