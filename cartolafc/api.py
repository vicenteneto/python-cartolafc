# -*- coding: utf-8 -*-

import logging
import sys

import requests

from cartolafc.error import CartolaFCError, CartolaFCOverloadError
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
from cartolafc.util import convert_team_name_to_slug, parse_and_check_cartolafc

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

if sys.version_info < (2, 7, 9):
    requests.packages.urllib3.disable_warnings()


class Api(object):
    """
    A python interface into the Cartola FC API.
    """

    def __init__(self, attempts=1):
        self.base_url = 'https://api.cartolafc.globo.com'
        self.attempts = attempts if isinstance(attempts, int) and attempts > 0 else 1

    def status(self):
        """ status. """
        url = '%s/mercado/status' % (self.base_url,)
        data = self._request(url)

        return Status.from_dict(data)

    def market(self):
        """ market. """
        url = '%s/atletas/mercado' % (self.base_url,)
        data = self._request(url)

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        positions = {position['id']: Position.from_dict(position) for position in data['posicoes'].values()}
        status = {status['id']: status for status in data['status'].values()}
        return [Athlete.from_dict(athlete, clubs=clubs, positions=positions, status=status) for athlete
                in data['atletas']]

    def round_score(self):
        """ round_score. """
        url = '%s/atletas/pontuados' % (self.base_url,)

        if self.status().status_mercado == 'Mercado fechado':
            data = self._request(url)

            clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
            positions = {position['id']: Position.from_dict(position) for position in data['posicoes'].values()}

            return {athlete_id: AthleteScore.from_dict(athlete, clubs=clubs, positions=positions) for
                    athlete_id, athlete in data['atletas'].items()}

        raise CartolaFCError('A pontuação parcial só fica disponível com o mercado fechado.')

    def highlights(self):
        """ highlights. """
        url = '%s/mercado/destaques' % (self.base_url,)
        data = self._request(url)

        return [Highlight.from_dict(highlight) for highlight in data]

    def round_highlights(self):
        """ round_highlights. """
        url = '%s/pos-rodada/destaques' % (self.base_url,)
        data = self._request(url)

        return RoundHighlights.from_dict(data)

    def sponsors(self):
        """ sponsors. """
        url = '%s/patrocinadores' % (self.base_url,)
        data = self._request(url)

        return {sponsor_id: Sponsor.from_dict(sponsor) for sponsor_id, sponsor in data.items()}

    def rounds(self):
        """ rounds. """
        url = '%s/rodadas' % (self.base_url,)
        data = self._request(url)

        return [Round.from_dict(round_) for round_ in data]

    def matches(self):
        """ matches. """
        url = '%s/partidas' % (self.base_url,)
        data = self._request(url)

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        return [Match.from_dict(match, clubs=clubs) for match in data['partidas']]

    def clubs(self):
        """ clubs. """
        url = '%s/clubes' % (self.base_url,)
        data = self._request(url)

        return {club_id: Club.from_dict(club) for club_id, club in data.items()}

    def schemes(self):
        """ schemes. """
        url = '%s/esquemas' % (self.base_url,)
        data = self._request(url)

        return [Scheme.from_dict(scheme) for scheme in data]

    def search_team_info_by_name(self, name):
        """ search_team_info_by_name. """
        url = '%s/times?q=%s' % (self.base_url, name)
        data = self._request(url)

        return [TeamInfo.from_dict(team_info) for team_info in data]

    def get_team(self, name, is_slug=False):
        """ get_team. """
        slug = name if is_slug else convert_team_name_to_slug(name)
        url = '%s/time/slug/%s' % (self.base_url, slug)
        data = self._request(url)

        return Team.from_dict(data)

    def get_team_by_round(self, name, round_, is_slug=False):
        """ get_team_by_round. """
        slug = name if is_slug else convert_team_name_to_slug(name)
        url = '%s/time/slug/%s/%s' % (self.base_url, slug, round_)
        data = self._request(url)

        return Team.from_dict(data)

    def search_league_info_by_name(self, name):
        """ search_league_info_by_name. """
        url = '%s/ligas?q=%s' % (self.base_url, name)
        data = self._request(url)

        return [LeagueInfo.from_dict(league_info) for league_info in data]

    def _request(self, url):
        attempts = self.attempts
        while attempts:
            try:
                resp = requests.get(url)
                return parse_and_check_cartolafc(resp.content.decode('utf-8'))
            except CartolaFCOverloadError as error:
                attempts -= 1
                if not attempts:
                    raise error
