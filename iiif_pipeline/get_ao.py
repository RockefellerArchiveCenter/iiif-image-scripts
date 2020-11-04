import logging

from asnake import utils
from asnake.aspace import ASpace
from configparser import ConfigParser

class GetObject:
    def __init__(self):
            self.config = ConfigParser()
            self.config.read("local_settings.cfg")
            self.client = ASpace(baseurl=self.config.get("ArchivesSpace", "baseurl"),
                            username=self.config.get("ArchivesSpace", "username"),
                            password=self.config.get("ArchivesSpace", "password"),
                            repository=self.config.get("ArchivesSpace", "repository")).client

    def run(self, ident):
        """Gets archival object title and date from an ArchivesSpace refid.

        Args:
            ident (str): an ArchivesSpace refid.
        Returns:
            ao (dict): A dictionary representation of an archival object from ArchivesSpace.
                Empty if no matching object is found.
            title (str): string representation of the closest title to the archival object.
            date (str): string representation of the closest date to the archival object.
        """
        title, date = '', ''
        ao = self.get_ao(ident)
        if ao:
            title, date = self.get_title_date(ao)
            return ao, title, date
        else:
            ao = {}
            return ao, title, date

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
