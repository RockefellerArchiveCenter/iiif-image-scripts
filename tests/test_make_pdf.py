import os
import random
import shutil

from helpers import random_string
from iiif_pipeline.make_pdf import PDFMaker

FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
UUIDS = [random_string() for x in range(random.randint(1,3))]
PAGE_COUNT = random.randint(1,5)

def setup():
    if os.path.isdir(DERIVATIVE_DIR):
        shutil.rmtree(DERIVATIVE_DIR)
    shutil.copytree(FIXTURE_FILEPATH, DERIVATIVE_DIR)
    for f in os.listdir(DERIVATIVE_DIR):
        print(f)
        for uuid in UUIDS:
            for page in range(PAGE_COUNT):
                shutil.copyfile(
                    os.path.join(DERIVATIVE_DIR, f),
                    os.path.join(DERIVATIVE_DIR, "{}_{}.jp2".format(uuid, page)))
        os.remove(os.path.join(DERIVATIVE_DIR, f))

def test_run():
    initial_length = len(os.listdir(DERIVATIVE_DIR))
    PDFMaker().run(DERIVATIVE_DIR)
    assert len(os.listdir(DERIVATIVE_DIR)) == initial_length + len(UUIDS)
    for uuid in UUIDS:
        assert os.path.isfile(os.path.join(DERIVATIVE_DIR, "{}.pdf".format(uuid)))
