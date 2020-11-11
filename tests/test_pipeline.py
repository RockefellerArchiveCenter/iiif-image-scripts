import os
import random
import shutil
from unittest.mock import patch

from iiif_pipeline.pipeline import IIIFPipeline
from helpers import archivesspace_vcr, copy_sample_files, random_string

SOURCE_DIR = os.path.join("/", "source")
FIXTURES_FILEPATH = os.path.join("fixtures", "tif")
UUIDS = [random_string() for x in range(random.randint(1, 3))]
PAGE_COUNT = random.randint(1, 5)

def setup():
    if os.path.isdir(SOURCE_DIR):
        shutil.rmtree(SOURCE_DIR)
    shutil.copytree(FIXTURES_FILEPATH, SOURCE_DIR)
    copy_sample_files(SOURCE_DIR, UUIDS, PAGE_COUNT, "tif", to_master=True)


@patch("iiif_pipeline.clients.AWSClient.upload_files")
def test_main(mock_aws_client):
    expected_derivatives = len(UUIDS) * PAGE_COUNT
    with archivesspace_vcr.use_cassette("get_ao.json"):
        IIIFPipeline().run(SOURCE_DIR, False)
        for subpath in ["images", "pdfs", "manifests"]:
            assert os.path.isdir(os.path.join(SOURCE_DIR, subpath))
        assert len(os.listdir(os.path.join(SOURCE_DIR, "images"))) == expected_derivatives
        for subpath in ["pdfs", "manifests"]:
            assert len(os.listdir(os.path.join(SOURCE_DIR, subpath))) == len(UUIDS)


def teardown():
    shutil.rmtree(SOURCE_DIR)
