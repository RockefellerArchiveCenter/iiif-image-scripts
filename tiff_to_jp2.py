import argparse
import boto3
import logging
import math
import mimetypes
import os
import subprocess

from pathlib import Path
from PIL import Image
from PIL.TiffTags import TAGS

s3 = boto3.resource(service_name='s3',
                    region_name='us-east-1',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'))

logfile = 'logfile.log'
logging.basicConfig(filename=logfile,
                    level=logging.INFO)

default_options = [
                   "-r 1.5",
                   "-c [256,256],[256,256],[128,128]",
                   "-b 64,64",
                   "-p RPCL"
                   ]

def get_parser():
    """Defines and gets parser arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
    parser.add_argument("output_directory", help="The full directory path to store derivative files in (ex. /Documents/derivatives/)")
    return parser

parser = get_parser()
args = parser.parse_args()

def get_dimensions(file):
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

def clean_directories(start_directory, end_directory):
    """Structures input and manifest directories based on whether they end in '/'.

    Args:
        start_directory (str): string representation of full path to directory with source files.
        end_directory (str): string representation of full path to directory to save derivatives.

    Returns:
        source_dir (str): string representation of the full path to directory with source images with trailing slash
        derivative_dir (str): string representation of full path to directory to save derivatives with trailing slash
    """
    source_dir = args.input_directory if args.input_directory.endswith('/') else args.input_directory + '/'
    derivative_dir = args.output_directory if args.output_directory.endswith('/') else args.output_directory + '/'
    return source_dir, derivative_dir

def calculate_layers(width, height):
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

def is_tiff(file):
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

def make_filenames(start_directory, end_directory, file):
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

def upload_s3(dir, file, s3_connection):
    path = "{}{}".format(dir, file)
    data = open(path, 'rb')
    s3.meta.client.upload_file(path, 'raciif-dev', file)

def main():
    """Main function, which is run when this script is executed"""
    source_dir, derivative_dir = clean_directories(args.input_directory, args.output_directory)
    for file in os.listdir(args.input_directory):
        original_file, derivative_file = make_filenames(source_dir, derivative_dir, file)
        if os.path.isfile(derivative_file):
            logging.error("{} already exists".format(derivative_file))
        else:
            if is_tiff(original_file):
                width, height = get_dimensions(original_file)
                resolutions = calculate_layers(width, height)
                cmd = "opj_compress -i {} -o {} -n {} {} -SOP".format(
                    original_file, derivative_file, resolutions, ' '.join(default_options))
                result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
                logging.info(result.decode().replace('\n', ' ').replace('[INFO]', ''))
                upload_s3(derivative_dir, file, s3)
            else:
                logging.error("{} is not a valid tiff file".format(original_file))

if __name__ == "__main__":
    main()
