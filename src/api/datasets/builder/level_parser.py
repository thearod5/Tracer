import os

import pandas as pd

from api.datasets.builder.trace_creator import get_document_delimiter
from api.util.file_operations import get_non_empty_lines


def read_level_in_dataset(path_to_folder,
                          contains_ids_in_file=False,
                          drop_na=True):
    if os.path.isfile(path_to_folder):
        if ".txt" in path_to_folder:
            df = parse_level_txt(path_to_folder)
        elif ".csv" in path_to_folder:
            df = pd.read_csv(path_to_folder)
        else:
            raise ValueError("Could not identify file type: %s" % path_to_folder)
    else:

        assert os.path.isdir(path_to_folder), "Given path is not a directory: %s" % path_to_folder
        df = pd.DataFrame(columns=["id", "text"])
        files_in_folder = list(filter(lambda f: f[0] != ".", os.listdir(path_to_folder)))
        for file_name in files_in_folder:
            path_to_file = os.path.join(path_to_folder, file_name)

            try:
                with open(path_to_file) as file:
                    text = file.read()
            except:
                with open(path_to_file, encoding='ISO-8859-1') as file:
                    text = file.read()

            if contains_ids_in_file:
                # Remove any identifier information
                file_delimiter, delimiter_index = get_document_delimiter(text, return_index=True)
                text = text[delimiter_index:]

            # add to df
            item = {"id": file_name.strip(), "text": text.strip()}
            df = df.append(item, ignore_index=True)

    df["id"] = df["id"].astype(str)
    df["text"] = df["text"].astype(str)
    df = df.dropna()
    return df


def parse_level_txt(path_to_file: str):
    assert os.path.isfile(path_to_file), "File not found: %s" % path_to_file
    df = pd.DataFrame(columns=["id", "text"])
    with open(path_to_file) as level_file:
        level_contents = level_file.read()
        level_lines = get_non_empty_lines(level_contents)
        for line in level_lines:
            line_delimiter = get_document_delimiter(line)
            line_split = line.split(line_delimiter)
            a_id, a_body = line_split[0], line_delimiter.join(line_split[1:])
            df = df.append({"id": a_id.strip(), "text": a_body.strip()}, ignore_index=True)
    return df
