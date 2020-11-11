import os
import random
import shutil
import string
import vcr
from configparser import ConfigParser


archivesspace_vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='fixtures/cassettes',
    record_mode='once',
    match_on=['path', 'method'],
    filter_query_parameters=['username', 'password'],
    filter_headers=['Authorization', 'X-ArchivesSpace-Session'],
)


def copy_sample_files(directory, identifiers, page_count, suffix, to_master=False):
    """Duplicates a sample file.

    Args:
        directory (str): Initial path of directory containing images to copy.
        identifiers (list): Identifiers used in filenames.
        page_count (int): The number of files to generate for each identifier.
        suffix (str): The filename suffix (extension) to be used
    """
    for f in os.listdir(directory):
        for ident in identifiers:
            for page in range(page_count):
                target = os.path.join(directory, "{}_{}.{}".format(ident, page, suffix))
                if to_master:
                    target = os.path.join(directory, ident, "master", "{}_{}.{}".format(ident, page, suffix))
                    if not os.path.isdir(os.path.join(directory, ident, "master")):
                        os.makedirs(os.path.join(directory, ident, "master"))
                shutil.copyfile(
                    os.path.join(directory, f),
                    os.path.join(target))
        os.remove(os.path.join(directory, f))


def get_config():
    config = ConfigParser()
    config.read("local_settings.cfg")
    return config


def random_string(length=10):
    """Generates random ascii lowercase letters."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
