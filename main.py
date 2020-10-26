import argparse
import logging
import os
import shortuuid

from create_derivatives import DerivativeMaker
from create_manifest import ManifestMaker
from aws_upload import UploadFiles
from get_ao import GetObject


parser = argparse.ArgumentParser(description="Generates JPEG2000 images from TIF files based on input and output directories")
parser.add_argument("source_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
parser.add_argument("--skip", help="Skips files ending in `_001` during derivative creation.")
args = parser.parse_args()

class GenerateFiles:
    def __init__(self):
        logfile = 'iiif_generation.log'
        logging.basicConfig(filename=logfile,
                            level=logging.INFO)

    def run(self, source_directory, skip):
        """Instantiates and runs derivative creation, manifest creation, and AWS upload files.

        Args:
            source_directory (str): Directory path to original source files.
            skip (bool): Boolean that indicates whether the derivative creation script should skip
                files ending with `_001`.
        """
        archival_object = GetObject()
        derivatives = DerivativeMaker()
        manifests = ManifestMaker()
        aws = UploadFiles()
        source_dir = source_directory if source_directory.endswith('/') else source_directory + '/'
        derivative_dir = os.path.join(source_dir, "images")
        manifest_dir = os.path.join(source_dir, "manifests")
        for x in [derivative_dir, manifest_dir]:
            if not os.path.exists(x):
                os.mkdir(x)
        excluded_directories = set([source_dir,
                                    derivative_dir,
                                    manifest_dir])
        directories = [x[0] for x in os.walk(source_dir) if x[0] not in excluded_directories]
        for directory in directories:
            identifier = directory.split('/')[-1]
            ao, title, date = archival_object.run(identifier)
            uuid = shortuuid.uuid()
            if ao:
                derivatives.run(directory, derivative_dir, uuid, skip)
                manifests.run(derivative_dir, manifest_dir, uuid, title, date)
            else:
                logging.error("Could not find archival object with refid of {}".format(identifier))
        aws.upload_s3(derivative_dir, manifest_dir)

GenerateFiles().run(args.source_directory, args.skip)
