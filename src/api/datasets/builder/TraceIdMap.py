"""
The following module is responsible for providing an class that allows users to:

1. Store an object whose key is a trace id
2. Lookup an object or its transpose with a single trace id
3. Get list of trace ids
"""
from typing import Dict, Generic, List, TypeVar

from api.datasets.builder.ITranspose import Transposable
from api.extension.type_checks import to_string

MapValueType = TypeVar("MapValueType", bound=Transposable)
TraceIdDict = Dict[str, MapValueType]


class TraceIdMap(Generic[MapValueType]):
    """
    Implements a hash table for objects whose keys are trace ids.
    """

    def __init__(self):
        self.trace_map: TraceIdDict = {}

    def get_keys(self) -> List[str]:
        return list(map(to_string, self.trace_map.keys()))

    def update(self, new_map: "TraceIdMap[MapValueType]"):
        self.trace_map.update(new_map)

    def __getitem__(self, trace_id: str) -> MapValueType:
        if trace_id in self.trace_map:
            return self.trace_map[trace_id]
        r_id = TraceIdMap.reverse_id(trace_id)
        if TraceIdMap.reverse_id(trace_id) in self.trace_map:
            return self.trace_map[r_id].transpose()
        raise ValueError(
            "%s key not found in [%s]" % (trace_id, ",".join(self.get_keys()))
        )

    def __setitem__(self, trace_id: str, new_item: MapValueType):
        a_index, b_index = TraceIdMap.parse_trace_id(trace_id)
        if a_index > b_index:
            self.trace_map[TraceIdMap.reverse_id(trace_id)] = new_item.transpose()
        else:
            self.trace_map[trace_id] = new_item

    def __contains__(self, trace_id: str):
        return (
            trace_id in self.trace_map
            or TraceIdMap.reverse_id(trace_id) in self.trace_map
        )

    def __iter__(self):
        for trace_id, object in self.trace_map.items():
            yield trace_id, object

    @staticmethod
    def reverse_id(trace_id: str):
        """
        Parses given trace id and swaps source and target artifact level indices.
        :param trace_id: the original trace id composed by [source_level_index]-[target_level_index]
        :return: str representing [target_level_index]-[source_level_index]
        """
        upper_level, lower_level = trace_id.split("-")
        return "%s-%s" % (lower_level, upper_level)

    @staticmethod
    def parse_trace_id(trace_id: str):
        """
        TODO
        :param trace_id:
        :return:
        """
        upper_level, lower_level = trace_id.split("-")
        return int(upper_level), int(lower_level)
