import logging
import math
import mimetypes
import os
import re
import subprocess

from pathlib import Path
from PIL import Image
from PIL.TiffTags import TAGS

class DerivativeMaker:

    def create_jp2(self, source_dir, derivative_dir, uuid, skip):
        """Iterates over files in a directory and creates derivative JP2 files for
        each on if it is a valid tiff file.

        Args:
            source_dir (str): Path to directory containing source image files (tiffs).
            derivative_dir (str): Path to directory location to save JP2 files.
            uuid (str): A unique identifier to use for derivative image filenaming.
            skip (bool): Boolean that tells the script whether to skip files
                ending with `_001`.
        """
        default_options = ["-r 1.5",
                           "-c [256,256],[256,256],[128,128]",
                           "-b 64,64",
                           "-p RPCL"
                           ]

        files = [file for file in os.listdir(source_dir)]
        if skip is not None:
            for file in files:
                if file.split('.')[0].endswith('_001'):
                    files.remove(file)
        for file in files:
                original_file, derivative_file = self.make_filenames(source_dir, derivative_dir, file, uuid)
                identifier = re.split('[/.]', derivative_file)[-2]
                if os.path.isfile(derivative_file):
                    logging.error("{} already exists".format(derivative_file))
                else:
                    if self.is_tiff(original_file):
                        width, height = self.get_dimensions(original_file)
                        resolutions = self.calculate_layers(width, height)
                        cmd = "opj_compress -i {} -o {} -n {} {} -SOP".format(
                            original_file, derivative_file, resolutions, ' '.join(default_options))
                        result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
                        logging.info(result.decode().replace('\n', ' ').replace('[INFO]', ''))
                    else:
                        logging.error("{} is not a valid tiff file".format(original_file))

    def make_filenames(self, start_directory, end_directory, file, uuid):
        """Make derivative filenames based on original filenames.

        Args:
            start_directory (str): the start directory with the original files.
            end_directory (str): the ending directory for derivative creation.
            file (str): string representation of a filename.
            uuid (str): unique identifier for the group of objects.
        Returns:
            original_file (str): concatenated string of original directory and file.
            derivative_file (str): concatenated string of end directory and file.
        """
        original_file = os.path.join(start_directory, file)
        new_id = file.replace(file.split("_")[0], uuid)
        fname = new_id.split(".")[0]
        derivative_file = os.path.join(end_directory, "{}.jp2".format(fname))
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
        Returns:
            layers (int): number of layers to convert to
        """
        pixdem = max(width, height)
        layers = math.ceil((math.log(pixdem) / math.log(2)) - ((math.log(96) / math.log(2)))) + 1
        return layers

    def is_tiff(self, file):
        """Checks whether a file is a tiff.

        Args:
            file (str): string representation of a filename.
        Returns:
            boolean: True if tiff file, false otherwise.
        """
        type = mimetypes.MimeTypes().guess_type(file)[0]
        if type == "image/tiff":
            return True
        else:
            return False
