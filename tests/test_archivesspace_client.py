import json
import pytest

from helpers import archivesspace_vcr, get_config, random_string
from iiif_pipeline.clients import ArchivesSpaceClient

def test_run():
    config = get_config()
    found_refid = "aspace_b1f076a9f49d369034188c232f7cdf25"
    missing_refid = "aspace_b1f076a9f49d369034188c232f7cdf26"
    with archivesspace_vcr.use_cassette("get_ao.json"):
        object = ArchivesSpaceClient(
            config.get("ArchivesSpace", "baseurl"),
            config.get("ArchivesSpace", "username"),
            config.get("ArchivesSpace", "password"),
            config.get("ArchivesSpace", "repository")).get_object(found_refid)
        assert isinstance(object, dict)
        assert "title" in object
        assert "dates" in object

        with pytest.raises(Exception):
            ArchivesSpaceClient().get_object(missing_refid)
