# -*- coding: utf-8 -*-
import json

import requests

from cartolafc.error import CartolaFCError
from cartolafc.models import Club, Highlight, Match, Round, Scheme, Sponsor, Status, Team, TeamInfo


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

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        return [Match.from_dict(match, clubs=clubs) for match in data['partidas']]

    def clubs(self):
        url = '%s/clubes' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Club.from_dict(club) for club in data.values()]

    def schemes(self):
        url = '%s/esquemas' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Scheme.from_dict(scheme) for scheme in data]

    def search_team_info_by_name(self, name):
        url = '%s/times?q=%s' % (self.base_url, name)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [TeamInfo.from_dict(team_info) for team_info in data]

    def get_team(self, slug):
        url = '%s/time/%s' % (self.base_url, slug)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return Team.from_dict(data)

    def get_team_by_round(self, slug, round_):
        url = '%s/time/%s/%s' % (self.base_url, slug, round_)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return Team.from_dict(data)

    def _parse_and_check_cartolafc(self, json_data):
        """
        Try and parse the JSON returned from Cartola FC API and return an empty dictionary if there is any error.
        This is a purely defensive check because during some Cartola FC API network outages it can return an error page.
        """
        try:
            data = json.loads(json_data)
            if 'mensagem' in data:
                raise CartolaFCError(data['mensagem'])
            return data
        except ValueError:
            raise CartolaFCError('Unknown error: {0}'.format(json_data))
