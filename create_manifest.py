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
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
    parser.add_argument("output_dir", help="The full directory path to store derivative files in (ex. /Documents/derivatives/)")
    return parser

def clean_directories(input_dir, output_dir):
    image_dir = args.input_dir if args.input_dir.endswith('/') else args.input_dir + '/'
    manifest_dir = args.output_dir if args.output_dir.endswith('/') else args.output_dir + '/'
    return image_dir, manifest_dir

parser = get_parser()
args = parser.parse_args()
fac = ManifestFactory()
fac.set_debug("error")

image_dir, manifest_dir = clean_directories(args.input_dir, args.output_dir)
fac.set_base_image_dir(image_dir)
fac.set_base_prezi_dir(manifest_dir)
fac.set_base_prezi_uri("http://example.org/iiif/prezi/")
fac.set_base_image_uri("http://example.org/iiif/image/")

def authorize_as():
    global aspace
    aspace = ASpace(
        baseurl=config.get("ArchivesSpace", "baseurl"),
        username=config.get("ArchivesSpace", "username"),
        password=config.get("ArchivesSpace", "password"),
    )

def get_ao(refid):
    refs = aspace.client.get('repositories/2/find_by_id/archival_objects?ref_id[]={}'.format(refid)).json()
    ao_id = refs.get("archival_objects")[0].get("ref")
    ao = aspace.client.get(ao_id).json()
    return ao

def get_identifiers(image_dir):
    identifiers = []
    for file in os.listdir(image_dir):
        identifier = file.split('_')[0]
        identifiers.append(identifier)
    return list(set(identifiers))

def get_page(file):
    name = file.split('.')[0]
    page = name.split('_')[-1]
    return page

def get_matching_files(ident, image_dir):
    files = []
    for file in os.listdir(image_dir):
        if file.startswith(ident):
            files.append(file)
    return files

def get_dimensions(file):
    with Image.open(file) as img:
        image_width, image_height = img.size
        return image_width, image_height

authorize_as()
identifiers = get_identifiers(image_dir)
for ident in identifiers:
    # TO DO: Change Manifest Label to AO Title or inherit closest title
    manifest_label = ident.title()
    manifest = fac.manifest(ident=ident, label=manifest_label)
    seq = manifest.sequence()
    page_number = 0
    files = sorted(get_matching_files(ident, image_dir))
    for file in files:
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
