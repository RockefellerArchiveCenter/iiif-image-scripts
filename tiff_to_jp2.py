import argparse
import os

from pathlib import Path

PROGRESSION_ORDER_CHOICES = ["LRCP","RLCP","RPCL","PCRL","CPRL""]

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory", help="The full directory path of the original image files to create derivatives from (ex. /Documents/originals/)")
    parser.add_argument("output_directory", help="The full directory path to store derivative files in (ex. /Documents/derivatives/)")
    parser.add_argument("compression_ratio", default=1, help="Compression ratio values (ex. 1.5, 2, 2.2)")
    parser.add_argument("resolution_number", default=6, help="Number of resolutions in whole numbers (ex. 4, 6, 7)")
    parser.add_argument("precinct_size", help="Precinct size. Values specified must be power of 2. (ex. [256,256]) or [256,256],[128,128], etc.")
    parser.add_argument("block_size", default=64,64, help="Code-block size. Maximum and default is 64x64. Nothing smaller than 4. (ex. 64,64 or 32,32)")
    parser.add_argument("progression_order", choices=PROGRESSION_ORDER_CHOICES, default="RPCL", help="Progression order. The five progression orders are : LRCP, RLCP, RPCL, PCRL and CPRL")
    return parser

def main():
     """Main function, which is run when this script is executed"""
    start_time = time.time()
    parser = get_parser()
    args = parser.parse_args()
    for file in os.listdir(args.input_directory):
        input_file = "{}{}".format(args.input_directory, file)
        fname = file.split(".")[0]
        output_file = "{}{}.jp2".format(args.output_directory, fname)
        os.system("opj_compress -i {} -o {} -r {} -n {} -c '{}' -b '{}' -p {} -SOP".format(
            input_file, output_file, args.compression_ratio, args.resolution_number, args.precinct_size,
            args.block_size, args.progression_order))

if __name__ == "__main__":
    main()
