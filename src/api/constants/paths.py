"""
This file is the container for constants related to documenting the folder
structure of this project.
"""

import os
from pathlib import Path  # Python 3.6+ only

from dotenv import load_dotenv

ENV_PATH = os.path.join(Path(__file__).parent.absolute(), "..", "..", "..", ".env")
assert os.path.isfile(ENV_PATH), "Make sure .env file is configured"
load_dotenv(dotenv_path=ENV_PATH)
PATH_TO_ROOT = os.environ.get("PATH_TO_ROOT")

NOTRACES_ID = "notraces"
WITHTRACES_ID = "withtraces"
TECHNIQUES_ID = "techniques"

PATH_TO_RESOURCES = os.path.join(PATH_TO_ROOT, "res")

# Roots
PATH_TO_DATA = os.path.join(PATH_TO_ROOT, "Data")
# TODO: separate this into a TEST_DATASETS and read this from .env file
PATH_TO_DATASETS = os.path.join(PATH_TO_RESOURCES, "datasets")
PATH_TO_DATA_SOURCE = os.path.join(PATH_TO_DATA, "source")
PATH_TO_DATA_PROCESSED = os.path.join(PATH_TO_DATA, "processed")
PATH_TO_DATA_INTERMEDIARY = os.path.join(PATH_TO_DATA, "intermediary")

# SOURCE
PATH_TO_TECHNIQUE_SOURCE_DATA = os.path.join(PATH_TO_DATA_SOURCE, TECHNIQUES_ID)
PATH_TO_SAMPLING_SOURCE = os.path.join(PATH_TO_DATA_SOURCE, "sampling")

# INTERMEDIARY
PATH_TO_GAIN_INTERMEDIARY = os.path.join(PATH_TO_DATA_INTERMEDIARY, "gain")
PATH_TO_BEST_INTERMEDIARY = os.path.join(PATH_TO_DATA_INTERMEDIARY, "best")
PATH_TO_SAMPLING_INTERMEDIARY = os.path.join(PATH_TO_DATA_INTERMEDIARY, "sampling")
PATH_TO_TECHNIQUES_INTERMEDIARY = os.path.join(PATH_TO_DATA_INTERMEDIARY, TECHNIQUES_ID)
PATH_TO_CORRELATION_INTERMEDIARY = os.path.join(PATH_TO_DATA_INTERMEDIARY, "correlation")

PATH_TO_NOTRACES_INTERMEDIARY = os.path.join(PATH_TO_TECHNIQUES_INTERMEDIARY, NOTRACES_ID)
PATH_TO_WITHTRACES_INTERMEDIARY = os.path.join(PATH_TO_TECHNIQUES_INTERMEDIARY, WITHTRACES_ID)

# PROCESSED
PATH_TO_BEST_PROCESSED = os.path.join(PATH_TO_DATA_PROCESSED, "best")
PATH_TO_DATASET_SIZES_DATA = os.path.join(PATH_TO_DATA_PROCESSED, "datasetsizes")
PATH_TO_GAIN_PROCESSED = os.path.join(PATH_TO_DATA_PROCESSED, "gain")
PATH_TO_SAMPLING_PROCESSED = os.path.join(PATH_TO_DATA_PROCESSED, "sampling")
PATH_TO_CORRELATION_PROCESSED = os.path.join(PATH_TO_DATA_PROCESSED, "correlation")

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
