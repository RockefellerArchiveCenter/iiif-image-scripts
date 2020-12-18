from os import listdir, remove
from os.path import basename, isdir, isfile, join, splitext
from shutil import rmtree


def matching_files(directory, prefix=None, suffix=None,
                   skip=False, prepend=False):
    """Get a list of files that start with a specific prefix, optionally removing
    any files that end in `_001`.

    Args:
        directory (str): The directory containing files.
        prefix (str): A prefix to match filenames against.
        suffix (str): A suffix (file extension) to match filenames against.
        skip (bool): Flag indicating if files ending with `_001` should be removed.
        prepend (bool): Add the directory to the filepaths returned
    Returns:
        files (lst): a list of files that matched the identifier.
    """
    files = sorted([f for f in listdir(directory) if (
        isfile(join(directory, f)) and not f.startswith((".", "Thumbs")))])
    if prefix:
        files = sorted([f for f in files if f.startswith(prefix)])
    if suffix:
        files = sorted([f for f in files if f.endswith(suffix)])
    if skip:
        for file in files:
            if file.split('.')[0].endswith('_001'):
                files.remove(file)
    return [join(directory, f) for f in files] if prepend else files


def refid_dirs(root_dir, reserved_dirs=[]):
    """Get full paths for ref id directories.

    Args:
        root_dir (str): Path to the root directory to be traversed.
        reserved_dirs (list): Paths of directories to be skipped.
    """
    return [join(root_dir, d) for d in listdir(root_dir) if (
        isdir(join(root_dir, d)) and join(root_dir, d) not in reserved_dirs)]


def cleanup_files(identifier, directories):
    """Removes files which start with an identifier from a list of directories.

    Args:
        identifier (str): Identifier which prefixes the files to be removed.
        reserved_dirs (list): Paths of directories to be cleaned.
    """
    for directory in directories:
        for f in matching_files(directory, prefix=identifier, prepend=True):
            remove(f)


def cleanup_dir(dir_path):
    """Removes a directory.

    Args:
        dir_path (str): path of the directory to be removed.
    """
    rmtree(dir_path)


def get_page_number(filepath):
    """Parses a page number from a filename."""
    filename, _ = splitext(basename(filepath))
    trimmed = filename.rstrip("_me").rstrip("_se")
    return trimmed.split("_")[-1]
