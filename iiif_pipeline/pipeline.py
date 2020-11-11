import logging
import os
import shortuuid
from configparser import ConfigParser

from .clients import ArchivesSpaceClient, AWSClient
from .derivatives import create_jp2, create_pdf
from .manifests import ManifestMaker
from .helpers import matching_files, refid_dirs


class IIIFPipeline:
    def __init__(self):
        logfile = 'iiif_generation.log'
        logging.basicConfig(filename=logfile,
                            level=logging.INFO)
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")

    def run(self, source_dir, skip):
        """Instantiates and runs derivative creation, manifest creation, and AWS upload files.

        Args:
            source_dir (str): A directory containing subdirectories (named using ref ids) for archival objects
            skip (bool): Boolean that indicates whether the derivative creation script should skip
                files ending with `_001`.
        """
        if not os.path.isdir(source_dir):
            raise Exception("{} is not a path to a directory.".format(source_dir))
        as_client = ArchivesSpaceClient(
            self.config.get("ArchivesSpace", "baseurl"),
            self.config.get("ArchivesSpace", "username"),
            self.config.get("ArchivesSpace", "password"),
            self.config.get("ArchivesSpace", "repository"))
        aws_client = AWSClient(
            self.config.get("S3", "region_name"),
            self.config.get("S3", "aws_access_key_id"),
            self.config.get("S3", "aws_secret_access_key"),
            self.config.get("S3", "bucketname"))
        jp2_dir = os.path.join(source_dir, "images")
        pdf_dir = os.path.join(source_dir, "pdfs")
        manifest_dir = os.path.join(source_dir, "manifests")
        for path in [jp2_dir, pdf_dir, manifest_dir]:
            if not os.path.exists(path):
                os.makedirs(path)
        object_dirs = refid_dirs(source_dir, [jp2_dir, pdf_dir, manifest_dir])
        for directory in object_dirs:
            ref_id = directory.split('/')[-1]
            try:
                obj_source_dir = os.path.join(directory, "master")
                if not os.path.isdir(os.path.join(source_dir, obj_source_dir)):
                    raise Exception("Object directory {} does not have a subdirectory named `master`".format(directory))
                obj_data = as_client.get_object(ref_id)
                identifier = shortuuid.uuid(name=obj_data["uri"])
                create_jp2(matching_files(obj_source_dir, skip=skip, prepend=True), jp2_dir, identifier)
                logging.info("JPEG2000 derivatives created for {}".format(identifier))
                ManifestMaker(
                    self.config.get("ImageServer", "baseurl"), manifest_dir).create_manifest(
                        matching_files(jp2_dir, prefix=identifier), jp2_dir, identifier, obj_data)
                logging.info("IIIF Manifest created for {}".format(identifier))
                create_pdf(matching_files(jp2_dir, prefix=identifier, prepend=True), identifier, pdf_dir)
                logging.info("Concatenated PDF created for {}".format(identifier))
                aws_client.upload_files(matching_files(jp2_dir, prefix=identifier, prepend=True), jp2_dir)
                logging.info("JPEG2000 files uploaded for {}".format(identifier))
                aws_client.upload_files(matching_files(pdf_dir, prefix=identifier, prepend=True), pdf_dir)
                logging.info("PDF file uploaded for {}".format(identifier))
                # TODO: add cleanup function
            except Exception as e:
                # TODO: add cleanup function
                print(e)
                logging.error(e)
                pass
