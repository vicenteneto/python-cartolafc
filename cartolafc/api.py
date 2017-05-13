# -*- coding: utf-8 -*-
import json
import re
from collections import OrderedDict

import requests

from cartolafc.error import CartolaFCError
from cartolafc.models import (
    Athlete,
    AthleteScore,
    Club,
    Highlight,
    LeagueInfo,
    Match,
    Position,
    Round,
    RoundHighlights,
    Scheme,
    Sponsor,
    Status,
    Team,
    TeamInfo
)


class Api(object):
    """
    A python interface into the Cartola FC API.
    """

    def __init__(self):
        self.base_url = 'https://api.cartolafc.globo.com'

    def status(self):
        """ status. """
        url = '%s/mercado/status' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return Status.from_dict(data)

    def market(self):
        """ market. """
        url = '%s/atletas/mercado' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        positions = {position['id']: Position.from_dict(position) for position in data['posicoes'].values()}
        status = {status['id']: status for status in data['status'].values()}
        return [Athlete.from_dict(athlete, clubs=clubs, positions=positions, status=status) for athlete
                in data['atletas']]

    def round_score(self):
        """ round_score. """
        url = '%s/atletas/pontuados' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        positions = {position['id']: Position.from_dict(position) for position in data['posicoes'].values()}

        return [AthleteScore.from_dict(athlete, clubs=clubs, positions=positions) for athlete in
                OrderedDict(sorted(data['atletas'].items())).values()]

    def highlights(self):
        """ highlights. """
        url = '%s/mercado/destaques' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Highlight.from_dict(highlight) for highlight in data]

    def round_highlights(self):
        """ round_highlights. """
        url = '%s/pos-rodada/destaques' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return RoundHighlights.from_dict(data)

    def sponsors(self):
        """ sponsors. """
        url = '%s/patrocinadores' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Sponsor.from_dict(sponsor) for sponsor in data.values()]

    def rounds(self):
        """ rounds. """
        url = '%s/rodadas' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Round.from_dict(round_) for round_ in data]

    def matches(self):
        """ matches. """
        url = '%s/partidas' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        return [Match.from_dict(match, clubs=clubs) for match in data['partidas']]

    def clubs(self):
        """ clubs. """
        url = '%s/clubes' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Club.from_dict(club) for club in OrderedDict(sorted(data.items())).values()]

    def schemes(self):
        """ schemes. """
        url = '%s/esquemas' % (self.base_url,)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [Scheme.from_dict(scheme) for scheme in data]

    def search_team_info_by_name(self, name):
        """ search_team_info_by_name. """
        url = '%s/times?q=%s' % (self.base_url, name)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [TeamInfo.from_dict(team_info) for team_info in data]

    def get_team(self, name, is_slug=False):
        """ get_team. """
        slug = name if is_slug else self._convert_team_name_to_slug(name)
        url = '%s/time/slug/%s' % (self.base_url, slug)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return Team.from_dict(data)

    def get_team_by_round(self, name, round_, is_slug=False):
        """ get_team_by_round. """
        slug = name if is_slug else self._convert_team_name_to_slug(name)
        url = '%s/time/slug/%s/%s' % (self.base_url, slug, round_)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return Team.from_dict(data)

    def search_league_info_by_name(self, name):
        """ search_league_info_by_name. """
        url = '%s/ligas?q=%s' % (self.base_url, name)

        resp = requests.get(url)
        data = self._parse_and_check_cartolafc(resp.content.decode('utf-8'))

        return [LeagueInfo.from_dict(league_info) for league_info in data]

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

    def _convert_team_name_to_slug(self, name):
        return re.sub(r'[^a-zA-Z]', '-', name)
