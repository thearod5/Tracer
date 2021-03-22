import os

from api.constants.paths import PATH_TO_ROOT, PATH_TO_SOURCE_CODE
from api.datasets.parsing.source_code_parser import (
    get_relative_path_to_files_from,
    parse_source_code,
)
from tests.res.smart_test import SmartTest


class TestSourceCodeParser(SmartTest):
    dataset = "derby"
    path_to_source_code = os.path.join(
        PATH_TO_ROOT, "SEProjects", dataset, "sourceCode"
    )

    def test_relative_file_path_file_types(self):
        source_code_paths = get_relative_path_to_files_from(self.path_to_source_code)
        valid_extensions = ["java"]
        for sc_path in source_code_paths:
            file_name = sc_path.split("/")[-1]
            extension = file_name.split(".")[-1]
            self.assertNotEqual(".", file_name[0], "Found system file in output")
            self.assertTrue(
                extension in valid_extensions, "invalid extension: %s" % extension
            )
            self.assertTrue(
                os.path.isfile("/".join([self.path_to_source_code, sc_path]))
            )

    def test_relative_file_path_on_sample_data(self):
        resulting_file_paths = get_relative_path_to_files_from(PATH_TO_SOURCE_CODE)
        expected_files = ["TestFolder/Entity.java", "Test.java"]
        self.assertEqual(len(resulting_file_paths), len(expected_files))
        for file_path in expected_files:
            self.assertTrue(
                file_path in resulting_file_paths,
                "Expected to find %s in file graph_paths." % file_path,
            )

    def test_parse_source_code(self):
        self.assertTrue(
            os.path.isdir(PATH_TO_SOURCE_CODE), "source code path is broken"
        )
        level_3 = parse_source_code(PATH_TO_SOURCE_CODE)

        self.assertEqual(2, len(level_3))
        expected_ids = ["TestFolder/Entity.java", "Test.java"]
        for expected_id in expected_ids:
            self.assertTrue(
                expected_id in list(level_3["id"]), "Could not find: %s" % expected_id
            )
