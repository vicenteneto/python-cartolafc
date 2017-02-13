# -*- coding: utf-8 -*-
import json

import requests

from cartolafc.error import CartolaFCError
from cartolafc.models import Club, Highlight, Match, Round, Sponsor, Status


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

    def highlights(self):
        url = '%s/mercado/destaques' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Highlight.from_dict(highlight) for highlight in data]

    def sponsors(self):
        url = '%s/patrocinadores' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Sponsor.from_dict(sponsor) for sponsor in data]

    def rounds(self):
        url = '%s/rodadas' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Round.from_dict(round_) for round_ in data]

    def matches(self):
        url = '%s/partidas' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Match.from_dict(match, data['clubes']) for match in data['partidas']]

    def clubs(self):
        url = '%s/clubes' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Club.from_dict(club) for club in data.values()]

    def _parse_and_check_cartolafc(self, json_data):
        """
        Try and parse the JSON returned from Cartola FC API and return an empty dictionary if there is any error.
        This is a purely defensive check because during some Cartola FC API network outages it can return an error page.
        """
        try:
            return json.loads(json_data)
        except ValueError:
            raise CartolaFCError('Unknown error: {0}'.format(json_data))
