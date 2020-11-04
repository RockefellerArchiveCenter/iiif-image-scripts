import os
import random
import shutil

from helpers import random_string
from iiif_pipeline.create_manifest import ManifestMaker


FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
MANIFEST_DIR = os.path.join("/", "manifests")
UUIDS = [random_string() for x in range(random.randint(1,3))]
PAGE_COUNT = random.randint(1,5)

def setup():
    """Sets up the derivative and manifest directories."""
    for d in [DERIVATIVE_DIR, MANIFEST_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(FIXTURE_FILEPATH, DERIVATIVE_DIR)
    for f in os.listdir(DERIVATIVE_DIR):
        for uuid in UUIDS:
            for page in range(PAGE_COUNT):
                shutil.copyfile(
                    os.path.join(DERIVATIVE_DIR, f),
                    os.path.join(DERIVATIVE_DIR, "{}_{}.jp2".format(uuid, page)))
        os.remove(os.path.join(DERIVATIVE_DIR, f))
    os.makedirs(MANIFEST_DIR)

def test_run():
    """Ensures a correctly-named manifest is created."""
    uuid = random.choice(UUIDS)
    ManifestMaker().run(DERIVATIVE_DIR, MANIFEST_DIR, uuid, random_string(), random_string())
    assert len(os.listdir(MANIFEST_DIR)) == 1
    assert os.path.isfile(os.path.join(MANIFEST_DIR, "{}.json".format(uuid)))

def teardown():
    """Removes the derivative and manifest directories."""
    for d in [DERIVATIVE_DIR, MANIFEST_DIR]:
        shutil.rmtree(d)
