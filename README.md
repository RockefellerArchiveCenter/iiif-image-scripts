# iiif-image-scripts
Repository for the RAC's iiif imaging scripts (derivative and manifest creation)

## `tif_to_jp2.py`

This script reads through tif files in a directory and uses OpenJPEG to convert them to jp2 files. After converting each file it will push it to an AWS S3 bucket.

### Setup

This script requires a `local_settings.cfg` file with the following sections and keys.

- `[S3]`
  - `bucketname` (the name of the S3 bucket you are pushing data to)

This scrip requires two environment variables to run correctly and push files to S3. Get this information from your AWS console.

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Requires

This script requires the following architecture and Python libraries to function correctly.

- Python3
- Boto3
- Pillow

Additionally, this script requires the following to be installed on your system.
- [OpenJPEG](https://github.com/uclouvain/openjpeg/blob/master/INSTALL.md)
  - You may have to install the libtiff library on your system depending on your environment.

### Usage

The script takes two arguments: an input directory and an output directory. The first is the directory containing your original tif files, and the second will be where the program saves your jp2 files.

`python3 tiff_to_jp2.py /path/to/tif/files/ /path/to/output/directory/`

#### Default Settings

The following default options for OpenJPEG have been set:

- Compression ration of `1.5`
- Precinct size: `[256,256]` for first two layers and then `[128,128]` for all others
- Code block size of `[64,64]`
- Progression order of `RPCL`

#### Logging

The script will make a logfile named `derivative_log` in the same directory you are running it in.

## `create_manifest.py`

Creates IIIF presentation manifests based on unique ArchivcesSpace refids in an image directory. All files starting with the same ref_id will be added to the manifest as image annotations.

Uses the `IIIF-Prezi` manifest factory to make Presentatino API 2-compliant manifest files.

All manifest files will be pushed to an S3 bucket in the `/manifests/` directory after creation.

### Setup

This script requires a `local_settings.cfg` file with the following sections and keys.

- `[ArchivesSpace]`
  - `baseurl` (the url, including backend port for your ArchivesSpace instance)
  - `username` (an ArchivesSpace username)
  - `password` (an ArchivesSpace password)
- `[ImageServer]`
  - `imageurl` (the url for your image server that will be included in the manifest)
- `[S3]`
  - `bucketname` (the name of the S3 bucket you are pushing data to)

### Requires

This script requires the following architecture and Python libraries to function correctly.

  - Python3
  - ArchivesSnake
  - Boto3
  - IIIF-Prezi
  - Pillow

### Usage

The script takes two arguments: an input directory and an output directory. The first is the directory containing your source images that will be served on your image server, and the second will be where the program saves your manifest files before pushing them to S3.

`python3 create_manifest.py /path/to/source/files/ /path/to/output/manifests/`

#### Logging

The script will make a logfile named `manifest_log` in the same directory you are running it in.
