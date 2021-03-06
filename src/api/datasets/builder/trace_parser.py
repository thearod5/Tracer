"""
Responsible for parsing trace links in user-defined datasets.
"""
import os
from typing import List, Tuple

import numpy as np
import pandas as pd

from api.extension.file_operations import (
    get_index_after_number_with_extension,
    get_non_empty_lines,
)
from api.technique.variationpoints.algebraicmodel.models import SimilarityMatrix

TraceLink = Tuple[str, str]
TraceLinks = List[TraceLink]
TRACE_LINK_DELIMITERS = [" ", "\t", ":"]


def parse_trace_file(path_to_trace_file: str) -> TraceLinks:
    """
    Reads file at path and parses trace links for each line in the file.
    Returns list of trace links.
    :param path_to_trace_file: path to trace link definition file
    :return: list of trace links found in file
    """
    assert os.path.isfile(path_to_trace_file), path_to_trace_file

    with open(path_to_trace_file) as trace_file:
        trace_file_contents = trace_file.read()
        traces = get_traces_in_trace_link_definitions(trace_file_contents)
    return traces


def get_traces_in_trace_link_definitions(
    trace_link_definitions: str,
) -> TraceLinks:
    """
    Returns list of trace links found in trace link definition file.
    :param trace_link_definitions: a string defining a list of trace links between source and target arifacts.
    :return: list of tuples in the form ([source artifact], [target artifact])
    """
    file_lines = get_non_empty_lines(trace_link_definitions)
    traces: TraceLinks = []
    for trace_line in file_lines:
        traces = traces + get_trace_links_string(trace_line)
    return traces


def get_trace_links_string(trace_line) -> List[Tuple[str, str]]:
    """
    Given a line a in trace definition file returns list of tuples in the form ([source artifact], [target artifact])
    :param trace_line: string containing a source artifact and zero or many target artifacts
    :return: list of trace links
    """
    trace_links: TraceLinks = []
    identifiers = get_non_empty_lines(trace_line, TRACE_LINK_DELIMITERS)

    if len(identifiers) < 2:
        return []

    source_id = identifiers[0]
    for target_id in identifiers[1:]:
        trace_links.append((source_id, target_id))
    return trace_links


def is_valid_trace_list(trace_list):
    """
    TODO
    :param trace_list:
    :return:
    """
    if not isinstance(trace_list, list):
        return False

    for trace in trace_list:
        if isinstance(trace, str):
            return False
        if len(trace) != 2:
            return False
    return True


def create_matrix_with_values(values, row_labels, column_labels):
    """
    TODO
    :param values:
    :param row_labels:
    :param column_labels:
    :return:
    """
    trace_matrix = pd.DataFrame(values)
    trace_matrix.columns = column_labels
    trace_matrix["id"] = row_labels
    return trace_matrix


def create_trace_matrix_values_from_trace_list(
    top_artifacts_ids: [str], bottom_artifact_ids: [str], trace_list: [(str, str)]
) -> SimilarityMatrix:
    """
    Creates a DataFrame with CACHE_COLUMNS as bottom ids and id col containing top ids
    TODO
    :param top_artifacts_ids:
    :param bottom_artifact_ids:
    :param trace_list:
    :return:
    """
    assert is_valid_trace_list(trace_list), "Received invalid trace list"

    shape = (len(top_artifacts_ids), len(bottom_artifact_ids))
    trace_matrix = create_matrix_with_values(
        np.zeros(shape=shape), top_artifacts_ids, bottom_artifact_ids
    )
    trace_matrix = trace_matrix.set_index("id")
    for trace in trace_list:
        source, target = trace
        if source in list(trace_matrix.index):
            trace_matrix.loc[source][target] = 1
        elif target in list(trace_matrix.index):
            trace_matrix.loc[target][source] = 1
    return trace_matrix.values


def get_document_delimiter(
    trace_file_content: str, return_none_on_fail=False, return_index=False
):
    """
    TODO
    :param trace_file_content:
    :param return_none_on_fail:
    :param return_index:
    :return:
    """
    assert isinstance(trace_file_content, str)

    file_lines = get_non_empty_lines(trace_file_content)
    assert file_lines[0] != ""
    first_line = file_lines[0]
    start_index = get_index_after_number_with_extension(first_line)
    index_on_next_item = get_index_of_next_alpha_char(first_line, start_index)

    if index_on_next_item == -1:
        if return_none_on_fail:
            return None
        raise Exception("Could not find the next alpha char in: %s:" % first_line)

    segment = first_line[start_index:index_on_next_item]
    delimiter = get_delimiter_in_segment(segment)
    if return_index:
        return delimiter, start_index + segment.index(delimiter)
    return delimiter


def get_delimiter_in_segment(segment: str, high_precedence=None, low_precedence=None):
    """
    Searches segment for highest precedence delimiters.
    :param low_precedence: delimiters with low precedence (default is space)
    :param high_precedence: delimiters which if found return immediately
    :param segment: the string to search
    :return: char representing the delimiter
    """

    if high_precedence is None:
        high_precedence = ["-", ":"]

    if low_precedence is None:
        low_precedence = [" ", "\t"]

    current_delimiter = None

    for char in segment:
        if char in high_precedence:
            return char
        if char in low_precedence:
            current_delimiter = char
    if current_delimiter is None:
        raise Exception("No delimiters in %s" % segment)

    return current_delimiter


def get_index_of_next_alpha_char(string: str, start_index=0) -> int:
    """
    TODO
    :param string:
    :param start_index:
    :return:
    """
    forbidden = [" ", "-"]
    for char_index, char in enumerate(string[start_index:]):
        if str.isalnum(char) and char not in forbidden:
            return start_index + char_index
    return -1
