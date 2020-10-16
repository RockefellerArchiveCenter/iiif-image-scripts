import argparse
import boto3
import logging
import math
import mimetypes
import os
import re
import subprocess

from configparser import ConfigParser
from pathlib import Path
from PIL import Image
from PIL.TiffTags import TAGS

class DerivativeMaker:
    def __init__(self, source_dir, derivative_dir):
        config = ConfigParser()
        config.read("local_settings.cfg")
        self.s3 = boto3.resource(service_name='s3',
                                 region_name='us-east-1',
                                 aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                 aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'))
        logfile = 'derivative_log.log'
        logging.basicConfig(filename=logfile,
                            level=logging.INFO)
        self.bucket = config.get("S3", "bucketname")
        self.default_options = [
                           "-r 1.5",
                           "-c [256,256],[256,256],[128,128]",
                           "-b 64,64",
                           "-p RPCL"
                           ]

    def run(self):
        for file in os.listdir(source_dir):
            original_file, derivative_file = self.make_filenames(source_dir, derivative_dir, file)
            identifier = re.split('[/.]', derivative_file)[-2]
            if os.path.isfile(derivative_file):
                logging.error("{} already exists".format(derivative_file))
            else:
                if self.is_tiff(original_file):
                    width, height = self.get_dimensions(original_file)
                    resolutions = self.calculate_layers(width, height)
                    cmd = "opj_compress -i {} -o {} -n {} {} -SOP".format(
                        original_file, derivative_file, resolutions, ' '.join(self.default_options))
                    result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
                    logging.info(result.decode().replace('\n', ' ').replace('[INFO]', ''))
                    s3.meta.client.upload_file(derivative_file, self.bucket, identifier)
                else:
                    logging.error("{} is not a valid tiff file".format(original_file))

    def make_filenames(self, start_directory, end_directory, file):
        """Make derivative filenames based on original filenames.

        Args:
            start_directory (str): the start directory with the original files.
            end_directory (str): the ending directory for derivative creation.
            file (str): string representation of a filename.
        Returns
            original_file (str): concatenated string of original directory and file.
            derivative_file (str): concatenated string of end directory and file.
        """
        original_file = "{}{}".format(start_directory, file)
        fname = file.split(".")[0]
        derivative_file = "{}{}.jp2".format(end_directory, fname)
        return original_file, derivative_file

    def get_dimensions(self, file):
        """Gets pixel dimensions of a file.

        Args:
            file (str): filename of an image file.
        Returns:
            image_width (int): pixel width of an image
            image_height (int): pixel height of an image
        """
        with Image.open(file) as img:
            for x in img.tag[256]:
                image_width = x
            for y in img.tag[257]:
                image_height = y
            return image_width, image_height

    def calculate_layers(self, width, height):
        """Calculates the number of layers based on pixel dimensions.

        Args:
            width (int): width of an image
            height (int): height of an image
        Returns
            layers (int): number of layers to convert to
        """
        pixdem = max(width, height)
        layers = math.ceil((math.log(pixdem) / math.log(2)) - ((math.log(96) / math.log(2)))) + 1
        return layers

    def is_tiff(self, file):
        """Checks whether a file is a tiff.

        Args:
            file (str): string representation of a filename.
        Returns
            boolean: True if tiff file, false otherwise.
        """
        type = mimetypes.MimeTypes().guess_type(file)[0]
        if type == "image/tiff":
            return True
        else:
            return False

parser = argparse.ArgumentParser(description="Generates JPEG2000 images from TIF files based on input and output directories")
parser.add_argument("input_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
parser.add_argument("output_directory", help="The full directory path to store derivative files in (ex. /Documents/derivatives/)")
args = parser.parse_args()

source_dir = args.input_directory if args.input_directory.endswith('/') else args.input_directory + '/'
derivative_dir = args.output_directory if args.output_directory.endswith('/') else args.output_directory + '/'

DerivativeMaker(source_dir, derivative_dir).run()
