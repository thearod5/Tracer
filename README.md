# About
The following library is a tracing engine originally developed alongside my thesis paper
Leveraging Intermediate Artifacts to improve Trace Link Retrieval. In this paper we discuss a set of techniques that 
retrieve trace links either by directly comparing source and target artifacts, transitively comparing the source artifact
to all intermediate artifacts, or a hybrid which combines both direct and transitive techniques.

# Installation
I have included a script `install.sh` that will:

* Install the python virtual environment and all its dependencies
* Create .env file containing the absolute path of the engine.
* Create `cache` folder used to be able to cache techniques.

# Documentation
API function documentation can be found here: https://traceabilitytracer.readthedocs.io/en/latest/

# Usage
There is a proxy class for common tracing operations under `api.tracer.Tracer`

```
from api.tables.metric_table import MetricTable
from api.tracer import Tracer

dataset_name = "EasyClinic"
direct_technique = "(. (LSI NT) (0 2))"
transitive_technique = "(x (PCA GLOBAL) ((. (LSI NT) (0 1)) (. (LSI NT) (1 2))))"
hybrid_technique = f"(o (MAX) ({direct_technique} {transitive_technique}))"

technique_definitions = [
    ("direct", direct_technique),
    ("transitive", transitive_technique),
    ("hybrid", hybrid_technique),
]

metric_table = MetricTable()
tracer = Tracer()

for t_name, t_def in technique_definitions:
    t_metrics = tracer.get_metrics(dataset_name, t_def)
    metric_table.add(t_metrics, {"name": t_name})

print(metric_table.table)
```

```
   query_id       map       auc         lag        name
0         0  0.686343  0.749641  259.621984      direct
1         0  0.432479  0.645247  367.879357  transitive
2         0  0.698789  0.786151  221.761394      hybrid
```

We notice that these metrics are summary metrics because the entire set of trace links
is treated as a single query.


## Language Definition
To define technique we use a lisp-like language parser where techniques
take the following form:

([technique_symbol] ([variants...]) ([components...]))
### Direct Techniques
Symbol: `.` <br>
Variants: [AlgebraicModel, TraceType]<br>
Components: [Source Artifact Level, Target Artifact Level]
### Transitive Techniques
Symbol: `x` <br>
Variants: [PathAggregationMethod, ScalingMethod]<br>
Components: [UpperTechnique, LowerTechnique]
### Hybrid Techniques
Symbol: `o` <br>
Variants: [TechniqueAggregationMethod]<br>
Components: [ComponentTechniques...]

# How to Contribute
All supporting developers are expected to use the pull request system
which performs linting, unit tests, and test coverage checks before allowing
potential merges. These checks can be run locally with:

`make checklist`