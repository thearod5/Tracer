from api.technique.variationpoints.aggregation.aggregation_method import AggregationMethod

arithmetic_aggregation_functions = {
    AggregationMethod.MAX: max,
    AggregationMethod.SUM: sum,
}
