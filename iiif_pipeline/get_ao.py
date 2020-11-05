import logging

from asnake import utils
from asnake.aspace import ASpace
from configparser import ConfigParser

class ArchivesSpaceClient:
    def __init__(self):
            self.config = ConfigParser()
            self.config.read("local_settings.cfg")
            self.client = ASpace(baseurl=self.config.get("ArchivesSpace", "baseurl"),
                            username=self.config.get("ArchivesSpace", "username"),
                            password=self.config.get("ArchivesSpace", "password"),
                            repository=self.config.get("ArchivesSpace", "repository")).client

    def get_object(self, ref_id):
        """Gets archival object title and date from an ArchivesSpace refid.

        Args:
            ident (str): an ArchivesSpace refid.
        Returns:
            obj (dict): A dictionary representation of an archival object from ArchivesSpace.
        """
        results = self.client.get(
            'repositories/{}/find_by_id/archival_objects?ref_id[]={}'.format(
                self.config.get("ArchivesSpace", "repository"), ref_id)).json()
        if not results.get("archival_objects"):
            raise Exception("Could not find an ArchivesSpace object matching refid: {}".format(ref_id))
        else:
            obj_uri = results["archival_objects"][0]["ref"]
            obj = self.client.get(obj_uri).json()
            if not obj.get("dates"):
                obj["dates"] = utils.find_closest_value(obj, 'dates', self.client)
            return self.format_data(obj)

    def format_data(self, data):
        """Parses ArchivesSpace data.

        Args:
            data (dict): ArchivesSpace data.
        Returns:
            parsed (dict): Parsed data, with only required fields present.
        """
        title = data.get("title", data.get("display_string")).title()
        dates = ", ".join([utils.get_date_display(d, self.client) for d in data.get("dates", [])])
        return {"title": title, "dates": dates}
