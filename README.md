# IIIF Pipeline
A pipeline to create image derivatives and IIIF Manifests.

## Quick start

The Dockerfile included in this repository will allow you to run this library
without installing dependencies locally.

First, copy the example config file ([local_settings.cfg.example](local_settings.cfg.example))
and create a new file named `local_settings.cfg`.

Then build the image:

    $ docker build . -t iiif-pipeline

You can then run the pipeline, mounting any local directories you need access to.
For example, the command above will mount `/local_files/` on your local machine
to `/source_files/` in the running container and then execute `iiif_pipeline.py`,
using `/tmp` in the container as a destination directory:

    $ docker run -v /local_files:/source_files iiif-pipeline python iiif-pipeline.py /source_files /tmp


## Requirements

The entire suite has the following system dependencies:
- Python 3 (tested on Python 3.6)
- OpenJPEG
- Ghostscript

It also requires these Python libraries in order to work correctly.
- [ArchivesSnake](https://pypi.org/project/ArchivesSnake/)
- [boto3](https://pypi.org/project/boto3/)
- [iiif-prezi](https://pypi.org/project/iiif-prezi/)
- [img2pdf](https://pypi.org/project/img2pdf/)
- [Pillow](https://pypi.org/project/Pillow/)
- [python-magic](https://pypi.org/project/python-magic/)
- [shortuuid](https://pypi.org/project/shortuuid/)


## Usage

The IIIF Pipeline expects to be pointed at a directory containing subdirectories
(named by ArchivesSpace ref ids) for archival object components, each of which
contains a subdirectory named `master` containing original TIFF files:

    source/
      ⌙ c9c9d379257645debc1ceb48fea9cd52/
        ⌙ master/
          ⌙ c9c9d379257645debc1ceb48fea9cd52_001.tiff
          ⌙ c9c9d379257645debc1ceb48fea9cd52_002.tiff
          ⌙ c9c9d379257645debc1ceb48fea9cd52_003.tiff
          ...
      ⌙ bbfa5599325b444a9f182401b1f31fc5
        ⌙ master/
          ⌙ bbfa5599325b444a9f182401b1f31fc5_001.tiff
          ⌙ bbfa5599325b444a9f182401b1f31fc5_002.tiff
          ⌙ bbfa5599325b444a9f182401b1f31fc5_003.tiff


This library is designed to be executed from the command line:

    $ iiif-pipeline.py source_directory target_directory [--skip] [--replace]

where `source_directory` is a path to the directory described above and
`target_directory` is a path at which the derivative and manifest files will be
created before they are uploaded. The user running the script must own the
`target_directory`. The optional `--skip` flag will skip image files with
filenames ending in `_001`, and the optional `--replace` flag will replace
existing files.


## Configuration

This script requires a `local_settings.cfg` file. For an example of the sections
and keys required, see [local_settings.cfg.example](local_settings.cfg.example)
in this repository


## Tests

This library comes with unit tests. To quickly run tests, along with linters,
run `tox` from the root of the project.
