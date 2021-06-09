import os
import random
import shutil

from helpers import copy_sample_files, random_string
from iiif_pipeline.helpers import (cleanup_files, get_page_number,
                                   matching_files, refid_dirs)

FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")
MATCHING_FIXTURE_FILEPATH = os.path.join("fixtures", "matching")
MATCHING_SOURCE_DIR = os.path.join("/", "matching")
SOURCE_DIR = os.path.join("/", "source")
UUIDS = [random_string() for x in range(random.randint(1, 3))]
PAGE_COUNT = random.randint(1, 5)


def setup():
    """Sets up a source directory."""
    for d in [SOURCE_DIR, MATCHING_SOURCE_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(FIXTURE_FILEPATH, SOURCE_DIR)
    copy_sample_files(SOURCE_DIR, UUIDS, PAGE_COUNT, "tif", to_master=True)
    shutil.copytree(MATCHING_FIXTURE_FILEPATH, MATCHING_SOURCE_DIR)


def test_matching_files():
    """Ensure the correct number of matching files are returned."""
    matching = matching_files(MATCHING_SOURCE_DIR)
    assert len(matching) == 4
    matching = matching_files(MATCHING_SOURCE_DIR, prefix="sample")
    assert len(matching) == 2
    matching = matching_files(MATCHING_SOURCE_DIR, prefix="foo")
    assert len(matching) == 0
    matching = matching_files(MATCHING_SOURCE_DIR, prefix="sample", skip=True)
    assert len(matching) == 2
    matching = matching_files(MATCHING_SOURCE_DIR, suffix=".jp2")
    assert len(matching) == 1
    matching = matching_files(MATCHING_SOURCE_DIR, suffix=".tif")
    assert len(matching) == 1
    matching = matching_files(MATCHING_SOURCE_DIR, suffix=".pdf")
    assert len(matching) == 0
    matching = matching_files(MATCHING_SOURCE_DIR, prepend=True)
    assert matching[0].startswith(MATCHING_SOURCE_DIR)


def test_refid_dirs():
    """Ensure the correct number of directories are returned."""
    dirs = refid_dirs(SOURCE_DIR)
    assert len(dirs) == len(UUIDS)


def test_cleanup_files():
    """Ensure files are deleted as expected."""
    assert len(os.listdir(SOURCE_DIR)) > 0
    for uuid in UUIDS:
        cleanup_files(uuid, [os.path.join(SOURCE_DIR, uuid, "master")])
        assert len(os.listdir(os.path.join(SOURCE_DIR, uuid, "master"))) == 0


def test_get_page_number():
    """Ensure page numbers are correctly parsed."""
    for filepath, page_number in [
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/00336.tif", "00336"),
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/foo_00336.tif", "00336"),
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/00336_se.tif", "00336"),
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/00336_me.tif", "00336"),
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/00336_se-12345.tif", "00336"),
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/00336_me-12345.tif", "00336"),
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/foo_00336_se-12345.tif", "00336"),
            ("/source_files/73ebb410267f43af884fd158d0427f8f/master/foo_00336_me-12345.tif", "00336")]:
        assert get_page_number(filepath) == page_number


def teardown():
    shutil.rmtree(SOURCE_DIR)
