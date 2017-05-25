# -*- coding: utf-8 -*-

import logging
import sys

import requests

from cartolafc.decorators import RequiresAuthentication
from cartolafc.error import CartolaFCError, CartolaFCOverloadError
from cartolafc.models import (
    Athlete,
    AthleteScore,
    Club,
    Highlight,
    LeagueInfo,
    Liga,
    Position,
    Scheme,
    Status,
    Time,
    TimeInfo
)
from cartolafc.util import convert_team_name_to_slug, parse_and_check_cartolafc

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

if sys.version_info < (2, 7, 9):
    requests.packages.urllib3.disable_warnings()


class Api(object):
    """ Uma API em Python para o Cartola FC

    Exemplo de uso:
        Para criar uma instância da classe cartolafc.Api, sem autenticação:
            >>> import cartolafc
            >>> api = cartolafc.Api()
        
        Para obter o status atual do mercado
            >>> status = api.status()
            >>> print(status.rodada_atual, status.status_mercado)
        
        Para utilizar autenticação, é necessário instancias a classe cartolafc.Api com os argumentos email e senha.
            >>> api =  cartolafc.Api(email='usuario@email.com', password='s3nha')
            
        Para obter os dados de uma liga (após se autenticar), onde "nome" é o nome da liga que deseja buscar:
            >>> liga = api.liga(nome)
            >>> print(liga.nome)

        python-cartolafc é massa!!! E possui muitos outros métodos, como:
            >>> api.status()
            >>> api.time(nome, slug)
            >>> api.busca_times(termo)
    """

    def __init__(self, email=None, password=None, attempts=1):
        """ Instancia um novo objeto de cartolafc.Api.

        Args:
            email (str, opcional): O e-mail da sua conta no CartolaFC. Requerido se o password for informado.
            password (str, opcional): A senha da sua conta no CartolaFC. Requerido se o email for informado.
            attempts (int): Quantidade de tentativas que serão efetuadas se os servidores estiverem sobrecarregados.
            
        raises:
            cartolafc.CartolaFCError: Se as credenciais forem inválidas ou se apenas um dos 
            dois argumentos (email e password) for informado.
        """

        self._base_url = 'https://api.cartolafc.globo.com'
        self._email = email
        self._password = password
        self._glb_id = None
        self.attempts = attempts if isinstance(attempts, int) and attempts > 0 else 1

        if bool(email) != bool(password):
            raise CartolaFCError('E-mail ou senha ausente')
        elif all((email, password)):
            self.set_credentials(email, password)

    def set_credentials(self, email, password):
        """ Realiza a autenticação no sistema do CartolaFC utilizando o email e password informados.

        Args:
            email (str): O email do usuário
            password (str): A senha do usuário
          
        Raises:
            cartolafc.CartolaFCError: Se o conjunto (email, password) não conseguiu realizar a autenticação com sucesso.
        """

        self._email = email
        self._password = password
        response = requests.post('https://login.globo.com/api/authentication',
                                 json=dict(payload=dict(email=self._email, password=self._password, serviceId=4728)))
        body = response.json()
        if response.status_code == 200:
            self._glb_id = body['glbId']
        else:
            raise CartolaFCError(body['userMessage'])

    @RequiresAuthentication
    def amigos(self):
        url = '{base_url}/auth/amigos'.format(base_url=self._base_url)
        data = self._request(url)
        return data

    def status(self):
        """ Obtém o status do mercado na rodada atual. 

        Returns:
            Uma instância de cartolafc.Status representando o status do mercado na rodada atual.
        """
        url = '{base_url}/mercado/status'.format(base_url=self._base_url)
        data = self._request(url)

        return Status.from_dict(data)

    def time(self, nome=None, slug=None):
        """ Obtém um time específico, baseando-se no nome ou no slug utilizado.
        Ao menos um dos dois devem ser informado. 

        Args:
            nome (str, opcional): Nome do time que se deseja obter. Requerido se o slug não for informado.
            slug (str, opcional): Slug do time que se deseja obter. *Este argumento tem prioridade sobre o nome*

        Returns:
            Uma instância de cartolafc.Time se o time foi encontrado.
            
        Raises:
            cartolafc.CartolaFCError: Se algum erro aconteceu, como por exemplo: Nenhum time foi encontrado.
        """
        if not any((nome, slug)):
            raise CartolaFCError('Você precisa informar o nome ou o slug do time que deseja buscar')

        url = '{base_url}/time/slug/{slug}'.format(base_url=self._base_url,
                                                   slug=slug if slug else convert_team_name_to_slug(nome))
        data = self._request(url)

        return Time.from_dict(data)

    def busca_times(self, termo):
        """ Retorna o resultado da busca ao Cartola por um determinado termo de pesquisa. 

        Args:
            termo (str): Termo para utilizar na busca.

        Returns:
            Uma lista de instâncias de cartolafc.TimeInfo, uma para cada time contento o termo utilizado na busca.
        """
        url = '{base_url}/times?q={term}'.format(base_url=self._base_url, term=termo)
        data = self._request(url)

        return [TimeInfo.from_dict(time_info) for time_info in data]

    def liga(self, name, is_slug=False):
        """ check_slug_liga """
        slug = name if is_slug else convert_team_name_to_slug(name)
        url = '{base_url}/auth/liga/{slug}'.format(base_url=self._base_url, slug=slug)
        data = self._request(url)

        return Liga.from_dict(data)

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

    def schemes(self):
        """ schemes. """
        url = '%s/esquemas' % (self._base_url,)
        data = self._request(url)

        return [Scheme.from_dict(scheme) for scheme in data]

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
