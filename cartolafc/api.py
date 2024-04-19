import logging
from typing import Any, Dict, List, Optional

import requests

from .constants import MERCADO_ABERTO, MERCADO_FECHADO, MULTIPLICADOR_CAPITAO
from .errors import CartolaFCError, CartolaFCOverloadError
from .models import (
    Atleta,
    AtletaDestaque,
    Clube,
    DestaqueRodada,
    Liga,
    Patrocinador,
    Mercado,
    Partida,
)
from .models import Time, TimeInfo
from .util import parse_and_check_cartolafc

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class Api(object):
    """Uma API em Python para o Cartola FC

    Exemplo de uso:
        Para criar uma instância da classe cartolafc.Api, sem autenticação:
            >>> import cartolafc
            >>> api = cartolafc.Api()

        Para obter o status atual do mercado
            >>> mercado = api.mercado()
            >>> print(mercado.rodada_atual, mercado.status.nome)

        python-cartolafc é massa!!! E possui muitos outros métodos, como:
            >>> api.mercado()
            >>> api.time(123)
            >>> api.times('termo')
    """

    def __init__(self, attempts: int = 1) -> None:
        """Instancia um novo objeto de cartolafc.Api.

        Args:
            attempts (int): Quantidade de tentativas que serão efetuadas se os servidores estiverem sobrecarregados.
        """

        self._api_url = "https://api.cartola.globo.com"
        self._attempts = attempts if attempts > 0 else 1

    def clubes(self) -> Dict[int, Clube]:
        url = f"{self._api_url}/clubes"
        data = self._request(url)
        return {
            int(clube_id): Clube.from_dict(clube) for clube_id, clube in data.items()
        }

    def ligas(self, query: str) -> List[Liga]:
        """Retorna o resultado da busca ao Cartola por um determinado termo de pesquisa.

        Args:
            query (str): Termo para utilizar na busca.

        Returns:
            Uma lista de instâncias de cartolafc.Liga, uma para cada liga contento o termo utilizado na busca.
        """

        url = f"{self._api_url}/ligas"
        data = self._request(url, params=dict(q=query))
        return [Liga.from_dict(liga_info) for liga_info in data]

    def patrocinadores(self) -> Dict[int, Patrocinador]:
        url = f"{self._api_url}/patrocinadores"
        data = self._request(url)
        return {
            int(patrocinador_id): Patrocinador.from_dict(patrocinador)
            for patrocinador_id, patrocinador in data.items()
        }

    def mercado(self) -> Mercado:
        """Obtém o status do mercado na rodada atual.

        Returns:
            Uma instância de cartolafc.Mercado representando o status do mercado na rodada atual.
        """

        url = f"{self._api_url}/mercado/status"
        data = self._request(url)
        return Mercado.from_dict(data)

    def mercado_atletas(self) -> List[Atleta]:
        url = f"{self._api_url}/atletas/mercado"
        data = self._request(url)
        clubes = {
            clube["id"]: Clube.from_dict(clube) for clube in data["clubes"].values()
        }
        return [Atleta.from_dict(atleta, clubes=clubes) for atleta in data["atletas"]]

    def parciais(self) -> Dict[int, Atleta]:
        """Obtém um mapa com todos os atletas que já pontuaram na rodada atual (aberta).

        Returns:
            Uma mapa, onde a key é um inteiro representando o id do atleta e o valor é uma instância de cartolafc.Atleta

        Raises:
            CartolaFCError: Se o mercado atual estiver com o status fechado.
        """

        if self.mercado().status.id == MERCADO_FECHADO:
            url = f"{self._api_url}/atletas/pontuados"
            data = self._request(url)
            clubes = {
                clube["id"]: Clube.from_dict(clube) for clube in data["clubes"].values()
            }
            return {
                int(atleta_id): Atleta.from_dict(
                    atleta, clubes=clubes, atleta_id=int(atleta_id)
                )
                for atleta_id, atleta in data["atletas"].items()
                if atleta["clube_id"] > 0
            }

        raise CartolaFCError(
            "As pontuações parciais só ficam disponíveis com o mercado fechado."
        )

    def partidas(self, rodada: Optional[int] = 0) -> List[Partida]:
        url = f"{self._api_url}/partidas"
        if rodada:
            url += f"/{rodada}"

        data = self._request(url)
        clubes = {
            clube["id"]: Clube.from_dict(clube) for clube in data["clubes"].values()
        }
        return sorted(
            [Partida.from_dict(partida, clubes=clubes) for partida in data["partidas"]],
            key=lambda p: p.data,
        )

    def destaques(self) -> List[AtletaDestaque]:
        """Obtém os destaques do mercado na rodada atual.

        Returns:
            Uma lista de Atletas.
        """

        url = f"{self._api_url}/mercado/destaques"
        data = self._request(url)
        return [AtletaDestaque.from_dict(destaque) for destaque in data]

    def destaques_reservas(self) -> List[AtletaDestaque]:
        """Obtém os destaques resservas do mercado na rodada atual.

        Returns:
            Uma lista de Atletas.
        """

        url = f"{self._api_url}/mercado/destaques/reservas"
        data = self._request(url)
        return [AtletaDestaque.from_dict(destaque) for destaque in data]

    def pos_rodada_destaques(self) -> DestaqueRodada:
        mercado = self.mercado()
        if mercado.rodada_atual == 1:
            raise CartolaFCError(
                "Os destaques de pós-rodada só ficam disponíveis após a primeira rodada."
            )

        if mercado.status.id == MERCADO_ABERTO:
            url = f"{self._api_url}/pos-rodada/destaques"
            data = self._request(url)
            return DestaqueRodada.from_dict(data)

        raise CartolaFCError(
            "Os destaques de pós-rodada só ficam disponíveis com o mercado aberto."
        )

    def time(self, time_id: int, rodada: Optional[int] = 0) -> Time:
        """Obtém um time específico, baseando-se no nome ou no slug utilizado.
        Ao menos um dos dois devem ser informado.

        Args:
            time_id (int): Id to time que se deseja obter.
            rodada (int): Número da rodada. Se não for informado, será retornado sempre a última rodada.

        Returns:
            Uma instância de cartolafc.Time se o time foi encontrado.

        Raises:
            cartolafc.CartolaFCError: Se algum erro aconteceu, como por exemplo: Nenhum time foi encontrado.
        """

        url = f"{self._api_url}/time/id/{time_id}"
        if rodada:
            url += f"/{rodada}"

        data = self._request(url)
        return Time.from_dict(data, clubes=self.clubes(), capitao=data["capitao_id"])

    def time_parcial(
        self,
        time_id: int,
        parciais: Optional[Dict[int, Atleta]] = None,
    ) -> Time:
        if parciais is None and self.mercado().status.id != MERCADO_FECHADO:
            raise CartolaFCError(
                "As pontuações parciais só ficam disponíveis com o mercado fechado."
            )

        parciais = parciais if isinstance(parciais, dict) else self.parciais()
        time = self.time(time_id)
        return self._calculate_parcial(time, parciais)

    def times(self, query: str) -> List[TimeInfo]:
        """Retorna o resultado da busca ao Cartola por um determinado termo de pesquisa.

        Args:
            query (str): Termo para utilizar na busca.

        Returns:
            Uma lista de instâncias de cartolafc.TimeInfo, uma para cada time contento o termo utilizado na busca.
        """
        url = f"{self._api_url}/times"
        data = self._request(url, params=dict(q=query))
        return [TimeInfo.from_dict(time_info) for time_info in data]

    @staticmethod
    def _calculate_parcial(time: Time, parciais: Dict[int, Atleta]) -> Time:
        if any(
            not isinstance(key, int) or not isinstance(parciais[key], Atleta)
            for key in parciais.keys()
        ) or not isinstance(time, Time):
            raise CartolaFCError("Time ou parciais não são válidos.")

        time.pontos = 0
        time.jogados = 0
        for atleta in time.atletas:
            atleta_parcial = parciais.get(atleta.id)
            tem_parcial = isinstance(atleta_parcial, Atleta)

            atleta.pontos = atleta_parcial.pontos if tem_parcial else 0
            atleta.scout = atleta_parcial.scout if tem_parcial else {}
            time.jogados += 1 if tem_parcial else 0

            if atleta.is_capitao:
                atleta.pontos *= MULTIPLICADOR_CAPITAO

            time.pontos += atleta.pontos

        return time

    def _request(self, url: str, params: Optional[Dict[str, Any]] = None) -> dict:
        attempts = self._attempts
        while attempts:
            try:
                response = requests.get(url, params=params)
                return parse_and_check_cartolafc(response.content.decode("utf-8"))
            except CartolaFCOverloadError as error:
                attempts -= 1
                if not attempts:
                    raise error
