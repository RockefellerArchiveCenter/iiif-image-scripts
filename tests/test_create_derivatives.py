import os
import random
import shutil

from helpers import random_string
from iiif_pipeline.create_derivatives import DerivativeMaker


FIXTURES_FILEPATH = os.path.join("fixtures", "tif")
SOURCE_DIR = os.path.join("/", "source")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
UUIDS = [random_string() for x in range(random.randint(1,3))]
PAGE_COUNT = 4

def setup():
    for d in [SOURCE_DIR, DERIVATIVE_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(FIXTURES_FILEPATH, SOURCE_DIR)
    for f in os.listdir(SOURCE_DIR):
        for uuid in UUIDS:
            for page in range(PAGE_COUNT):
                shutil.copyfile(os.path.join(SOURCE_DIR, f), os.path.join(SOURCE_DIR, "{}_{}.tif".format(uuid, page)))
        os.remove(os.path.join(SOURCE_DIR, f))
    os.makedirs(DERIVATIVE_DIR)

def test_run():
    DerivativeMaker().run(SOURCE_DIR, DERIVATIVE_DIR, random.choice(UUIDS), None)
    assert len(os.listdir(DERIVATIVE_DIR)) == PAGE_COUNT
