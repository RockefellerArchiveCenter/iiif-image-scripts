import json
from unittest.mock import patch

from helpers import archivesspace_vcr, random_string
from iiif_pipeline.get_ao import GetObject

def test_run():
    found_refid = "aspace_b1f076a9f49d369034188c232f7cdf25"
    missing_refid = "aspace_b1f076a9f49d369034188c232f7cdf26"
    with archivesspace_vcr.use_cassette("get_ao.json"):
        for refid in [found_refid, missing_refid]:
            object = GetObject().run(refid)
            assert isinstance(object, tuple)    
