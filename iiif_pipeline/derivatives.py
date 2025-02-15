import math
import os
import subprocess
from mimetypes import MimeTypes

from PIL import Image

from .helpers import get_page_number


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
    return math.ceil((math.log(max(width, height)) / math.log(2)
                      ) - ((math.log(96) / math.log(2)))) + 1


def is_tiff(file):
    """Checks whether a file is a tiff.

    Args:
        file (str): string representation of a filename.
    Returns:
        boolean: True if tiff file, false otherwise.
    """
    content_type = MimeTypes().guess_type(file)[0]
    return True if content_type == "image/tiff" else False


def create_jp2(files, identifier, derivative_dir, replace=False):
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
        replace (bool): Replace existing derivative files.
    """
    default_options = ["-r", "1.5",
                       "-c", "[256,256],[256,256],[128,128]",
                       "-b", "64,64",
                       "-p", "RPCL"]
    for original_file in files:
        derivative_path = os.path.join(derivative_dir, "{}_{}.jp2".format(
            identifier, get_page_number(original_file)))
        if (os.path.isfile(derivative_path) and not replace):
            raise FileExistsError(
                "Error creating JPEG2000: {} already exists".format(derivative_path))
        else:
            if is_tiff(original_file):
                layers = calculate_layers(original_file)
                cmd = ["/usr/local/bin/opj_compress",
                       "-i", original_file,
                       "-o", derivative_path,
                       "-n", str(layers),
                       "-SOP"] + default_options
                subprocess.run(cmd, check=True)
            else:
                raise Exception(
                    "Error creating JPEG2000: {} is not a valid TIFF".format(original_file))


def create_pdf(files, identifier, pdf_dir, replace=False):
    """Creates concatenated PDFS from JPEG2000 files.

    Args:
        files (list): Filepaths of JPEG2000 files.
        identifier (str): Identifier of created PDF file.
        pdf_dir (str): Directory in which to save the PDF file.
        replace (bool): Replace existing derivative files.
    """
    pdf_path = "{}.pdf".format(os.path.join(pdf_dir, identifier))
    if (os.path.isfile(pdf_path) and not replace):
        raise FileExistsError(
            "Error creating PDF: {} already exists".format(pdf_path))
    subprocess.run(["/usr/local/bin/img2pdf"] + files + ["-o", pdf_path])


def compress_pdf(identifier, pdf_dir):
    """Compress PDF via Ghostscript command line interface.

    Original PDF is replaced with compressed PDF.

    Args:
        identifier (str): Identifier of created PDF file.
        pdf_dir (str): Directory in which to save the PDF file.
    """
    source_pdf_path = "{}.pdf".format(os.path.join(pdf_dir, identifier))
    output_pdf_path = "{}_compressed.pdf".format(
        os.path.join(pdf_dir, identifier))
    subprocess.run(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS={}'.format('/screen'),
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile={}'.format(output_pdf_path),
                    source_pdf_path]
                   )
    os.remove(source_pdf_path)
    os.rename(output_pdf_path, source_pdf_path)


def ocr_pdf(identifier, pdf_dir):
    """Add OCR layer using ocrmypdf.

    Args:
        identifier (str): Identifier of created PDF file.
        pdf_dir (str): Directory in which to save the PDF file.
    """
    pdf_path = "{}.pdf".format(os.path.join(pdf_dir, identifier))
    subprocess.run(["/usr/local/bin/ocrmypdf",
                    pdf_path, pdf_path,
                    "--output-type", "pdf",
                    "--optimize", "0",
                    "--quiet"])
