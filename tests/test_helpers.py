import os

from iiif_pipeline.helpers import matching_files

FIXTURE_FILEPATH = os.path.join("fixtures", "jp2")


def test_matching_files():
    matching = matching_files(FIXTURE_FILEPATH)
    assert len(matching) == 1
    matching = matching_files(FIXTURE_FILEPATH, prefix="sample")
    assert len(matching) == 1
    matching = matching_files(FIXTURE_FILEPATH, prefix="foo")
    assert len(matching) == 0
    matching = matching_files(FIXTURE_FILEPATH, prefix="sample", skip=True)
    assert len(matching) == 1
    matching = matching_files(FIXTURE_FILEPATH, prepend=True)
    assert matching[0].startswith(FIXTURE_FILEPATH)
