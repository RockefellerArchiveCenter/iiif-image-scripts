import logging
import os

from configparser import ConfigParser
from iiif_prezi.factory import ManifestFactory
from pathlib import Path
from PIL import Image

class ManifestMaker:

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.fac = ManifestFactory()
        self.server_url = self.config.get("ImageServer", "imageurl")
        self.resource_url = "{}/iiif/2/".format(self.server_url)

    def run(self, image_dir, manifest_dir, uuid, title, date):
        """Method that runs the other methods to build a manifest file and populate
        it with information.

        Args:
            image_dir (str): Path to directory containing derivative image files.
            manifest_dir (str): Path to directory to save manifest files.
            uuid (str): A unique identifier.
            title (str): String title of the archival object the manifest refers to.
            date (str): String date of the archival object the manifest refers to.
        """

        self.fac.set_debug("error")
        self.fac.set_base_prezi_dir(manifest_dir)
        self.fac.set_base_prezi_uri("{}/manifests/".format(self.server_url))
        self.fac.set_base_image_uri("{}/".format(self.resource_url))

        page_number = 0
        manifest = self.set_manifest_data(uuid, title, date)
        seq = manifest.sequence(ident="{}.json".format(uuid))
        files = sorted(self.get_matching_files(uuid, image_dir))
        self.set_thumbnail(manifest, files[0].split('.')[0])
        for file in files:
            page_number = page_number + 1
            width, height = self.get_image_info(image_dir, file)
            page_ref = file[:-4]
            cvs = self.set_canvas_data(seq, page_ref, page_number, width, height)
            anno = cvs.annotation(ident=page_ref)
            self.set_image_data(height, width, page_ref, anno)
            self.set_thumbnail(cvs, page_ref, height=height, width=width)
        manifest.toFile(compact=False)
        manifest_file = '{}{}.json'.format(manifest_dir, uuid)
        logging.info("Created manifest {}.json".format(uuid))


    def set_manifest_data(self, identifier, title, date):
        """Sets the manifest title, date, and instantiates the manifest.

        Args:
            identifier (str): a unique identifier to use for the manifest identifier.
            title (str): string representation of the object's title.
            date (str): string representation of the object's date.
        Returns:
            manifest (dict): a JSON IIIF manifest
        """
        manifest_label = title.title()
        manifest = self.fac.manifest(ident=identifier, label=manifest_label)
        manifest.set_metadata({"Date": date})
        return manifest

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
        """
        with Image.open(os.path.join(image_dir, file)) as img:
            width, height = img.size
        return width, height

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
        img = annotation.image("{}/full/max/0/default.jpg".format(page_ref))
        img.height = height
        img.width = width
        img.format = "image/jpeg"
        img.service = self.set_service(page_ref)
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
        section.thumbnail = self.fac.image(ident="{}/square/200,/0/default.jpg".format(identifier))
        section.thumbnail.format = "image/jpeg"
        section.thumbnail.height = 200
        if not (height or width):
            section.thumbnail.width = 200
        else:
            section.thumbnail.width = int(width / (height / section.thumbnail.height))
        section.thumbnail.service = self.set_service(identifier)
        return section

    def set_service(self, identifier):
        service = self.fac.service(ident="{}{}".format(self.resource_url, identifier),
                                   context="http://iiif.io/api/image/2/context.json",
                                   profile="http://iiif.io/api/image/2/level2.json")
        return service
