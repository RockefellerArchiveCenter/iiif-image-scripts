import os
import random
import shutil

from helpers import copy_sample_files, random_string
from iiif_pipeline.create_derivatives import DerivativeMaker


FIXTURES_FILEPATH = os.path.join("fixtures", "tif")
SOURCE_DIR = os.path.join("/", "source")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
UUIDS = [random_string() for x in range(random.randint(1,3))]
PAGE_COUNT = random.randint(1,5)

def setup():
    """Sets up source directory for tests."""
    for d in [SOURCE_DIR, DERIVATIVE_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(FIXTURES_FILEPATH, SOURCE_DIR)
    copy_sample_files(SOURCE_DIR, UUIDS, PAGE_COUNT, "tif")
    os.makedirs(DERIVATIVE_DIR)

def test_create_jp2():
    """Ensure the run method produces the expected number of files."""
    DerivativeMaker().create_jp2(SOURCE_DIR, DERIVATIVE_DIR, random.choice(UUIDS), None)
    assert len(os.listdir(DERIVATIVE_DIR)) == PAGE_COUNT

def teardown():
    """Removes test directories."""
    for d in [SOURCE_DIR, DERIVATIVE_DIR]:
        shutil.rmtree(d)
