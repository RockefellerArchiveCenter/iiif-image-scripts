import argparse
import math
import mimetypes
import os

from pathlib import Path
from PIL import Image
from PIL.TiffTags import TAGS


PROGRESSION_ORDER_CHOICES = ["LRCP","RLCP","RPCL","PCRL","CPRL""]

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
    parser.add_argument("output_directory", help="The full directory path to store derivative files in (ex. /Documents/derivatives/)")
    parser.add_argument("compression_ratio", default=1, help="Compression ratio values (ex. 1.5, 2, 2.2)")
    parser.add_argument("precinct_size", help="Precinct size. Values specified must be power of 2. (ex. [256,256]) or [256,256],[128,128], etc.")
    parser.add_argument("block_size", default=64,64, help="Code-block size. Maximum and default is 64x64. Nothing smaller than 4. (ex. 64,64 or 32,32)")
    parser.add_argument("progression_order", choices=PROGRESSION_ORDER_CHOICES, default="RPCL", help="Progression order. The five progression orders are : LRCP, RLCP, RPCL, PCRL and CPRL")
    return parser

def get_dimensions(file):
    with Image.open(file) as img:
        for x in img.tag[256]:
            image_width = x
        for y in img.tag[257]:
            image_height = y
        return image_width, image_height

def calculate_layers(width, height):
    pixdem = max(width, height)
    layers = math.ceil((math.log(pixdem) / math.log(2)) - ((math.log(96) / math.log(2)))) + 1

def is_tiff(file):
    type = mimetypes.MimeTypes().guess_type(file)[0]
    if type = "image/tiff":
        return True
    else:
        return False

def make_filenames(start_directory, end_directory):
    original_file = "{}{}".format(args.start_directory, file)
    fname = file.split(".")[0]
    derivative_file = "{}{}.jp2".format(args.end_directory, fname)
    return original_file, derivative_file

def main():
     """Main function, which is run when this script is executed"""
    parser = get_parser()
    args = parser.parse_args()
    for file in os.listdir(args.input_directory):
        make_filenames(input_directory, output_directory)
        if os.path.isfile(derivative_file):
            print("Derivative file already exists")
        else:
            if is_tiff(original_file):
                get_dimensions(original_file)
                layers = calculate_layers(image_width, image_height)
                os.system("opj_compress -i {} -o {} -r {} -n {} -c '{}' -b '{}' -p {} -SOP".format(
                    original_file, derivative_file, args.compression_ratio, layers, args.precinct_size,
                    args.block_size, args.progression_order))
            else:
                print("Not a valid tiff file")

if __name__ == "__main__":
    main()
