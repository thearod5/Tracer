import ntpath
import os

import re
import shutil


def rename_with_timestamp(path_to_file: str, file_name_delimiter="_", old_run_folder=".old"):
    if not os.path.isfile(path_to_file):
        return

    # Extract original information
    original_folder_container = "/".join(os.path.split(path_to_file)[:-1])  # TODO: Replace with generic function
    original_file_name, file_extension = ntpath.basename(path_to_file).split(".")

    # Create dir for old runs
    path_to_old_run_folder = os.path.join(original_folder_container, old_run_folder)
    if not os.path.isdir(path_to_old_run_folder):
        os.mkdir(path_to_old_run_folder)

    # Create new file path
    time_created = os.path.getmtime(path_to_file)
    new_file_name = file_name_delimiter.join([original_file_name, repr(time_created) + "." + file_extension])
    new_path_to_file = os.path.join(path_to_old_run_folder, new_file_name)

    os.rename(path_to_file, new_path_to_file)


def remove_folder(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)


def get_non_empty_lines(file_content: str, delimiters=["\n"]):
    lines = re.split("|".join(delimiters), file_content)
    return list(filter(lambda line: len(line) > 1, lines))


def get_index_after_number_with_extension(line: str):
    stop_at = [" ", ":", "-", "\t"]
    index = get_index_after_numbers(line)
    if line[index] == ".":
        for new_index in range(index, len(line)):
            if line[new_index] in stop_at:
                return new_index
        return len(line)
    else:
        return index


def get_index_after_numbers(line):
    for index, char in enumerate(line[:-1]):
        if char.isnumeric() and not line[index + 1].isnumeric():
            return index + 1
    return -1


def create_if_not_exist(path_to_folder):
    folder_exists = os.path.isdir(path_to_folder)
    if not folder_exists:
        os.mkdir(path_to_folder)


def list_to_string(lst: [str]) -> str:
    result = ""
    for elem in lst:

        if isinstance(elem, list):
            elem_str = list_to_string((elem))
        elif isinstance(elem, str):
            elem_str = elem
        else:
            elem_str = repr(elem)
        result = "%s %s" % (result, elem_str)
    return "(%s)" % result.strip()
