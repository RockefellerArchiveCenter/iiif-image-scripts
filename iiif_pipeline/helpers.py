from os import listdir
from os.path import isfile, join


def matching_files(directory, prefix=None, skip=False, prepend=False):
    """Get a list of files that start with a specific prefix, optionally removing
    any files that end in `_001`.

    Args:
        directory (str): The directory containing files.
        prefix (str): A prefix to match filenames against.
        skip (bool): Flag indicating if files ending with `_001` should be removed.
        prepend (bool): Add the directory to the filepaths returned
    Returns:
        files (lst): a list of files that matched the identifier.
    """
    files = sorted([f for f in listdir(directory) if (isfile(join(directory, f)) and not f.startswith("."))])
    if prefix:
        files = sorted([f for f in files if f.startswith(prefix)])
    if skip:
        for file in files:
            if file.split('.')[0].endswith('_001'):
                files.remove(file)
    return [join(directory, f) for f in files] if prepend else files
