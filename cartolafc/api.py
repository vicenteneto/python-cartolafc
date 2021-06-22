import json
import logging
from typing import Any, Dict, List, Optional, Union

import redis
import requests
from redis import ConnectionError, TimeoutError
from requests.status_codes import codes
from requests.exceptions import HTTPError

from .constants import MERCADO_ABERTO, MERCADO_FECHADO, CAMPEONATO
from .decorators import RequiresAuthentication
from .errors import CartolaFCError, CartolaFCOverloadError
from .models import Atleta, Clube, DestaqueRodada, Liga, LigaPatrocinador, Mercado, Partida, PontuacaoInfo
from .models import Time, TimeInfo
from .util import convert_team_name_to_slug, parse_and_check_cartolafc

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class Api(object):
    """ Uma API em Python para o Cartola FC

    Exemplo de uso:
        Para criar uma instância da classe cartolafc.Api, sem autenticação:
            >>> import cartolafc
            >>> api = cartolafc.Api()

        Para obter o status atual do mercado
            >>> mercado = api.mercado()
            >>> print(mercado.rodada_atual, mercado.status.nome)

        Para utilizar autenticação, é necessário instancias a classe cartolafc.Api com os argumentos email e senha.
            >>> api =  cartolafc.Api(email='usuario@email.com', password='s3nha')

        Para obter os dados de uma liga (após se autenticar), onde "nome" é o nome da liga que deseja buscar:
            >>> liga = api.liga('nome')
            >>> print(liga.nome)

        python-cartolafc é massa!!! E possui muitos outros métodos, como:
            >>> api.mercado()
            >>> api.time(123, 'slug')
            >>> api.times('termo')
    """

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None, attempts: int = 1,
                 redis_url: Optional[str] = None, redis_timeout: int = 10) -> None:
        """ Instancia um novo objeto de cartolafc.Api.

        Args:
            email (str): O e-mail da sua conta no CartolaFC. Requerido se o password for informado.
            password (str): A senha da sua conta no CartolaFC. Requerido se o email for informado.
            attempts (int): Quantidade de tentativas que serão efetuadas se os servidores estiverem sobrecarregados.
            redis_url (str): URL para conectar ao servidor Redis, exemplo: redis://user:password@localhost:6379/2.
            redis_timeout (int): O timeout padrão (em segundos).

        Raises:
            cartolafc.CartolaFCError: Se as credenciais forem inválidas ou se apenas um dos
            dois argumentos (email e password) for informado.
        """

        self._api_url = 'https://api.cartolafc.globo.com'
        self._auth_url = 'https://login.globo.com/api/authentication'
        self._email = None
        self._password = None
        self._glb_id = None
        self._attempts = attempts if isinstance(attempts, int) and attempts > 0 else 1
        self._redis_url = None
        self._redis_timeout = None
        self._redis = None

        self.set_credentials(email, password)
        self.set_redis(redis_url, redis_timeout)

    def set_credentials(self, email: str, password: str) -> None:
        """ Realiza a autenticação no sistema do CartolaFC utilizando o email e password informados.

        Args:
            email (str): O email do usuário
            password (str): A senha do usuário

        Raises:
            cartolafc.CartolaFCError: Se o conjunto (email, password) não conseguiu realizar a autenticação com sucesso.
        """

        if bool(email) != bool(password):
            raise CartolaFCError('E-mail ou senha ausente')
        elif not email:
            return

        self._email = email
        self._password = password

        data = {
            "payload": {
                "email": self._email,
                "password": self._password,
                "serviceId": 4728,
            }
        }

        try:
            response = requests.post(self._auth_url, json=data)
            body = response.json()

            if response.status_code != codes.ok:
                raise CartolaFCError(body['userMessage'])

            self._glb_id = body['glbId']
        except HTTPError:
            raise CartolaFCError('Erro authenticando no Cartola.')

    def set_redis(self, redis_url: str, redis_timeout: int = 10) -> None:
        """ Realiza a autenticação no servidor Redis utilizando a URL informada.

        Args:
            redis_url (str): URL para conectar ao servidor Redis, exemplo: redis://user:password@localhost:6379/2.
            redis_timeout (int): O timeout padrão (em segundos).

        Raises:
            cartolafc.CartolaFCError: Se não for possível se conectar ao servidor Redis
        """
        if not redis_url:
            return

        self._redis_url = redis_url
        self._redis_timeout = redis_timeout if isinstance(redis_timeout, int) and redis_timeout > 0 else 10

        try:
            self._redis = redis.StrictRedis.from_url(url=redis_url)
            self._redis.ping()
        except (ConnectionError, TimeoutError, ValueError):
            self._redis = None
            raise CartolaFCError('Erro conectando ao servidor Redis.')

    @RequiresAuthentication
    def amigos(self) -> List[TimeInfo]:
        url = '{api_url}/auth/amigos'.format(api_url=self._api_url)
        data = self._request(url)
        return [TimeInfo.from_dict(time_info) for time_info in data['times']]

    @RequiresAuthentication
    def liga(self, nome: Optional[str] = None, slug: Optional[str] = None, page: int = 1,
             order_by: str = CAMPEONATO) -> Liga:
        """ Este serviço requer que a API esteja autenticada, e realiza uma busca pelo nome ou slug informados.
        Este serviço obtém apenas 20 times por página, portanto, caso sua liga possua mais que 20 membros, deve-se
        utilizar o argumento "page" para obter mais times.

        Args:
            nome (str): Nome da liga que se deseja obter. Requerido se o slug não for informado.
            slug (str): Slug do time que se deseja obter. *Este argumento tem prioridade sobre o nome*
            page (int): Página dos times que se deseja obter.
            order_by (str): É possível obter os times ordenados por "campeonato", "turno", "mes", "rodada" e
            "patrimonio". As constantes estão disponíveis em "cartolafc.CAMPEONATO", "cartolafc.TURNO" e assim
            sucessivamente.

        Returns:
            Um objeto representando a liga encontrada.

        Raises:
            CartolaFCError: Se a API não está autenticada ou se nenhuma liga foi encontrada com os dados recebidos.
        """

        if not any((nome, slug)):
            raise CartolaFCError('Você precisa informar o nome ou o slug da liga que deseja obter')

        slug = slug if slug else convert_team_name_to_slug(nome)
        url = '{api_url}/auth/liga/{slug}'.format(api_url=self._api_url, slug=slug)
        data = self._request(url, params=dict(page=page, orderBy=order_by))
        return Liga.from_dict(data, order_by)

    @RequiresAuthentication
    def pontuacao_atleta(self, atleta_id: int) -> List[PontuacaoInfo]:
        url = '{api_url}/auth/mercado/atleta/{id}/pontuacao'.format(api_url=self._api_url, id=atleta_id)
        data = self._request(url)
        return [PontuacaoInfo.from_dict(pontuacao_info) for pontuacao_info in data]

    @RequiresAuthentication
    def time_logado(self) -> Time:
        url = '{api_url}/auth/time'.format(api_url=self._api_url)
        data = self._request(url)
        clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
        return Time.from_dict(data, clubes=clubes, capitao=data['capitao_id'])

    def clubes(self) -> Dict[int, Clube]:
        url = '{api_url}/clubes'.format(api_url=self._api_url)
        data = self._request(url)
        return {int(clube_id): Clube.from_dict(clube) for clube_id, clube in data.items()}

    def ligas(self, query: str) -> List[Liga]:
        """ Retorna o resultado da busca ao Cartola por um determinado termo de pesquisa.

        Args:
            query (str): Termo para utilizar na busca.

        Returns:
            Uma lista de instâncias de cartolafc.Liga, uma para cada liga contento o termo utilizado na busca.
        """

        url = '{api_url}/ligas'.format(api_url=self._api_url)
        data = self._request(url, params=dict(q=query))
        return [Liga.from_dict(liga_info) for liga_info in data]

    def ligas_patrocinadores(self) -> Dict[int, LigaPatrocinador]:
        url = '{api_url}/patrocinadores'.format(api_url=self._api_url)
        data = self._request(url)
        return {
            int(patrocinador_id): LigaPatrocinador.from_dict(patrocinador)
            for patrocinador_id, patrocinador in data.items()
        }

    def mercado(self) -> Mercado:
        """ Obtém o status do mercado na rodada atual.

        Returns:
            Uma instância de cartolafc.Mercado representando o status do mercado na rodada atual.
        """

        url = '{api_url}/mercado/status'.format(api_url=self._api_url)
        data = self._request(url)
        return Mercado.from_dict(data)

    def mercado_atletas(self) -> List[Atleta]:
        url = '{api_url}/atletas/mercado'.format(api_url=self._api_url)
        data = self._request(url)
        clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
        return [Atleta.from_dict(atleta, clubes=clubes) for atleta in data['atletas']]

    def parciais(self) -> Dict[int, Atleta]:
        """ Obtém um mapa com todos os atletas que já pontuaram na rodada atual (aberta).

        Returns:
            Uma mapa, onde a key é um inteiro representando o id do atleta e o valor é uma instância de cartolafc.Atleta

        Raises:
            CartolaFCError: Se o mercado atual estiver com o status fechado.
        """

        if self.mercado().status.id == MERCADO_FECHADO:
            url = '{api_url}/atletas/pontuados'.format(api_url=self._api_url)
            data = self._request(url)
            clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
            return {
                int(atleta_id): Atleta.from_dict(atleta, clubes=clubes, atleta_id=int(atleta_id))
                for atleta_id, atleta in data['atletas'].items()
                if atleta['clube_id'] > 0
            }

        raise CartolaFCError('As pontuações parciais só ficam disponíveis com o mercado fechado.')

    def partidas(self, rodada) -> List[Partida]:
        url = '{api_url}/partidas/{rodada}'.format(api_url=self._api_url, rodada=rodada)
        data = self._request(url)
        clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
        return sorted([Partida.from_dict(partida, clubes=clubes) for partida in data['partidas']], key=lambda p: p.data)

    def pos_rodada_destaques(self) -> DestaqueRodada:
        if self.mercado().status.id == MERCADO_ABERTO:
            url = '{api_url}/pos-rodada/destaques'.format(api_url=self._api_url)
            data = self._request(url)
            return DestaqueRodada.from_dict(data)

        raise CartolaFCError('Os destaques de pós-rodada só ficam disponíveis com o mercado aberto.')

    def time(self, time_id: Optional[int] = None, nome: Optional[str] = None, slug: Optional[str] = None,
             as_json: bool = False, rodada: Optional[int] = 0) -> Union[Time, dict]:
        """ Obtém um time específico, baseando-se no nome ou no slug utilizado.
        Ao menos um dos dois devem ser informado.

        Args:
            time_id (int): Id to time que se deseja obter. *Este argumento sempre será utilizado primeiro*
            nome (str): Nome do time que se deseja obter. Requerido se o slug não for informado.
            slug (str): Slug do time que se deseja obter. *Este argumento tem prioridade sobre o nome*
            as_json (bool): Se desejar obter o retorno no formato json.

        Returns:
            Uma instância de cartolafc.Time se o time foi encontrado.

        Raises:
            cartolafc.CartolaFCError: Se algum erro aconteceu, como por exemplo: Nenhum time foi encontrado.
        """
        if not any((time_id, nome, slug)):
            raise CartolaFCError('Você precisa informar o nome ou o slug do time que deseja obter')

        param = 'id' if time_id else 'slug'
        value = time_id if time_id else (slug if slug else convert_team_name_to_slug(nome))
        url = '{api_url}/time/{param}/{value}'.format(api_url=self._api_url, param=param, value=value)
        if rodada:
            url += f'/{rodada}'

        data = self._request(url)

        if bool(as_json):
            return data

        clubes = {clube['id']: Clube.from_dict(clube) for clube in data['clubes'].values()}
        return Time.from_dict(data, clubes=clubes, capitao=data['capitao_id'])

    def time_parcial(self, time_id: Optional[int] = None, nome: Optional[str] = None, slug: Optional[str] = None,
                     parciais: Optional[Dict[int, Atleta]] = None) -> Time:
        if parciais is None and self.mercado().status.id != MERCADO_FECHADO:
            raise CartolaFCError('As pontuações parciais só ficam disponíveis com o mercado fechado.')

        parciais = parciais if isinstance(parciais, dict) else self.parciais()
        time = self.time(time_id, nome, slug)
        return self._calculate_parcial(time, parciais)

    def times(self, query: str) -> List[TimeInfo]:
        """ Retorna o resultado da busca ao Cartola por um determinado termo de pesquisa.

        Args:
            query (str): Termo para utilizar na busca.

        Returns:
            Uma lista de instâncias de cartolafc.TimeInfo, uma para cada time contento o termo utilizado na busca.
        """
        url = '{api_url}/times'.format(api_url=self._api_url)
        data = self._request(url, params=dict(q=query))
        return [TimeInfo.from_dict(time_info) for time_info in data]

    @staticmethod
    def _calculate_parcial(time: Time, parciais: Dict[int, Atleta]) -> Time:
        if any(not isinstance(key, int) or not isinstance(parciais[key], Atleta) for key in parciais.keys()) \
                or not isinstance(time, Time):
            raise CartolaFCError('Time ou parciais não são válidos.')

        time.pontos = 0
        time.jogados = 0
        for atleta in time.atletas:
            atleta_parcial = parciais.get(atleta.id)
            tem_parcial = isinstance(atleta_parcial, Atleta)

            atleta.pontos = atleta_parcial.pontos if tem_parcial else 0
            atleta.scout = atleta_parcial.scout if tem_parcial else {}
            time.jogados += 1 if tem_parcial else 0

            if atleta.is_capitao:
                atleta.pontos *= 2

            time.pontos += atleta.pontos

        return time

    def _request(self, url: str, params: Optional[Dict[str, Any]] = None) -> dict:
        cached = self._get(url)
        if cached:
            try:
                cached = cached.decode('utf-8')
            except AttributeError:
                pass
            return json.loads(cached)

        attempts = self._attempts
        while attempts:
            try:
                headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
                response = requests.get(url, params=params, headers=headers)
                if self._glb_id and response.status_code == codes.unauthorized:
                    self.set_credentials(self._email, self._password)
                    response = requests.get(url, params=params, headers={'X-GLB-Token': self._glb_id})
                parsed = parse_and_check_cartolafc(response.content.decode('utf-8'))
                return self._set(url, parsed)
            except CartolaFCOverloadError as error:
                attempts -= 1
                if not attempts:
                    raise error

    def _get(self, url: str) -> bytes:
        cached = None
        if self._redis:
            cached = self._redis.get(url)
        return cached

    def _set(self, url: str, data: dict) -> dict:
        if self._redis:
            self._redis.set(url, json.dumps(data), ex=self._redis_timeout)
        return data
