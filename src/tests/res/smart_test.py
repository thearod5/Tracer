import inspect
import unittest

run_long_tests = False


class SmartTest(unittest.TestCase):
    """
    implements a generic runTest that subclasses use to run all tests
    """

    def runTest(self):
        tests_names = [key for key, _ in inspect.getmembers(self) if "test_" in key]
        for test_name in tests_names:
            if "_long" == test_name[-5:]:
                if run_long_tests:
                    getattr(self, test_name)()
            else:
                getattr(self, test_name)()
