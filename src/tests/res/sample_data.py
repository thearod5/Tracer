import os

from api.constants.paths import PATH_TO_SOURCE_CODE


def get_test_java_class():
    path_to_file = os.path.join(PATH_TO_SOURCE_CODE, "Test.java")
    file = open(path_to_file, "r")
    file_content = file.read()
    file.close()
    return file_content


def get_entity_java_class():
    path_to_file = os.path.join(PATH_TO_SOURCE_CODE, "TestFolder", "Entity.java")
    file = open(path_to_file, "r")
    file_content = file.read()
    file.close()
    return file_content
