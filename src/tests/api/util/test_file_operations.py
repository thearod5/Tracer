import os
from pathlib import Path

from api.constants.paths import PATH_TO_CACHE_TEMP
from api.util.file_operations import get_non_empty_lines, rename_with_timestamp, remove_folder, get_index_after_numbers, \
    get_index_after_number_with_extension, create_if_not_exist, list_to_string
from tests.res.smart_test import SmartTest


class TestFileOperations(SmartTest):
    """

    rename_with_timestamp
    """
    file_name = "TestFile"
    path_to_old = os.path.join(PATH_TO_CACHE_TEMP, ".old")

    def test_rename_with_timestamp_with_existing_file(self):
        remove_folder(self.path_to_old)

        # 1. Create
        path_to_file = os.path.join(PATH_TO_CACHE_TEMP, self.file_name + ".txt")
        Path(path_to_file).touch()  # existing file
        rename_with_timestamp(path_to_file)
        self.assertEqual(1, len(os.listdir(self.path_to_old)))
        self.assertFalse(os.path.isfile(path_to_file))
        self.assertTrue(any([self.file_name in file for file in os.listdir(self.path_to_old)]))

        #
        remove_folder(self.path_to_old)

    def test_rename_with_timestamp_without_file(self):
        remove_folder(self.path_to_old)

        # 1. Create
        path_to_file = os.path.join(PATH_TO_CACHE_TEMP, self.file_name + ".txt")
        result = rename_with_timestamp(path_to_file)
        self.assertIsNone(result)

    """
    test_get_non_empty_lines
    """

    def test_get_non_empty_lines(self):
        line = "abc def"
        content = "%s\n\n%s" % (line, line)
        lines = get_non_empty_lines(content)
        self.assertEqual(2, len(lines))
        self.assertEqual(line, lines[0])
        self.assertEqual(line, lines[1])

    def test_get_non_empty_lines_tab(self):
        line = "abc\tdef"
        lines = get_non_empty_lines(line, ["\t"])
        self.assertEqual(2, len(lines))
        self.assertEqual("abc", lines[0])
        self.assertEqual("def", lines[1])

    def test_get_non_empty_lines_with_extra_delimiters(self):
        line = "abc\tdef"
        lines = get_non_empty_lines(line, ["\t", " "])

        self.assertEqual(2, len(lines))
        self.assertEqual("abc", lines[0])
        self.assertEqual("def", lines[1])

    """
    get_index_after_numbers
    """

    def test_get_index_after_numbers(self):
        self.assertEqual(-1, get_index_after_numbers("hello"))

    """
    get_index_after_number_with_extension
    """

    def test_get_index_after_number_with_extension(self):
        self.assertEqual(7, get_index_after_number_with_extension("123.txt"))

    """
    create_if_not_exist
    """

    def test_create_if_not_exist(self):
        remove_folder(self.path_to_old)
        create_if_not_exist(self.path_to_old)
        self.assertTrue(os.path.isdir(self.path_to_old))
        remove_folder(self.path_to_old)

    """
    list_to_string
    """

    def test_list_to_string(self):
        self.assertEqual("(VSM SUM)", list_to_string(["VSM", "SUM"]))
