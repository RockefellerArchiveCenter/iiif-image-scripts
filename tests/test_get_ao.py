from unittest.mock import patch

from helpers import random_string
from iiif_pipeline.get_ao import GetObject

@patch("requests.post")
@patch("requests.get")
def test_run(mock_post, mock_get):
    mock_post.return_value.status_code = 200
    mock_get.return_value.json = {}
    object = GetObject().run(random_string())
    assert object == ({}, "", "")
