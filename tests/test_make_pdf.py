import os
import random
import shutil

from helpers import copy_sample_files, random_string
from iiif_pipeline.make_pdf import PDFMaker

FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
UUIDS = [random_string() for x in range(random.randint(1,3))]
PAGE_COUNT = random.randint(1,5)

def setup():
    """Sets up derivative directory."""
    if os.path.isdir(DERIVATIVE_DIR):
        shutil.rmtree(DERIVATIVE_DIR)
    shutil.copytree(FIXTURE_FILEPATH, DERIVATIVE_DIR)
    copy_sample_files(DERIVATIVE_DIR, UUIDS, PAGE_COUNT, "jp2")

def test_make_pdf():
    """Ensure the run method produces the expected number of files."""
    initial_length = len(os.listdir(DERIVATIVE_DIR))
    PDFMaker().make_pdf(DERIVATIVE_DIR)
    assert len(os.listdir(DERIVATIVE_DIR)) == initial_length + len(UUIDS)
    for uuid in UUIDS:
        assert os.path.isfile(os.path.join(DERIVATIVE_DIR, "{}.pdf".format(uuid)))

def teardown():
    """Remove derivative directory."""
    shutil.rmtree(DERIVATIVE_DIR)
