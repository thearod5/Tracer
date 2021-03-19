import os

import pandas as pd

from api.datasets.parsing.java_class_parser import create_class_doc


def parse_source_code(path_to_source_code):
    file_paths = list(get_relative_path_to_files_from(path_to_source_code))
    ids = []
    contents = []

    for relative_file_path in file_paths:
        path_to_source_file = os.path.join(path_to_source_code, relative_file_path)
        source_file = open(path_to_source_file, encoding="ISO-8859-1", mode="r")

        # Attempt to open the source code file
        source_content = source_file.read()
        source_file.close()

        try:
            source_code_identifiers_doc = create_class_doc(source_content)
            assert source_code_identifiers_doc is not None, "Received None for identifiers of source code: %s" % \
                                                            path_to_source_file
            if len(source_code_identifiers_doc) > 0:
                contents.append(source_code_identifiers_doc)
                ids.append(relative_file_path)
            else:
                print("%s had no identifiers." % path_to_source_file)
        except Exception as e:
            if "not enough identifiers" in repr(e).lower():
                continue
            raise e

    # Export
    result = pd.DataFrame()
    result["id"] = ids
    result["text"] = contents
    return result


def get_relative_path_to_files_from(root_dir):
    """
    Returns list of relative paths to files contained in given dir.
    :param root_dir: the path of the container to search
    :return: list of relative paths representing subfiles' locations from root_dir
    """
    file_set = set()

    for full_path, subdirs, files in os.walk(root_dir):
        for file_name in files:
            if file_name[0] == ".":
                continue
            file_path = os.path.join(full_path, file_name)
            rel_file = file_path.split(root_dir)[1][1:]
            file_set.add(rel_file)  # ids in oracle start from sourceCode

    return list(file_set)
