import os
import random
import shutil
from unittest.mock import patch

from helpers import archivesspace_vcr, copy_sample_files, random_string
from iiif_pipeline.pipeline import IIIFPipeline

SOURCE_DIR = os.path.join("/", "source")
TARGET_DIR = os.path.join("/", "target")
FIXTURES_FILEPATH = os.path.join("fixtures", "tif")
UUIDS = [random_string() for x in range(random.randint(2, 3))]
PAGE_COUNT = random.randint(1, 5)


def setup():
    for d in [SOURCE_DIR, TARGET_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(FIXTURES_FILEPATH, SOURCE_DIR)
    copy_sample_files(SOURCE_DIR, UUIDS, PAGE_COUNT, "tif", to_master=True)


@patch("iiif_pipeline.clients.ArchivesSpaceClient.get_object")
@patch("iiif_pipeline.clients.AWSClient.upload_files")
def test_pipeline(mock_aws_client, mock_get_object):
    """Ensures that target directories are empty after successful run.

    Mock.side_effect is used so that the random_string returned in the URI is
    unique each time the mock is called.
    """
    mock_get_object.side_effect = [
        {"title": random_string(), "dates": "1945-1950", "uri": random_string()},
        {"title": random_string(), "dates": "1950-1951", "uri": random_string()},
        {"title": random_string(), "dates": "1945-1973", "uri": random_string()}]
    with archivesspace_vcr.use_cassette("get_ao.json"):
        IIIFPipeline().run(SOURCE_DIR, TARGET_DIR, False, False, True)
        for subpath in ["images", "pdfs", "manifests"]:
            assert os.path.isdir(os.path.join(TARGET_DIR, subpath))
            assert len(os.listdir(os.path.join(TARGET_DIR, subpath))) == 0
        assert len(os.listdir(os.path.join(SOURCE_DIR))) == 0


@patch("iiif_pipeline.clients.ArchivesSpaceClient.get_object")
@patch("iiif_pipeline.clients.AWSClient.upload_files")
def test_pipeline_exception(mock_aws_client, mock_get_object, caplog):
    """Ensures that the pipeline handles exceptions.

    Target directories are expected to be empty, and the exception should be
    caught and logged.
    """
    mock_get_object.return_value = {
        "title": random_string(),
        "dates": "1945-1950",
        "uri": random_string()}
    mock_aws_client.side_effect = Exception()
    with archivesspace_vcr.use_cassette("get_ao.json"):
        IIIFPipeline().run(SOURCE_DIR, TARGET_DIR, False, False, False)
        log_records = [r for r in caplog.records if r.levelname == "ERROR"]
        assert len(log_records) == len(UUIDS)
        for subpath in ["images", "pdfs", "manifests"]:
            assert os.path.isdir(os.path.join(TARGET_DIR, subpath))
            assert len(os.listdir(os.path.join(TARGET_DIR, subpath))) == 0


def teardown():
    for d in [SOURCE_DIR, TARGET_DIR]:
        shutil.rmtree(d)
