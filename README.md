# iiif-image-scripts
Repository for the RAC's iiif imaging scripts (derivative and manifest creation)

## `main.py`

Main wrapper script for running the four scripts together. Point it at a directory containing multiple other directories of tiff image files. Will create JP2 copies from those files, a manifest file, and upload JP2 files and manifests to an AWS bucket. Assumes each directory is an ArchivesSpace refid.

### Requires

- Python3
- Shortuuid

### Usage

`python3 main.py /path/to/tif/files/ /path/to/tiff/files/`

or

`python3 main.py /path/to/tif/files/ /path/to/tiff/files/ --skip True` to skip image files ending in `_001`.

Local usage skips these files sometimes because they are scanning targets, and not part of the object.

### Logging

This script will make a log file named `iiif_generation.log` containing information about derivative creation, manifest creation, and AWS upload.

## `aws_upload.py`

Uploads files to an AWS bucket.

### Requires

This script requires the following libraries to function correctly.

- Boto3
- Python Magic

### Setup

This script requires a `local_settings.cfg` file with the following sections and keys.

- `[S3]`
  - `bucketname` (the name of your S3 bucket)

You will also either need to create sections/keys or set the following environment variables specific to your S3 bucket:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## `create_derivatives.py`

This script reads through tif files in a directory and uses OpenJPEG to convert them to jp2 files.

### Requires

This script requires the following libraries to function correctly.

- Pillow

Additionally, this script requires the following to be installed on your system.
- [OpenJPEG](https://github.com/uclouvain/openjpeg/blob/master/INSTALL.md)
  - You may have to install the libtiff library on your system depending on your environment.


### Default Settings

The following default options for OpenJPEG have been set:

- Compression ration of `1.5`
- Precinct size: `[256,256]` for first two layers and then `[128,128]` for all others
- Code block size of `[64,64]`
- Progression order of `RPCL`

## `create_manifest.py`

Creates IIIF presentation manifests based on unique ArchivesSpace refids in an image directory. All files starting with the same identifier will be added to the manifest as image annotations.

Uses the `IIIF-Prezi` manifest factory to make Presentation API 2.1-compliant manifest files.

### Requires

This script requires the following libraries to function correctly.

  - Python3
  - Boto3
  - IIIF-Prezi
  - Pillow

### Setup

This script requires a `local_settings.cfg` file with the following sections and keys.

- `[ImageServer]`
  - `imageurl` (the url for your image server that will be included in the manifest)

Update any hardcoded URLs to point to the proper image and manifest storage locations. You may have to update the following lines.

  - `fac.set_base_prezi_uri("{}/manifests/".format(self.imageurl))`
  - `fac.set_base_image_uri("{}/iiif/2/".format(self.imageurl))`
  - `img = annotation.image("/{}/full/max/0/default.jpg".format(page_ref))`
  - `section.thumbnail = fac.image(ident="/{}/square/200,/0/default.jpg".format(identifier))`

## `get_ao.py`

Checks if an archival object exists in ArchivesSpace using `find_by_id`, and if it does, returns the closest value of the object's title and date.

### Requires

This script requires the following libraries to function correctly.

- ArchivesSnake

### Setup

This script requires a `local_settings.cfg` file with the following sections and keys.

- `[ArchivesSpace]`
  - [`baseurl`] (backend url for your ArchivesSpace instance)
  - [`repository`] (ArchivesSpace repository ID)
  - [`username`] (ArchivesSpace username)
  - [`password`] (ArchivesSpace password)

## `make_pdf.py`

Merges files with matching identifiers into a single pdf.

### Requires

This script requires the following libraries to function correctly.

- img2pdf
