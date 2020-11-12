import os
import pytest
import random
import shutil

from helpers import copy_sample_files, random_string
from iiif_pipeline.derivatives import create_jp2
from iiif_pipeline.helpers import matching_files


FIXTURES_FILEPATH = os.path.join("fixtures", "tif")
SOURCE_DIR = os.path.join("/", "source")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
UUIDS = [random_string() for x in range(random.randint(2, 3))]
PAGE_COUNT = random.randint(1, 5)


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
    uuid = random.choice(UUIDS)
    create_jp2(matching_files(SOURCE_DIR, prefix=uuid, skip=False, prepend=True), DERIVATIVE_DIR, uuid)
    assert len(os.listdir(DERIVATIVE_DIR)) == PAGE_COUNT
    for f in os.listdir(DERIVATIVE_DIR):
        assert ".tif" not in f


def test_replace_jp2():
    """Ensure replacing of files is handled correctly.

    If files exist and the replace parameter is False, a FileExistsError should
    be raised.
    """
    uuid = random.choice(UUIDS)
    create_jp2(matching_files(SOURCE_DIR, prefix=uuid, skip=False, prepend=True), DERIVATIVE_DIR, uuid)
    with pytest.raises(FileExistsError):
        create_jp2(matching_files(SOURCE_DIR, prefix=uuid, skip=False, prepend=True), DERIVATIVE_DIR, uuid)
    create_jp2(matching_files(SOURCE_DIR, prefix=uuid, skip=False, prepend=True), DERIVATIVE_DIR, uuid, replace=True)


def teardown():
    """Removes test directories."""
    for d in [SOURCE_DIR, DERIVATIVE_DIR]:
        shutil.rmtree(d)
