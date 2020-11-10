import math
import magic
import os
import subprocess

import img2pdf
from PIL import Image


def calculate_layers(file):
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
    return math.ceil((math.log(max(width, height)) / math.log(2)) - ((math.log(96) / math.log(2)))) + 1


def is_tiff(file):
    """Checks whether a file is a tiff.

    Args:
        file (str): string representation of a filename.
    Returns:
        boolean: True if tiff file, false otherwise.
    """
    # TODO: evaluate if we can use mimetypes library instead
    content_type = magic.from_file(file, mime=True)
    return True if content_type == "image/tiff" else False


def create_jp2(files, derivative_dir, identifier):
    """Creates JPEG2000 files from TIFF files.

    The default options for conversion below are:
    - Compression ration of `1.5`
    - Precinct size: `[256,256]` for first two layers and then `[128,128]` for all others
    - Code block size of `[64,64]`
    - Progression order of `RPCL`

    Args:
        files (list): Filepaths for source files, which include source directory.
        derivative_dir (str): Path to directory location to save JP2 files.
        identifier (str): A unique identifier to use for derivative image filenaming.
    """
    default_options = ["-r 1.5",
                       "-c [256,256],[256,256],[128,128]",
                       "-b 64,64",
                       "-p RPCL"
                       ]
    for original_file in files:
        derivative_file = os.path.join(
            derivative_dir, "{}_{}.jp2".format(identifier, original_file.split("_")[-1]))
        if os.path.isfile(derivative_file):
            pass
            # TODO: handle replace
        else:
            if is_tiff(original_file):
                try:
                    layers = calculate_layers(original_file)
                    cmd = "opj_compress -i {} -o {} -n {} {} -SOP".format(
                        original_file, derivative_file, layers, ' '.join(default_options))
                    subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
                except Exception as e:
                    raise Exception("Error creating JPEG2000: {}".format(e)) from e
            else:
                raise Exception("Error creating JPEG2000: {} is not a valid TIFF".format(original_file))


def create_pdf(files, identifier, pdf_dir):
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
