import os
import shutil
import random

import botocore.session
from botocore.stub import Stubber, ANY

from helpers import copy_sample_files, random_string
from iiif_pipeline.aws_upload import UploadFiles


MANIFEST_FIXTURES = os.path.join("fixtures", "manifests")
MANIFEST_DIR = os.path.join("/", "manifests")
DERIVATIVE_FIXTURES = os.path.join("fixtures", "jp2")
DERIVATIVE_DIR = os.path.join("/", "derivatives")
UUIDS = [random_string() for x in range(random.randint(1,3))]
PAGE_COUNT = random.randint(1,5)

def setup():
    for d in [MANIFEST_DIR, DERIVATIVE_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(DERIVATIVE_FIXTURES, DERIVATIVE_DIR)
    shutil.copytree(MANIFEST_FIXTURES, MANIFEST_DIR)
    copy_sample_files(DERIVATIVE_DIR, UUIDS, PAGE_COUNT, "jp2")
    copy_sample_files(MANIFEST_DIR, UUIDS, PAGE_COUNT, "json")

def test_s3_check():
    s3 = botocore.session.get_session().create_client("s3")
    head_response = {}  # TODO: add a response for head_object
    expected_params = {'Bucket': ANY}  # TODO: add expected_params
    with Stubber(s3) as stubber:
        stubber.add_response("head_object", head_response, expected_params)
        found = UploadFiles().s3_check(DERIVATIVE_DIR, MANIFEST_DIR)
        assert found == False

# TODO: tests for run method.
# The trick here is that the botocore Stubber does not include methods for
# upload_file, so we'll need to find some other way of mocking that.
