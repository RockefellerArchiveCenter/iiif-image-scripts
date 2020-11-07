import os
import shutil
import random

import botocore.session
from botocore.stub import Stubber, ANY

from helpers import copy_sample_files, get_config, random_string
from iiif_pipeline.clients import AWSClient


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

def test_object_in_bucket():
    config = get_config()
    key = random.choice(os.listdir(DERIVATIVE_DIR))
    aws = AWSClient(
        config.get("S3", "region_name"),
        config.get("S3", "aws_access_key_id"),
        config.get("S3", "aws_secret_access_key"),
        config.get("S3", "bucketname"))
    expected_params = {"Bucket": config.get("S3", "bucketname"), "Key": os.path.join(DERIVATIVE_DIR, key)}
    with Stubber(aws.s3.meta.client) as stubber:
        stubber.add_response("head_object", service_response={}, expected_params=expected_params)
        found = aws.object_in_bucket(DERIVATIVE_DIR, key)
        assert found == True

        stubber.add_client_error("head_object", service_error_code='404', expected_params=expected_params)
        not_found = aws.object_in_bucket(DERIVATIVE_DIR, key)
        assert not_found == False

# TODO: tests for run method.
# The trick here is that the botocore Stubber does not include methods for
# upload_file, so we'll need to find some other way of mocking that.
