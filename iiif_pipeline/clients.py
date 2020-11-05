import boto3
import logging
import magic
import os

from asnake import utils
from asnake.aspace import ASpace
from botocore.exceptions import ClientError
from configparser import ConfigParser

class ArchivesSpaceClient:
    def __init__(self):
            self.config = ConfigParser()
            self.config.read("local_settings.cfg")
            self.client = ASpace(baseurl=self.config.get("ArchivesSpace", "baseurl"),
                            username=self.config.get("ArchivesSpace", "username"),
                            password=self.config.get("ArchivesSpace", "password"),
                            repository=self.config.get("ArchivesSpace", "repository")).client

    def get_object(self, ref_id):
        """Gets archival object title and date from an ArchivesSpace refid.

        Args:
            ident (str): an ArchivesSpace refid.
        Returns:
            obj (dict): A dictionary representation of an archival object from ArchivesSpace.
        """
        results = self.client.get(
            'repositories/{}/find_by_id/archival_objects?ref_id[]={}'.format(
                self.config.get("ArchivesSpace", "repository"), ref_id)).json()
        if not results.get("archival_objects"):
            raise Exception("Could not find an ArchivesSpace object matching refid: {}".format(ref_id))
        else:
            obj_uri = results["archival_objects"][0]["ref"]
            obj = self.client.get(obj_uri).json()
            if not obj.get("dates"):
                obj["dates"] = utils.find_closest_value(obj, 'dates', self.client)
            return self.format_data(obj)

    def format_data(self, data):
        """Parses ArchivesSpace data.

        Args:
            data (dict): ArchivesSpace data.
        Returns:
            parsed (dict): Parsed data, with only required fields present.
        """
        title = data.get("title", data.get("display_string")).title()
        dates = ", ".join([utils.get_date_display(d, self.client) for d in data.get("dates", [])])
        return {"title": title, "dates": dates}


class AWSClient:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.s3 = boto3.resource(service_name='s3',
                            region_name=self.config.get("S3", "region_name"),
                            aws_access_key_id=self.config.get("S3", "aws_access_key_id"),
                            aws_secret_access_key=self.config.get("S3", "aws_secret_access_key"))
        self.bucket = self.config.get("S3", "bucketname")

    def upload_files(self, derivative_dir, manifest_dir):
        """Iterates over directories and conditionally uploads files to S3.

        Args:
            derivative_dir (str): Directory path to derivative image files.
            manifest_dir (str): Directory path to manifest files.
        """
        for dir in [derivative_dir, manifest_dir]:
            for file in os.listdir(dir):
                if not file.startswith('.'):
                    key = file.split(".")[0]
                    if self.object_in_bucket(key, dir):
                        logging.error("{} already exists in {}".format(key, self.bucket))
                    else:
                        if file.endswith(".json"):
                            type = "application/json"
                        else:
                            type = magic.from_file(os.path.join(dir, file), mime=True)
                        self.s3.meta.client.upload_file(os.path.join(dir, file),
                                                        self.bucket, os.path.join(dir.split("/")[-1], key),
                                                        ExtraArgs={'ContentType': type})

    def object_in_bucket(self, key, dir):
        """Checks if a file already exists in an S3 bucket.

        Args:
            key (str): A filename without the trailing filetype.
            dir (str): A directory path containing files.
        Returns:
            boolean: True if file exists, false otherwise.
        """
        try:
            self.s3.Object(self.bucket, os.path.join(dir.split("/")[-1], key)).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                logging.error(e)
                return False
