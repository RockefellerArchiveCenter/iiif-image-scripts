import os
import shutil
import random

from iiif_pipeline.helpers import cleanup_files, matching_files, refid_dirs
from helpers import copy_sample_files, random_string


FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")
SOURCE_DIR = os.path.join("/", "source")
UUIDS = [random_string() for x in range(random.randint(1, 3))]
PAGE_COUNT = random.randint(1, 5)


def setup():
    """Sets up a source directory."""
    if os.path.isdir(SOURCE_DIR):
        shutil.rmtree(SOURCE_DIR)
    shutil.copytree(FIXTURE_FILEPATH, SOURCE_DIR)
    copy_sample_files(SOURCE_DIR, UUIDS, PAGE_COUNT, "tif", to_master=True)


def test_matching_files():
    """Ensure the correct number of matching files are returned."""
    matching = matching_files(FIXTURE_FILEPATH)
    assert len(matching) == 1
    matching = matching_files(FIXTURE_FILEPATH, prefix="sample")
    assert len(matching) == 1
    matching = matching_files(FIXTURE_FILEPATH, prefix="foo")
    assert len(matching) == 0
    matching = matching_files(FIXTURE_FILEPATH, prefix="sample", skip=True)
    assert len(matching) == 1
    matching = matching_files(FIXTURE_FILEPATH, prepend=True)
    assert matching[0].startswith(FIXTURE_FILEPATH)


def test_refid_dirs():
    """Ensure the correct number of directories are returned."""
    print(os.listdir(SOURCE_DIR))
    dirs = refid_dirs(SOURCE_DIR)
    assert len(dirs) == len(UUIDS)


def test_cleanup_files():
    """Ensure files are deleted as expected."""
    assert len(os.listdir(SOURCE_DIR)) > 0
    for uuid in UUIDS:
        cleanup_files(uuid, [os.path.join(SOURCE_DIR, uuid, "master")])
        assert len(os.listdir(os.path.join(SOURCE_DIR, uuid, "master"))) == 0


def teardown():
    shutil.rmtree(SOURCE_DIR)
