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
    Liga,
    Match,
    Position,
    Round,
    RoundHighlights,
    Scheme,
    Sponsor,
    Status,
    Team,
    TeamInfo,
    Time
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

    def __init__(self, email=None, password=None, as_json=False, attempts=1):
        self._base_url = 'https://api.cartolafc.globo.com'
        self._email = email
        self._password = password
        self._glb_id = None
        self._as_json = bool(as_json)
        self.attempts = attempts if isinstance(attempts, int) and attempts > 0 else 1

        if bool(email) != bool(password):
            raise CartolaFCError('E-mail ou senha ausente')
        elif all((email, password)):
            self.set_credentials(email, password)

    def set_credentials(self, email, password):
        self._email = email
        self._password = password
        response = requests.post('https://login.globo.com/api/authentication',
                                 json=dict(payload=dict(email=self._email, password=self._password, serviceId=4728)))
        body = response.json()
        if response.status_code == 200:
            self._glb_id = body['glbId']
        else:
            raise CartolaFCError(body['userMessage'])

    def time(self):
        """ time """
        if not self._glb_id:
            raise CartolaFCError('Este serviço requer autenticação')

        url = '{base_url}/auth/time'.format(base_url=self._base_url)
        data = self._request(url)

        return data if self._as_json else Time.from_dict(data)

    def liga(self, name, is_slug=False):
        """ check_slug_liga """
        if not self._glb_id:
            raise CartolaFCError('Este serviço requer autenticação')

        slug = name if is_slug else convert_team_name_to_slug(name)
        url = '{base_url}/auth/liga/{slug}'.format(base_url=self._base_url, slug=slug)
        data = self._request(url)

        return data if self._as_json else Liga.from_dict(data)

    def status(self):
        """ status. """
        url = '%s/mercado/status' % (self._base_url,)
        data = self._request(url)

        return Status.from_dict(data)

    def market(self):
        """ market. """
        url = '%s/atletas/mercado' % (self._base_url,)
        data = self._request(url)

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        positions = {position['id']: Position.from_dict(position) for position in data['posicoes'].values()}
        status = {status['id']: status for status in data['status'].values()}
        return [Athlete.from_dict(athlete, clubs=clubs, positions=positions, status=status) for athlete
                in data['atletas']]

    def round_score(self):
        """ round_score. """
        url = '%s/atletas/pontuados' % (self._base_url,)

        if self.status().status_mercado == 'Mercado fechado':
            data = self._request(url)

            clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
            positions = {position['id']: Position.from_dict(position) for position in data['posicoes'].values()}

            return {athlete_id: AthleteScore.from_dict(athlete, clubs=clubs, positions=positions) for
                    athlete_id, athlete in data['atletas'].items()}

        raise CartolaFCError('A pontuação parcial só fica disponível com o mercado fechado.')

    def highlights(self):
        """ highlights. """
        url = '%s/mercado/destaques' % (self._base_url,)
        data = self._request(url)

        return [Highlight.from_dict(highlight) for highlight in data]

    def round_highlights(self):
        """ round_highlights. """
        url = '%s/pos-rodada/destaques' % (self._base_url,)
        data = self._request(url)

        return RoundHighlights.from_dict(data)

    def sponsors(self):
        """ sponsors. """
        url = '%s/patrocinadores' % (self._base_url,)
        data = self._request(url)

        return {sponsor_id: Sponsor.from_dict(sponsor) for sponsor_id, sponsor in data.items()}

    def rounds(self):
        """ rounds. """
        url = '%s/rodadas' % (self._base_url,)
        data = self._request(url)

        return [Round.from_dict(round_) for round_ in data]

    def matches(self):
        """ matches. """
        url = '%s/partidas' % (self._base_url,)
        data = self._request(url)

        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        return [Match.from_dict(match, clubs=clubs) for match in data['partidas']]

    def clubs(self):
        """ clubs. """
        url = '%s/clubes' % (self._base_url,)
        data = self._request(url)

        return {club_id: Club.from_dict(club) for club_id, club in data.items()}

    def schemes(self):
        """ schemes. """
        url = '%s/esquemas' % (self._base_url,)
        data = self._request(url)

        return [Scheme.from_dict(scheme) for scheme in data]

    def search_team_info_by_name(self, name):
        """ search_team_info_by_name. """
        url = '%s/times?q=%s' % (self._base_url, name)
        data = self._request(url)

        return [TeamInfo.from_dict(team_info) for team_info in data]

    def get_team(self, name, is_slug=False):
        """ get_team. """
        slug = name if is_slug else convert_team_name_to_slug(name)
        url = '%s/time/slug/%s' % (self._base_url, slug)
        data = self._request(url)

        return Team.from_dict(data)

    def get_team_by_round(self, name, round_, is_slug=False):
        """ get_team_by_round. """
        slug = name if is_slug else convert_team_name_to_slug(name)
        url = '%s/time/slug/%s/%s' % (self._base_url, slug, round_)
        data = self._request(url)

        return Team.from_dict(data)

    def search_league_info_by_name(self, name):
        """ search_league_info_by_name. """
        url = '%s/ligas?q=%s' % (self._base_url, name)
        data = self._request(url)

        return [LeagueInfo.from_dict(league_info) for league_info in data]

    def _request(self, url):
        attempts = self.attempts
        while attempts:
            try:
                headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
                response = requests.get(url, headers=headers)
                if self._glb_id and response.status_code == 401:
                    self.set_credentials(self._email, self._password)
                    response = requests.get(url, headers={'X-GLB-Token': self._glb_id})
                return parse_and_check_cartolafc(response.content.decode('utf-8'))
            except CartolaFCOverloadError as error:
                attempts -= 1
                if not attempts:
                    raise error
