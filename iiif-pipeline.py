import argparse
import logging
import os
import shortuuid
from configparser import ConfigParser

from iiif_pipeline.pipeline import IIIFPipeline


def main():
    parser = argparse.ArgumentParser(description="Generates JPEG2000 images from TIF files based on input and output directories")
    parser.add_argument("source_directory", help="A directory containing subdirectories - named using ref ids - for archival objects")
    parser.add_argument("--skip", help="Skips files ending in `_001` during derivative creation.")
    args = parser.parse_args()
    IIIFPipeline().run(args.source_directory, args.skip)

if __name__ == "__main__":
    main()
