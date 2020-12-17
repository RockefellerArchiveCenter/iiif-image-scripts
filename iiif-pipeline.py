import argparse

from iiif_pipeline.pipeline import IIIFPipeline


def main():
    parser = argparse.ArgumentParser(
        description="Generates JPEG2000 images from TIF files based on input and output directories.")
    parser.add_argument(
        "source_directory",
        help="A directory containing subdirectories (named using ref ids) for archival objects.")
    parser.add_argument(
        "target_directory",
        help="A directory in which to create generated image derivatives and manifests.")
    parser.add_argument(
        "--skip",
        action="store_true",
        help="Skip files ending in `_001` during derivative creation.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing files.")
    parser.add_argument(
        "--cleanup_source",
        action="store_true",
        help="Delete source files if they are successfully processed.")
    args = parser.parse_args()
    IIIFPipeline().run(
        args.source_directory,
        args.target_directory,
        args.skip,
        args.replace,
        args.cleanup_source)


if __name__ == "__main__":
    main()
