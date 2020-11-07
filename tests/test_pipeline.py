import os
import shutil
from unittest.mock import patch

from iiif_pipeline.pipeline import IIIFPipeline
from helpers import archivesspace_vcr

SOURCE_DIR = os.path.join("/", "source")

def setup():
    if os.path.isdir(SOURCE_DIR):
        shutil.rmtree(SOURCE_DIR)
    os.makedirs(SOURCE_DIR)


@patch("iiif_pipeline.clients.ArchivesSpaceClient.get_object")
@patch("iiif_pipeline.clients.AWSClient.upload_files")
@patch("iiif_pipeline.derivatives.create_jp2")
@patch("iiif_pipeline.derivatives.create_pdf")
@patch("iiif_pipeline.manifests.ManifestMaker.create_manifest")
def test_main(mock_as_client, mock_aws_client, mock_jp2, mock_pdf, mock_manifest):
    with archivesspace_vcr.use_cassette("get_ao.json"):
        IIIFPipeline().run(SOURCE_DIR, False)
        for subpath in ["images", "pdfs", "manifests"]:
            assert os.path.isdir(os.path.join(SOURCE_DIR, subpath))
        IIIFPipeline().run(SOURCE_DIR, True)


def teardown():
    shutil.rmtree(SOURCE_DIR)
