import boto3
import logging
import os

from configparser import ConfigParser
from botocore.exceptions import ClientError

class UploadFiles:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.s3 = boto3.resource(service_name='s3',
                            region_name='us-east-1',
                            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'))
        self.bucket = self.config.get("S3", "bucketname")

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
                            type = magic.from_file(os.path.join(dir, file), mime=True)
                        self.s3.meta.client.upload_file(os.path.join(dir, file),
                                                        self.bucket, os.path.join(dir.split("/")[-1], key),
                                                        ExtraArgs={'ContentType': type})

    def s3_check(self, key, dir):
        try:
            self.s3.Object(self.bucket, os.path.join(dir.split("/")[-1], key)).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                print(e)
