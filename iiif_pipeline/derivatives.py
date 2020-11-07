import math
import mimetypes
import os
import re
import subprocess

import img2pdf
from PIL import Image
from PIL.TiffTags import TAGS

class DerivativeMaker:

    def create_jp2(self, files, derivative_dir, uuid):
        """Creates JPEG2000 files from TIFF files.

        Args:
            files (list): Filepaths for source files, which include source directory.
            derivative_dir (str): Path to directory location to save JP2 files.
            uuid (str): A unique identifier to use for derivative image filenaming.
        """
        default_options = ["-r 1.5",
                           "-c [256,256],[256,256],[128,128]",
                           "-b 64,64",
                           "-p RPCL"
                           ]
        for original_file in files:
            derivative_file = self.make_filename(derivative_dir, original_file, uuid)
            if os.path.isfile(derivative_file):
                pass
                # TODO: handle replace
            else:
                if self.is_tiff(original_file):
                    try:
                        resolutions = self.calculate_layers(original_file)
                        cmd = "opj_compress -i {} -o {} -n {} {} -SOP".format(
                            original_file, derivative_file, resolutions, ' '.join(default_options))
                        result = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
                    except Exception as e:
                        raise Exception("Error creating JPEG2000: {}".format(e)) from e
                else:
                    raise Exception("Error creating JPEG2000: {} is not a valid TIFF".format(original_file))

    def create_pdf(self, files, identifier, pdf_dir):
        """Creates concatenated PDFS from JPEG2000 files.

        Args:
            files (list): Filepaths of JPEG2000 files.
            identifier (str): Identifier of created PDF file.
            pdf_dir (str): Directory in which to save the PDF file.
        """
        try:
            with open("{}.pdf".format(os.path.join(pdf_dir, identifier)), "wb") as f:
                f.write(img2pdf.convert(files))
        except Exception as e:
            raise Exception("Error creating pdf: {}".format(e)) from e

    def make_filename(self, end_directory, file, uuid):
        """Make derivative filenames based on original filenames.

        Args:
            end_directory (str): the ending directory for derivative creation.
            file (str): string representation of a filename.
            uuid (str): unique identifier for the group of objects.
        Returns:
            derivative_file (str): concatenated string of end directory and file.
        """
        new_id = file.replace(file.split("_")[0], uuid)
        fname = new_id.split(".")[0]
        derivative_file = os.path.join(end_directory, "{}.jp2".format(fname))
        return derivative_file

    def calculate_layers(self, file):
        """Calculates the number of layers based on pixel dimensions.

        For TIFF files, image tag 256 is the width, and 257 is the height.

        Args:
            file (str): filename of a TIFF image file.
        Returns:
            layers (int): number of layers to convert to
        """
        with Image.open(file) as img:
            width = [w for w in img.tag[256]][0]
            height = [h for h in img.tag[257]][0]
        pixel_dimension = max(width, height)
        layers = math.ceil((math.log(pixel_dimension) / math.log(2)) - ((math.log(96) / math.log(2)))) + 1
        return layers

    def is_tiff(self, file):
        """Checks whether a file is a tiff.

        Args:
            file (str): string representation of a filename.
        Returns:
            boolean: True if tiff file, false otherwise.
        """
        type = mimetypes.MimeTypes().guess_type(file)[0]
        return True if type == "image/tiff" else False
