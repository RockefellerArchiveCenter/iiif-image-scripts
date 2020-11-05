import argparse
import logging
import os
import shortuuid

from aws_upload import AWSClient
from derivatives import DerivativeMaker
from create_manifest import ManifestMaker
from get_ao import ArchivesSpaceClient


parser = argparse.ArgumentParser(description="Generates JPEG2000 images from TIF files based on input and output directories")
parser.add_argument("source_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
parser.add_argument("--skip", help="Skips files ending in `_001` during derivative creation.")
args = parser.parse_args()

class IIIFPipeline:
    def __init__(self):
        logfile = 'iiif_generation.log'
        logging.basicConfig(filename=logfile,
                            level=logging.INFO)
        self.config = ConfigParser().read("local_settings.cfg")

    def run(self, source_dir, skip):
        """Instantiates and runs derivative creation, manifest creation, and AWS upload files.

        Args:
            source_directory (str): Directory path to original source files.
            skip (bool): Boolean that indicates whether the derivative creation script should skip
                files ending with `_001`.
        """
        as_client = ArchivesSpaceClient() # TODO: the config values for these should be passed in here
        aws_client = AWSClient() # TODO: the config values for these should be passed in here
        jp2_dir = os.path.join(source_dir, "images")
        pdf_dir = os.path.join(source_dir, "pdfs")
        manifest_dir = os.path.join(source_dir, "manifests")
        for path in [jp2_dir, pdf_dir, manifest_dir]:
            if not os.path.exists(path):
                os.makedirs(path)
        excluded_directories = set([source_dir,
                                    jp2_dir,
                                    pdf_dir,
                                    manifest_dir])
        directories = [x[0] for x in os.walk(source_dir) if x[0] not in excluded_directories]
        for directory in directories:
            ref_id = directory.split('/')[-1]
            try:
                obj_data = as_client.get_object(ref_id)
                identifier = shortuuid.uuid(name=obj_data["uri"])
                DerivativeMaker().create_jp2(directory, jp2_dir, identifier, skip)
                ManifestMaker(
                    self.config.get("ImageServer", "baseurl")).create_manifest(
                        jp2_dir, manifest_dir, identifier, obj_data)
                DerivativeMaker().make_pdf(pdf_dir)
                aws_client.upload_files(jp2_dir, manifest_dir)
            except Exception as e:
                # TODO: add cleanup function
                logging.error(e)

IIIFPipeline().run(args.source_directory, args.skip)
