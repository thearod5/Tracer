import os
import sys

import nose

PATH_TO_FILE = os.path.abspath(__file__)
PATH_TO_TESTS = os.path.join(os.path.abspath(os.path.dirname(PATH_TO_FILE)))
PATH_TO_SRC = os.path.normpath(os.path.join(PATH_TO_TESTS, ".."))
PATH_TO_API = os.path.join(PATH_TO_SRC, "api")
sys.path.append(PATH_TO_SRC)
sys.path.append(PATH_TO_API)

if __name__ == "__main__":
    result = nose.main()
