from abc import abstractmethod

from pydantic import BaseModel


class MiraklExportMapper(BaseModel):
    _identity_key = None

    def get_key(self):
        return getattr(self, self._identity_key, "")

    @abstractmethod
    def to_json(self):
        """
        :return: a dictionary with the correctly formatted headers
        as keys and the appropriate values to add to the export file
        """

    @classmethod
    def map_item(cls, mirakl_channel, product):
        """
        Build a mirakl record from an odoo record
        :param mirakl_channel: Mirakl channel on which the product is attached
        :param product: product to map
        :return: a pydantic object corresponding to the form expected by mirakl
        """

    @classmethod
    def get_file_header(cls):
        """
        :return: list corresponding to the header of the csv file
        to export to mirakl
        """
        return []

    @classmethod
    def get_additional_options(cls):
        """
        :return: depending on the data to export, the export file may be
        accompanied by options
        """
        return {}
