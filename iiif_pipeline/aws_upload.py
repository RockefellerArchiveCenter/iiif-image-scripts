import boto3
import logging
import magic
import os

from configparser import ConfigParser
from botocore.exceptions import ClientError

class AWSClient:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.s3 = boto3.resource(service_name='s3',
                            region_name=self.config.get("S3", "region_name"),
                            aws_access_key_id=self.config.get("S3", "aws_access_key_id"),
                            aws_secret_access_key=self.config.get("S3", "aws_secret_access_key"))
        self.bucket = self.config.get("S3", "bucketname")

    def upload_files(self, files, destination_dir):
        """Iterates over directories and conditionally uploads files to S3.

        Args:
            files (list): Filepaths to be uploaded.
            destination_dir: Path in the bucket in which the file should be stored.
        """
        for file in files:
            key = file.split(".")[0]
            if self.object_in_bucket(destination_dir, key):
                logging.error("{} already exists in {}".format(key, self.bucket))
            else:
                if file.endswith(".json"):
                    type = "application/json"
                else:
                    type = magic.from_file(file, mime=True)
                self.s3.meta.client.upload_file(file, self.bucket, destination_dir, key),
                                                ExtraArgs={'ContentType': type})

    def object_in_bucket(self, destination_dir, key):
        """Checks if a file already exists in an S3 bucket.

        Args:
            key (str): A filename without the trailing filetype.
            dir (str): A directory path containing files.
        Returns:
            boolean: True if file exists, false otherwise.
        """
        try:
            self.s3.Object(self.bucket, os.path.join(destination_dir, key)).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                logging.error(e)
                return False
