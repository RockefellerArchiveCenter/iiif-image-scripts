import logging
import os

from asnake import utils
from asnake.aspace import ASpace
from configparser import ConfigParser
from iiif_prezi.factory import ManifestFactory
from pathlib import Path
from PIL import Image

class ManifestMaker:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.client = ASpace(baseurl=self.config.get("ArchivesSpace", "baseurl"),
                        username=self.config.get("ArchivesSpace", "username"),
                        password=self.config.get("ArchivesSpace", "password"),
                        repository=self.config.get("ArchivesSpace", "repository")).client

        self.fac = ManifestFactory()

    def run(self, image_dir, manifest_dir):
        """Method that runs the other methods to build a manifest file and populate
        it with information.

        Args:
            image_dir (str): Path to directory containing derivative image files.
            manifest_dir (str): Path to directory to save manifest files.
        """
        imageurl=self.config.get("ImageServer", "imageurl")

        self.fac.set_debug("error")
        self.fac.set_base_prezi_dir(manifest_dir)
        self.fac.set_base_prezi_uri("{}/manifests/".format(imageurl))
        self.fac.set_base_image_uri("{}/iiif/2/images/".format(imageurl))

        identifiers = self.get_identifiers(image_dir)
        for ident in identifiers:
            page_number = 0
            ao = self.get_ao(ident)
            if ao:
                manifest = self.set_manifest_data(ident, ao)
                seq = manifest.sequence(ident="{}.json".format(ident))
                files = sorted(self.get_matching_files(ident, image_dir))
                self.set_thumbnail(manifest, files[0].split('.')[0])
                for file in files:
                    """Gets a refid from a file, and then creates a canvas and annotations
                    based on image dimensions and base prezi directories.
                    """
                    page_ref = file[:-4]
                    page_number = page_number + 1
                    width, height, path = self.get_image_info(image_dir, file)
                    cvs = self.set_canvas_data(seq, page_ref, page_number, width, height)
                    anno = cvs.annotation(ident=page_ref)
                    self.set_image_data(height, width, page_ref, anno)
                    self.set_thumbnail(cvs, page_ref, height=height, width=width)
                manifest.toFile(compact=False)
                manifest_file = '{}{}.json'.format(manifest_dir, ident)
                logging.info("Created manifest {}.json".format(ident))

    def get_identifiers(self, image_dir):
        """Get a list of unique identifiers from files in a directory.

        Args:
            image_dir (str): a string representation of the directory containing image files.
        Returns:
            identifiers (lst): a list of unique identifiers.
        """
        identifiers = [file.split('_')[0] for file in os.listdir(image_dir)]
        return list(set(identifiers))

    def get_matching_files(self, ident, image_dir):
        """Get a list of files that start with a specific refid.

        Args:
            ident (str): a string representation of an ArchivesSpace refid.
            image_dir (str): a string representation of the directory containing image files.
        Returns:
            files (lst): a list of files that matched the identifier.
        """
        files = [file for file in os.listdir(image_dir) if file.startswith(ident)]
        return files

    def get_dimensions(self, file):
        """Get the pixel height and width of an image file.

        Args:
            file (str): an image filename
        Returns:
            image_width (int): pixel width of an image
            image_height (int): pixel height of an image
        """
        with Image.open(file) as img:
            image_width, image_height = img.size
            return image_width, image_height

    def get_ao(self, refid):
        """Gets a JSON representation of an archival object.

        Args:
            refid (str): an ArchivesSpace refid
        Returns:
            ao (dict): a JSON representation of an archival object
        """
        refs = self.client.get('repositories/2/find_by_id/archival_objects?ref_id[]={}'.format(refid)).json()
        if not refs.get("archival_objects"):
            logging.error("Could not find an ArchivesSpace object matching refid: {}".format(refid))
            return False
        else:
            ao_id = refs.get("archival_objects")[0].get("ref")
            ao = self.client.get(ao_id).json()
            return ao

    def get_title_date(self, archival_object):
        """Gets the closest title and date to an archival object by looking through its
        ancestors.

        Args:
            archival_object (dict): a JSON representation of an archival object
        Returns:
            title (str): A string representation of of a title.
            date (str): A string representation of a date expression.
        """
        ao_title = utils.find_closest_value(archival_object, 'title', self.client)
        ao_date = utils.find_closest_value(archival_object, 'dates', self.client)
        expressions = [date.get('expression') for date in ao_date]
        ao_date = ', '.join([str(expression) for expression in expressions])
        return ao_title, ao_date

    def set_manifest_data(self, identifier, archival_object):
        """Sets the manifest title, date, and instantiates the manifest.

        Args:
            identifier (str): an ArchivesSpace refid to use for the manifest identifier.
            archival_object (dict): A JSON representation of an archival object.

        Returns:
            manifest (dict): a JSON IIIF manifest
        """
        title, date = self.get_title_date(archival_object)
        manifest_label = title.title()
        manifest = self.fac.manifest(ident=identifier, label=manifest_label)
        manifest.set_metadata({"Date": date})
        return manifest

    def set_canvas_data(self, sequence, ref, page_number, width, height):
        """Sets canvas information.

        Args:
            sequence (object): A iiif_prezi factory sequence object.
            ref (str): string representation of the filename without the extension.
            page_number (int): Page number for the canvas.
            width (int): Pixel width of the canvas.
            height (int): Pixel height of the canvas

        Returns:
            cvs (object): A iiif_prezi factory canvas object.
        """
        canvas_label = str(page_number)
        cvs = sequence.canvas(ident=ref, label="Page {}".format(canvas_label))
        cvs.set_hw(height, width)
        return cvs

    def get_image_info(self, image_dir, file):
        """Gets information about the image file.

        Args:
            image_dir (str): path to the directory containing the image file
            file (str): filename of the image file

        Returns:
            width (int): Pixel width of the image file
            height (int): Pixel height of the image file
            path (str): Concatenated path to the source image file.
        """
        path = os.path.join(image_dir, file)
        width, height = self.get_dimensions(path)
        return width, height, path

    def set_image_data(self, height, width, page_ref, annotation):
        """Sets the image height and width. Creates the image object.

        Args:
            height (int): Pixel height of the image
            width (int): Pixel width of the image
            page_ref (string): Reference identifier for the file, including page in filename
            annotation (object): A iiif_prezi annotation object

        Returns:
            img (object): A iiif_prezi image object with data.
        """
        img = annotation.image("/{}/full/max/0/default.jpg".format(page_ref))
        img.height = height
        img.width = width
        img.format = "image/jpeg"
        return img

    def set_thumbnail(self, section, identifier, height=None, width=None):
        """Creates a iiif-compatible thumbnail.

        Args:
            section (object): A iiif_prezi object to make the thumbnail in.
            identifier (str): A string identifier to use as the thumbnail id.
            height (int): Height in pixels of the original image.
            width (int): Width in pixels of the original image.

        Returns:
            section (object): An updated iiif_prezi object with thumbnail section.
        """
        section.thumbnail = self.fac.image(ident="/{}/square/200,/0/default.jpg".format(identifier))
        section.thumbnail.format = "image/jpeg"
        section.thumbnail.height = 200
        if not (height or width):
            section.thumbnail.width = 200
        else:
            section.thumbnail.width = int(width / (height / section.thumbnail.height))
        return section
