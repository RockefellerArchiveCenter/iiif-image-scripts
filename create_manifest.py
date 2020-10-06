import argparse
import os

from asnake.aspace import ASpace
from configparser import ConfigParser
from pathlib import Path
from PIL import Image
from iiif_prezi.factory import ManifestFactory


config = ConfigParser()
config.read("local_settings.cfg")

def get_parser():
    """Defines and gets parser arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="The full directory path of the jp2 image files (ex. /Documents/images/)")
    parser.add_argument("output_dir", help="The full directory path to store manifest files in (ex. /Documents/manifests/)")
    return parser

def clean_directories(input_dir, output_dir):
    """Structures input and manifest directories based on whether they end in '/'.

    Args:
        input_dir (str): string representation of full path to directory with image files.
        output_dir (str): string representation of full path to directory to save manifests.
    """
    image_dir = args.input_dir if args.input_dir.endswith('/') else args.input_dir + '/'
    manifest_dir = args.output_dir if args.output_dir.endswith('/') else args.output_dir + '/'
    return image_dir, manifest_dir

parser = get_parser()
args = parser.parse_args()
fac = ManifestFactory()
fac.set_debug("error")

"""Sets directories for use in the manifest creation. Will need to change for dev/production."""
image_dir, manifest_dir = clean_directories(args.input_dir, args.output_dir)
fac.set_base_image_dir(image_dir)
fac.set_base_prezi_dir(manifest_dir)
fac.set_base_prezi_uri("http://example.org/iiif/prezi/")
fac.set_base_image_uri("http://example.org/iiif/image/")

def authorize_as():
    """Authorize an ArchivesSpace session."""
    global aspace
    aspace = ASpace(
        baseurl=config.get("ArchivesSpace", "baseurl"),
        username=config.get("ArchivesSpace", "username"),
        password=config.get("ArchivesSpace", "password"),
    )

def get_ao(refid):
    """Gets a JSON representation of an archival object.

    Args:
        refid (str): an ArchivesSpace refid
    Returns:
        ao (dict): a JSON representation of an archival object
    """
    refs = aspace.client.get('repositories/2/find_by_id/archival_objects?ref_id[]={}'.format(refid)).json()
    ao_id = refs.get("archival_objects")[0].get("ref")
    ao = aspace.client.get(ao_id).json()
    return ao

def get_identifiers(image_dir):
    """Get a list of unique identifiers from files in a directory.

    Args:
        image_dir (str): a string representation of the directory containing image files.
    Returns:
        identifiers (lst): a list of unique identifiers.
    """
    identifiers = []
    for file in os.listdir(image_dir):
        identifier = file.split('_')[0]
        identifiers.append(identifier)
    return list(set(identifiers))

def get_matching_files(ident, image_dir):
    """Get a list of files that start with a specific refid.

    Args:
        ident (str): a string representation of an ArchivesSpace refid.
        image_dir (str): a string representation of the directory containing image files.
    Returns:
        files (lst): a list of files that matched the identifier.
    """
    files = []
    for file in os.listdir(image_dir):
        if file.startswith(ident):
            files.append(file)
    return files

def get_dimensions(file):
    """Get the pixel height and width of an image file.

    Args:
        file (str): an image filename
    Returns:
        image_width (int): pixel width of an image
        image_height (int): pixel height of an image
    """
    with Image.open(file) as img:
        image_width, image_height = img.size
        return image_width, image_height

authorize_as()
identifiers = get_identifiers(image_dir)
for ident in identifiers:
    """Sets the overall manifest labels, instantiate the manifest, and then
    creates a sequence in that manifest for a specific identifier.
    """
    # TO DO: Change Manifest Label to AO Title or inherit closest title
    manifest_label = ident.title()
    manifest = fac.manifest(ident=ident, label=manifest_label)
    seq = manifest.sequence()
    page_number = 0
    files = sorted(get_matching_files(ident, image_dir))
    for file in files:
        """Gets a refid from a file, and then creates a canvas and annotations
        based on image dimensions and base prezi directories.
        """
        ref = file[:-4]
        page_number = page_number + 1
        canvas_label = str(page_number)
        cvs = seq.canvas(ident=ref, label="Page {}".format(canvas_label))
        path = "{}{}".format(image_dir, file)
        width, height = get_dimensions(path)
        cvs.set_hw(width, height)
        anno = cvs.annotation()
        img = anno.image("{}{}".format(image_dir,file))
    manifest.toFile(compact=False)
