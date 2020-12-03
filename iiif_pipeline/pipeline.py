import logging
import os
from configparser import ConfigParser

import ocrmypdf
import shortuuid

from .clients import ArchivesSpaceClient, AWSClient
from .derivatives import compress_pdf, create_jp2, create_pdf, ocr_pdf
from .helpers import cleanup_files, matching_files, refid_dirs
from .manifests import ManifestMaker


class IIIFPipeline:
    def __init__(self):
        logging.basicConfig(
            datefmt='%m/%d/%Y %I:%M:%S %p',
            filename='iiif_generation.log',
            format='%(asctime)s %(message)s',
            level=logging.INFO)
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        ocrmypdf.configure_logging(verbosity=-1)

    def run(self, source_dir, target_dir, skip, replace):
        """Instantiates and runs derivative creation, manifest creation, and AWS upload files.

        Args:
            source_dir (str): A directory containing subdirectories (named using ref ids) for archival objects.
            skip (bool): Flag to should skip files ending with `_001`.
            replace (bool): Flag to replace existing files.
        """
        if not os.path.isdir(source_dir):
            raise Exception(
                "{} is not a path to a directory.".format(source_dir))
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
        jp2_dir = os.path.join(target_dir, "images")
        pdf_dir = os.path.join(target_dir, "pdfs")
        manifest_dir = os.path.join(target_dir, "manifests")
        for path in [jp2_dir, pdf_dir, manifest_dir]:
            if not os.path.exists(path):
                os.makedirs(path)
        object_dirs = refid_dirs(source_dir, [jp2_dir, pdf_dir, manifest_dir])
        for directory in object_dirs:
            identifier = None
            ref_id = directory.split('/')[-1]
            try:
                obj_source_dir = os.path.join(directory, "master")
                if not os.path.isdir(os.path.join(source_dir, obj_source_dir)):
                    raise Exception(
                        "Object directory {} does not have a subdirectory named `master`".format(directory))
                obj_data = as_client.get_object(ref_id)
                identifier = shortuuid.uuid(name=obj_data["uri"])
                tiff_files = matching_files(
                    obj_source_dir, skip=skip, prepend=True)
                create_jp2(tiff_files, identifier, jp2_dir, replace)
                logging.info(
                    "JPEG2000 derivatives with identifier {} created for ref_id {}".format(identifier, ref_id))
                ManifestMaker(
                    self.config.get("ImageServer", "baseurl"), manifest_dir).create_manifest(
                        matching_files(jp2_dir, prefix=identifier), jp2_dir, identifier, obj_data, replace)
                logging.info(
                    "IIIF Manifest with identifier {} created for ref_id {}".format(
                        identifier, ref_id))
                jp2_files = matching_files(
                    jp2_dir, prefix=identifier, prepend=True)
                create_pdf(jp2_files, identifier, pdf_dir, replace)
                logging.info(
                    "Concatenated PDF with identifier {} created for ref_id {}".format(identifier, ref_id))
                compress_pdf(identifier, pdf_dir)
                logging.info(
                    "Compressed PDF with identifier {} created for {}".format(identifier, ref_id))
                ocr_pdf(identifier, pdf_dir)
                logging.info(
                    "OCRed PDF with identifier {} created for {}".format(identifier, ref_id))
                for src_dir, target_dir, file_type in [
                        (jp2_dir, "images", "JPEG2000 files"),
                        (pdf_dir, "pdfs", "PDF file"),
                        (manifest_dir, "manifests", "Manifest file")]:
                    uploads = matching_files(
                        src_dir, prefix=identifier, prepend=True)
                    aws_client.upload_files(uploads, target_dir, replace)
                    logging.info(
                        "{} uploaded for {}".format(
                            file_type, identifier))
                cleanup_files(identifier, [jp2_dir, pdf_dir, manifest_dir])
            except Exception as e:
                print(
                    "Error processing identifier {} with ref_id {}: {}".format(
                        identifier, ref_id, e))
                if identifier:
                    cleanup_files(identifier, [jp2_dir, pdf_dir, manifest_dir])
                logging.error(
                    "Error processing identifier {} with ref_id {}: {}".format(
                        identifier, ref_id, e))
                pass
