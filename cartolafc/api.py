import json

import requests

from cartolafc.error import CartolaFCError
from cartolafc.models import Status


class Api(object):
    """
    A python interface into the Cartola FC API.
    """

    def __init__(self):
        self.base_url = 'https://api.cartolafc.globo.com'

    def status(self):
        url = '%s/mercado/status' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return Status.from_dict(data)

    def _parse_and_check_cartolafc(self, json_data):
        """
        Try and parse the JSON returned from Cartola FC API and return an empty dictionary if there is any error.
        This is a purely defensive check because during some Cartola FC API network outages it can return an error page.
        """
        try:
            return json.loads(json_data)
        except ValueError:
            raise CartolaFCError('Unknown error: {0}'.format(json_data))
