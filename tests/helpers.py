import os
import random
import shutil
import string
import vcr


archivesspace_vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='fixtures/cassettes',
    record_mode='once',
    match_on=['path', 'method', 'query'],
    filter_query_parameters=['username', 'password'],
    filter_headers=['Authorization', 'X-ArchivesSpace-Session'],
)


def copy_sample_files(dir, identifiers, page_count, suffix):
    """Duplicates a sample file.

    Args:
        identifiers (list): Identifiers used in filenames.
        page_count (int): The number of files to generate for each identifier.
        suffix (str): The filename suffix (extension) to be used
    """
    for f in os.listdir(dir):
        for ident in identifiers:
            for page in range(page_count):
                shutil.copyfile(
                    os.path.join(dir, f),
                    os.path.join(dir, "{}_{}.{}".format(ident, page, suffix)))
        os.remove(os.path.join(dir, f))


def random_string(length=10):
    """Generates random ascii lowercase letters."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
