import os

from iiif_prezi.factory import ManifestFactory
from PIL import Image

THUMBNAIL_HEIGHT = 200
THUMBNAIL_WIDTH = 200

class ManifestMaker:

    def __init__(self, server_url, manifest_dir):
        self.server_url = server_url
        self.manifest_dir = manifest_dir
        self.resource_url = "{}/iiif/2/".format(server_url)
        self.fac = ManifestFactory()
        self.fac.set_base_prezi_dir(manifest_dir)
        self.fac.set_base_prezi_uri("{}/manifests/".format(self.server_url))
        self.fac.set_base_image_uri(self.resource_url)
        self.fac.set_debug("error")

    def create_manifest(self, files, image_dir, identifier, obj_data):
        """Method that runs the other methods to build a manifest file and populate
        it with information.

        Args:
            files (list): Files to iterate over
            image_dir (str): Path to directory containing derivative image files.
            identifier (str): A unique identifier.
            obj_data (dict): Data about the archival object.
        """
        page_number = 1
        manifest = self.fac.manifest(ident=identifier, label=obj_data["title"])
        manifest.set_metadata({"Date": obj_data["dates"]})
        manifest.thumbnail = self.set_thumbnail(os.path.splitext(files[0])[0])
        sequence = manifest.sequence(ident="{}.json".format(identifier))
        for file in files:
            page_ref = os.path.splitext(file)[0]
            width, height = self.get_image_info(image_dir, file)
            canvas = sequence.canvas(ident=page_ref, label="Page {}".format(str(page_number)))
            canvas.set_hw(height, width)
            annotation = canvas.annotation(ident=page_ref)
            img = annotation.image(ident="{}/full/max/0/default.jpg".format(page_ref))
            self.set_image_data(img, height, width, page_ref)
            canvas.thumbnail = self.set_thumbnail(page_ref)
            page_number += 1
        manifest.toFile(compact=False)
        manifest_file = '{}{}.json'.format(self.manifest_dir, identifier)

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

    def set_image_data(self, img, height, width, ref):
        """Sets the image height and width. Creates the image object.

        Args:
            img (object): An iiif-prezi Image object.
            height (int): Pixel height of the image.
            width (int): Pixel width of the image.
            ref (string): Reference identifier for the file, including page in filename.

        Returns:
            img (object): A iiif_prezi image object with data.
        """
        img.height = height
        img.width = width
        img.format = "image/jpeg"
        img.service = self.set_service(ref)
        return img

    def set_thumbnail(self, identifier):
        """Creates a IIIF-compatible thumbnail.

        Args:
            identifier (str): A string identifier to use as the thumbnail id.
        Returns:
            thumbnail (object): An iiif_prezi Image object.
        """
        thumbnail = self.fac.image(ident="{}/square/{},/0/default.jpg".format(identifier, THUMBNAIL_WIDTH))
        self.set_image_data(thumbnail, THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH, identifier)
        return thumbnail

    def set_service(self, identifier):
        return self.fac.service(
            ident="{}{}".format(self.resource_url, identifier),
            context="http://iiif.io/api/image/2/context.json",
            profile="http://iiif.io/api/image/2/level2.json")
