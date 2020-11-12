import os
import random
import shutil

from helpers import copy_sample_files, random_string
from iiif_pipeline.helpers import matching_files
from iiif_pipeline.manifests import ManifestMaker

FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
MANIFEST_DIR = os.path.join("/", "manifests")
UUIDS = [random_string() for x in range(random.randint(1, 3))]
PAGE_COUNT = random.randint(1, 5)


def setup():
    """Sets up the derivative and manifest directories."""
    for d in [DERIVATIVE_DIR, MANIFEST_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(FIXTURE_FILEPATH, DERIVATIVE_DIR)
    copy_sample_files(DERIVATIVE_DIR, UUIDS, PAGE_COUNT, "jp2")
    os.makedirs(MANIFEST_DIR)


def test_create_manifest():
    """Ensures a correctly-named manifest is created."""
    uuid = random.choice(UUIDS)
    ManifestMaker("http://example.com", MANIFEST_DIR).create_manifest(
        matching_files(DERIVATIVE_DIR, prefix=uuid),
        DERIVATIVE_DIR, uuid,
        {"title": random_string(), "dates": random_string()})
    assert len(os.listdir(MANIFEST_DIR)) == 1
    assert os.path.isfile(os.path.join(MANIFEST_DIR, "{}.json".format(uuid)))


def teardown():
    """Removes the derivative and manifest directories."""
    for d in [DERIVATIVE_DIR, MANIFEST_DIR]:
        shutil.rmtree(d)
