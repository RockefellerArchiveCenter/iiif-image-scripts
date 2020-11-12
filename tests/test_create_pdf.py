import os
import random
import shutil

import pytest
from helpers import copy_sample_files, random_string
from iiif_pipeline.derivatives import create_pdf
from iiif_pipeline.helpers import matching_files

FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
PDF_DIR = os.path.join("/", "pdfs")
UUIDS = [random_string() for x in range(random.randint(1, 3))]
PAGE_COUNT = random.randint(1, 5)


def setup():
    """Sets up derivative directory."""
    for d in [DERIVATIVE_DIR, PDF_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(FIXTURE_FILEPATH, DERIVATIVE_DIR)
    copy_sample_files(DERIVATIVE_DIR, UUIDS, PAGE_COUNT, "jp2")
    os.makedirs(PDF_DIR)


def test_create_pdf():
    """Ensure the run method produces the expected number of files."""
    identifier = random.choice(UUIDS)
    create_pdf(
        matching_files(
            DERIVATIVE_DIR,
            prefix=identifier,
            prepend=True),
        identifier,
        PDF_DIR)
    assert len(os.listdir(PDF_DIR)) == 1
    assert os.path.isfile(os.path.join(PDF_DIR, "{}.pdf".format(identifier)))


def test_replace_pdf():
    """Ensure replacing of files is handled correctly.

    If files exist and the replace parameter is False, a FileExistsError should
    be raised.
    """
    identifier = random.choice(UUIDS)
    create_pdf(
        matching_files(
            DERIVATIVE_DIR,
            prefix=identifier,
            prepend=True),
        identifier,
        PDF_DIR)
    with pytest.raises(FileExistsError):
        create_pdf(
            matching_files(
                DERIVATIVE_DIR,
                prefix=identifier,
                prepend=True),
            identifier,
            PDF_DIR)
    create_pdf(
        matching_files(
            DERIVATIVE_DIR,
            prefix=identifier,
            prepend=True),
        identifier,
        PDF_DIR,
        replace=True)


def teardown():
    """Remove derivative directory."""
    shutil.rmtree(DERIVATIVE_DIR)
