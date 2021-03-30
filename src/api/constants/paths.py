"""
This file is the container for constants related to documenting the folder
structure of this project.
"""

import os
from pathlib import Path  # Python 3.6+ only

from dotenv import load_dotenv

from api.extension.type_checks import to_string

ENV_PATH = os.path.join(Path(__file__).parent.absolute(), "..", "..", "..", ".env")
assert os.path.isfile(ENV_PATH), "Make sure .env file is configured"
load_dotenv(dotenv_path=ENV_PATH)

PATH_TO_ROOT = os.environ.get("PATH_TO_ROOT")
PATH_TO_DATASETS = os.environ.get("PATH_TO_DATASETS")

NOTRACES_ID = "notraces"
WITHTRACES_ID = "withtraces"
TECHNIQUES_ID = "techniques"

PATH_TO_RESOURCES = os.path.join(to_string(PATH_TO_ROOT), "res")

# Roots
PATH_TO_SAMPLE_DATASETS = os.path.join(PATH_TO_RESOURCES, "datasets")

# Tracer
PATH_TO_TRACER_SRC = os.path.join(PATH_TO_ROOT, "src")

# Graphs
PATH_TO_GRAPHS = os.path.join(PATH_TO_ROOT, "Graphs")
PATH_TO_MINIMAL_GRAPHS = os.path.join(PATH_TO_GRAPHS, "Minimal")
PATH_TO_ORIGINAL_GRAPHS = os.path.join(PATH_TO_GRAPHS, "Original")

# res

PATH_TO_STOP_WORDS = os.path.join(PATH_TO_RESOURCES, "Stopwords.txt")
PATH_TO_TEST_REQUIREMENTS = os.path.join(PATH_TO_RESOURCES, "requirements.txt")
PATH_TO_RESERVED_WORDS = os.path.join(PATH_TO_RESOURCES, "JavaReservedKeywords.txt")
PATH_TO_SOURCE_CODE = os.path.join(PATH_TO_RESOURCES, "SourceCode")

# Cache
PATH_TO_CACHE_TEMP = os.path.join(PATH_TO_ROOT, "cache")

# SEProject
PATH_TO_SE_PROJECTS = os.path.join(PATH_TO_ROOT, ".old", "SEProjects")
