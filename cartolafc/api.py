# -*- coding: utf-8 -*-

import logging
import sys

import requests

from cartolafc.decorators import RequiresAuthentication
from cartolafc.error import CartolaFCError, CartolaFCOverloadError
from cartolafc.models import Atleta, Clube, DestaqueRodada, Liga, Mercado, Patrocinador, PontuacaoInfo, Time, TimeInfo
from cartolafc.util import convert_team_name_to_slug, parse_and_check_cartolafc

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

if sys.version_info < (2, 7, 9):
    requests.packages.urllib3.disable_warnings()

MERCADO_ABERTO = 1
MERCADO_FECHADO = 2

CAMPEONATO = 'campeonato'
TURNO = 'turno'
MES = 'mes'
RODADA = 'rodada'
PATRIMONIO = 'patrimonio'


class Api(object):
    """ Uma API em Python para o Cartola FC

    Exemplo de uso:
        Para criar uma instância da classe cartolafc.Api, sem autenticação:
            >>> import cartolafc
            >>> api = cartolafc.Api()
        
        Para obter o status atual do mercado
            >>> status = api.status()
            >>> print(status.rodada_atual, status.status_mercado.nome)
        
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
        return [TimeInfo.from_dict(time_info) for time_info in data['times']]

    @RequiresAuthentication
    def liga(self, nome=None, slug=None, page=1, order_by=CAMPEONATO):
        if not any((nome, slug)):
            raise CartolaFCError('Você precisa informar o nome ou o slug da liga que deseja obter')

        slug = slug if slug else convert_team_name_to_slug(nome)
        url = '{base_url}/auth/liga/{slug}'.format(base_url=self._base_url, slug=slug)
        data = self._request(url, params=dict(page=page, orderBy=order_by))
        return Liga.from_dict(data)

    @RequiresAuthentication
    def pontuacao_atleta(self, id):
        url = '{base_url}/auth/mercado/atleta/{id}/pontuacao'.format(base_url=self._base_url, id=id)
        data = self._request(url)
        return [PontuacaoInfo.from_dict(pontuacao_info) for pontuacao_info in data]

    @RequiresAuthentication
    def time_logado(self):
        url = '{base_url}/auth/time'.format(base_url=self._base_url)
        data = self._request(url)
        clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
        return Time.from_dict(data, clubes=clubes)

    def clubes(self):
        url = '{base_url}/clubes'.format(base_url=self._base_url)
        data = self._request(url)
        return {clube_id: Clube.from_dict(clube) for clube_id, clube in data.items()}

    def ligas(self, query):
        url = '{base_url}/ligas'.format(base_url=self._base_url)
        data = self._request(url, params=dict(q=query))
        return [Liga.from_dict(liga_info) for liga_info in data]

    def mercado(self):
        url = '{base_url}/atletas/mercado'.format(base_url=self._base_url)
        data = self._request(url)
        clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
        return [Atleta.from_dict(atleta, clubes=clubes) for atleta in data['atletas']]

    def status_mercado(self):
        """ Obtém o status do mercado na rodada atual. 

        Returns:
            Uma instância de cartolafc.Mercado representando o status do mercado na rodada atual.
        """

        url = '{base_url}/mercado/status'.format(base_url=self._base_url)
        data = self._request(url)
        return Mercado.from_dict(data)

    def parciais(self):
        if self.status_mercado().status_mercado.id == MERCADO_FECHADO:
            url = '{base_url}/atletas/pontuados'.format(base_url=self._base_url)
            data = self._request(url)
            clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
            return {atleta_id: Atleta.from_dict(atleta, clubes=clubes, atleta_id=atleta_id) for atleta_id, atleta
                    in data['atletas'].items()}

        raise CartolaFCError('As pontuações parciais só ficam disponíveis com o mercado fechado.')

    def patrocinadores(self):
        url = '{base_url}/patrocinadores'.format(base_url=self._base_url)
        data = self._request(url)
        return {patrocinador_id: Patrocinador.from_dict(patrocinador) for patrocinador_id, patrocinador in data.items()}

    def pos_rodada_destaques(self):
        if self.status_mercado().status_mercado.id == MERCADO_ABERTO:
            url = '{base_url}/pos-rodada/destaques'.format(base_url=self._base_url)
            data = self._request(url)
            return DestaqueRodada.from_dict(data)

        raise CartolaFCError('Os destaques de pós-rodada só ficam disponíveis com o mercado aberto.')

    def time(self, id=None, nome=None, slug=None):
        """ Obtém um time específico, baseando-se no nome ou no slug utilizado.
        Ao menos um dos dois devem ser informado. 

        Args:
            id (int, opcional): Id to time que se deseja obter. *Este argumento sempre será utilizado primeiro*
            nome (str, opcional): Nome do time que se deseja obter. Requerido se o slug não for informado.
            slug (str, opcional): Slug do time que se deseja obter. *Este argumento tem prioridade sobre o nome*

        Returns:
            Uma instância de cartolafc.Time se o time foi encontrado.
            
        Raises:
            cartolafc.CartolaFCError: Se algum erro aconteceu, como por exemplo: Nenhum time foi encontrado.
        """
        if not any((id, nome, slug)):
            raise CartolaFCError('Você precisa informar o nome ou o slug do time que deseja obter')

        param = 'id' if id else 'slug'
        value = id if id else (slug if slug else convert_team_name_to_slug(nome))
        url = '{base_url}/time/{param}/{value}'.format(base_url=self._base_url, param=param, value=value)
        data = self._request(url)
        clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
        return Time.from_dict(data, clubes=clubes)

    def time_parcial(self, id=None, nome=None, slug=None, parciais=None):
        parciais = parciais if parciais else self.parciais()
        time = self.time(id, nome, slug)

        time.pontos = 0
        for atleta in time.atletas:
            tem_parcial = atleta.atleta_id in parciais
            atleta.pontos = parciais[atleta.atleta_id].pontos if tem_parcial else 0
            atleta.scout = parciais[atleta.atleta_id].scout if tem_parcial else {}
            time.pontos += atleta.pontos

        return time

    def times(self, query):
        """ Retorna o resultado da busca ao Cartola por um determinado termo de pesquisa. 

        Args:
            query (str): Termo para utilizar na busca.

        Returns:
            Uma lista de instâncias de cartolafc.TimeInfo, uma para cada time contento o termo utilizado na busca.
        """
        url = '{base_url}/times'.format(base_url=self._base_url)
        data = self._request(url, params=dict(q=query))
        return [TimeInfo.from_dict(time_info) for time_info in data]

    def _request(self, url, params=None):
        attempts = self.attempts
        while attempts:
            try:
                headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
                response = requests.get(url, params=params, headers=headers)
                if self._glb_id and response.status_code == 401:
                    self.set_credentials(self._email, self._password)
                    response = requests.get(url, params=params, headers={'X-GLB-Token': self._glb_id})
                return parse_and_check_cartolafc(response.content.decode('utf-8'))
            except CartolaFCOverloadError as error:
                attempts -= 1
                if not attempts:
                    raise error
