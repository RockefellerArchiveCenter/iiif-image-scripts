import argparse
import boto3
import logging
import magic
import os

from botocore.exceptions import ClientError
from configparser import ConfigParser
from create_derivatives import DerivativeMaker
from create_manifest import ManifestMaker


parser = argparse.ArgumentParser(description="Generates JPEG2000 images from TIF files based on input and output directories")
parser.add_argument("source_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
parser.add_argument("--skip", help="Skips files ending in `_001` during derivative creation.")
args = parser.parse_args()

class GenerateFiles:
    def __init__(self):
        logfile = 'iiif_generation.log'
        logging.basicConfig(filename=logfile,
                            level=logging.INFO)
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.s3 = boto3.resource(service_name='s3',
                            region_name='us-east-1',
                            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'))
        self.bucket = self.config.get("S3", "bucketname")

    def run(self, source_directory, skip):
        source_dir = source_directory if source_directory.endswith('/') else source_directory + '/'
        derivative_dir = "{}{}".format(source_dir, "images")
        manifest_dir = "{}{}".format(source_dir, "manifests")
        for x in [derivative_dir, manifest_dir]:
            if not os.path.exists(x):
                os.mkdir(x)
        excluded_directories = set([source_dir,
                                    "{}{}".format(source_dir, "images"),
                                    "{}{}".format(source_dir, "manifests")])
        directories = [x[0] for x in os.walk(source_dir) if x[0] not in excluded_directories]
        derivatives = DerivativeMaker()
        manifests = ManifestMaker()
        for directory in directories:
            derivatives.run(directory, derivative_dir, skip)
            manifests.run(derivative_dir, manifest_dir)
        self.upload_s3(derivative_dir, manifest_dir)

    def upload_s3(self, derivative_dir, manifest_dir):
        for dir in [derivative_dir, manifest_dir]:
            for file in os.listdir(dir):
                if not file.startswith('.'):
                    key = file.split(".")[0]
                    if self.s3_check(key, dir):
                        logging.error("{} already exists in {}".format(key, self.bucket))
                    else:
                        if file.endswith(".json"):
                            type = "application/json"
                        else:
                            type = magic.from_file("{}/{}".format(dir, file), mime=True)
                        self.s3.meta.client.upload_file('{}/{}'.format(dir, file),
                                                        self.bucket, '{}/{}'.format(dir.split("/")[-1], key),
                                                        ExtraArgs={'ContentType': type})

    def s3_check(self, key, dir):
        try:
            self.s3.Object(self.bucket, '{}/{}'.format(dir.split("/")[-1], key)).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                print(e)


GenerateFiles().run(args.source_directory, args.skip)
