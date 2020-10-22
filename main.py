import argparse
import boto3
import logging
import os

from asnake.aspace import ASpace
from configparser import ConfigParser
from create_derivatives import DerivativeMaker
from create_manifest import ManifestMaker
from iiif_prezi.factory import ManifestFactory


parser = argparse.ArgumentParser(description="Generates JPEG2000 images from TIF files based on input and output directories")
parser.add_argument("source_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
parser.add_argument("derivative_directory", help="The full directory path to store derivative files in (ex. /Documents/derivatives/)")
parser.add_argument("manifest_directory", help="The full directory path to store manifest files in (ex. /Documents/manifests/)")
parser.add_argument("--skip", help="Skips files ending in `_001` during derivative creation.")
args = parser.parse_args()

class RunProcesses:
    def __init__(self, source_directory, derivative_directory, manifest_directory, skip):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.s3 = boto3.resource(service_name='s3',
                            region_name='us-east-1',
                            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'))
        self.bucket = self.config.get("S3", "bucketname")
        self.client = ASpace(baseurl=self.config.get("ArchivesSpace", "baseurl"),
                        username=self.config.get("ArchivesSpace", "username"),
                        password=self.config.get("ArchivesSpace", "password"),
                        repository=self.config.get("ArchivesSpace", "repository")).client
        self.imageurl=self.config.get("ImageServer", "imageurl")
        self.default_options = [
                           "-r 1.5",
                           "-c [256,256],[256,256],[128,128]",
                           "-b 64,64",
                           "-p RPCL"
                           ]
        self.fac = ManifestFactory()
        self.fac.set_debug("error")
        self.source_dir = source_directory if source_directory.endswith('/') else source_directory + '/'
        self.derivative_dir = derivative_directory if derivative_directory.endswith('/') else derivative_directory + '/'
        self.manifest_dir = manifest_directory if manifest_directory.endswith('/') else manifest_directory + '/'
        self.skip = skip

    def run(self):
        derivatives = DerivativeMaker(self.source_dir,
                                      self.derivative_dir,
                                      self.skip,
                                      self.s3,
                                      self.bucket,
                                      self.default_options)
        derivatives.run()
        manifests = ManifestMaker(self.derivative_dir,
                                  self.manifest_dir,
                                  self.imageurl,
                                  self.fac,
                                  self.client,
                                  self.s3,
                                  self.bucket)
        manifests.run()

RunProcesses(args.source_directory, args.derivative_directory, args.manifest_directory, args.skip).run()
