import json
from collections import namedtuple
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from .util import json_default

Posicao = namedtuple("Posicao", ["id", "nome", "abreviacao"])
Status = namedtuple("Status", ["id", "nome"])

_posicoes = {
    1: Posicao(1, "Goleiro", "gol"),
    2: Posicao(2, "Lateral", "lat"),
    3: Posicao(3, "Zagueiro", "zag"),
    4: Posicao(4, "Meia", "mei"),
    5: Posicao(5, "Atacante", "ata"),
    6: Posicao(6, "Técnico", "tec"),
}

_atleta_status = {
    2: Status(2, "Dúvida"),
    3: Status(3, "Suspenso"),
    5: Status(5, "Contundido"),
    6: Status(6, "Nulo"),
    7: Status(7, "Provável"),
}

_mercado_status = {
    1: Status(1, "Mercado aberto"),
    2: Status(2, "Mercado fechado"),
    3: Status(3, "Mercado em atualização"),
    4: Status(4, "Mercado em manutenção"),
    6: Status(6, "Final de temporada"),
}

T = TypeVar("T", bound="BaseModel")


class BaseModel(object):
    def __repr__(self) -> str:
        return json.dumps(self, default=json_default)

    @classmethod
    def from_dict(cls: Type[T], *args: Tuple[Any], **kwargs: Dict[str, Any]) -> T:
        raise NotImplementedError


class TimeInfo(BaseModel):
    """Time Info"""

    def __init__(
        self,
        time_id: int,
        nome: str,
        nome_cartola: str,
        slug: str,
        assinante: bool,
        pontos: float,
    ) -> None:
        self.id = time_id
        self.nome = nome
        self.nome_cartola = nome_cartola
        self.slug = slug
        self.assinante = assinante
        self.pontos = pontos

    @classmethod
    def from_dict(cls, data: dict, ranking: str = None) -> "TimeInfo":
        pontos = (
            data["pontos"][ranking] if ranking and ranking in data["pontos"] else None
        )
        return cls(
            data["time_id"],
            data["nome"],
            data["nome_cartola"],
            data["slug"],
            data["assinante"],
            pontos,
        )


class Clube(BaseModel):
    """Representa um dos 20 clubes presentes no campeonato, e possui informações como o nome e a abreviação"""

    def __init__(self, clube_id: int, nome: str, abreviacao: str) -> None:
        self.id = clube_id
        self.nome = nome
        self.abreviacao = abreviacao

    @classmethod
    def from_dict(cls, data: dict) -> "Clube":
        return cls(data["id"], data["nome"], data["abreviacao"])


class Atleta(BaseModel):
    """Representa um atleta (jogador ou técnico), e possui informações como o apelido, clube e pontuação obtida"""

    def __init__(
        self,
        atleta_id: int,
        apelido: str,
        pontos: float,
        scout: Dict[str, int],
        posicao_id: int,
        clube: Clube,
        status_id: Optional[int] = None,
        is_capitao: Optional[bool] = None,
    ) -> None:
        self.id = atleta_id
        self.apelido = apelido
        self.pontos = pontos
        self.scout = scout
        self.posicao = _posicoes[posicao_id]
        self.clube = clube
        self.status = _atleta_status[status_id] if status_id else None
        self.is_capitao = is_capitao

    @classmethod
    def from_dict(
        cls,
        data: dict,
        clubes: Dict[int, Clube],
        atleta_id: Optional[int] = None,
        is_capitao: Optional[bool] = None,
    ) -> "Atleta":
        atleta_id = atleta_id if atleta_id else data["atleta_id"]
        pontos = data["pontos_num"] if "pontos_num" in data else data["pontuacao"]
        if data["clube_id"] in clubes:
            clube = clubes[data["clube_id"]]
        else:
            clube = Clube(0, "Sem Clube", "Sem Clube")
        return cls(
            atleta_id,
            data["apelido"],
            pontos,
            data["scout"],
            data["posicao_id"],
            clube,
            data.get("status_id", None),
            is_capitao,
        )


class DestaqueRodada(BaseModel):
    """Destaque Rodada"""

    def __init__(
        self, media_cartoletas: float, media_pontos: float, mito_rodada: TimeInfo
    ) -> None:
        self.media_cartoletas = media_cartoletas
        self.media_pontos = media_pontos
        self.mito_rodada = mito_rodada

    @classmethod
    def from_dict(cls, data: dict) -> "DestaqueRodada":
        mito_rodada = TimeInfo.from_dict(data["mito_rodada"])
        return cls(data["media_cartoletas"], data["media_pontos"], mito_rodada)


class Liga(BaseModel):
    """Liga"""

    def __init__(
        self, liga_id: int, nome: str, slug: str, descricao: str, times: List[TimeInfo]
    ) -> None:
        self.id = liga_id
        self.nome = nome
        self.slug = slug
        self.descricao = descricao
        self.times = times

    @classmethod
    def from_dict(cls, data: dict, ranking: Optional[str] = None) -> "Liga":
        data_liga = data.get("liga", data)
        times = (
            [TimeInfo.from_dict(time, ranking=ranking) for time in data["times"]]
            if "times" in data
            else None
        )
        return cls(
            data_liga["liga_id"],
            data_liga["nome"],
            data_liga["slug"],
            data_liga["descricao"],
            times,
        )


class LigaPatrocinador(BaseModel):
    """Liga Patrocinador"""

    def __init__(self, liga_id: int, nome: str, url_link: str) -> None:
        self.id = liga_id
        self.nome = nome
        self.url_link = url_link

    @classmethod
    def from_dict(cls, data: dict) -> "LigaPatrocinador":
        return cls(data["liga_id"], data["nome"], data["url_link"])


class Mercado(BaseModel):
    """Mercado"""

    def __init__(
        self,
        rodada_atual: int,
        status_mercado: int,
        times_escalados: int,
        fechamento: datetime,
    ) -> None:
        self.rodada_atual = rodada_atual
        self.status = _mercado_status[status_mercado]
        self.times_escalados = times_escalados
        self.fechamento = fechamento

    @classmethod
    def from_dict(cls, data: dict) -> "Mercado":
        fechamento = datetime(
            data["fechamento"]["ano"],
            data["fechamento"]["mes"],
            data["fechamento"]["dia"],
            data["fechamento"]["hora"],
            data["fechamento"]["minuto"],
        )
        return cls(
            data["rodada_atual"],
            data["status_mercado"],
            data["times_escalados"],
            fechamento,
        )


class Partida(BaseModel):
    """Partida"""

    def __init__(
        self,
        data: datetime,
        local: str,
        clube_casa: Clube,
        placar_casa: int,
        clube_visitante: Clube,
        placar_visitante: int,
    ) -> None:
        self.data = data
        self.local = local
        self.clube_casa = clube_casa
        self.placar_casa = placar_casa
        self.clube_visitante = clube_visitante
        self.placar_visitante = placar_visitante

    @classmethod
    def from_dict(cls, data: dict, clubes: Dict[int, Clube]) -> "Partida":
        data_ = datetime.strptime(data["partida_data"], "%Y-%m-%d %H:%M:%S")
        local = data["local"]
        clube_casa = clubes[data["clube_casa_id"]]
        placar_casa = data["placar_oficial_mandante"]
        clube_visitante = clubes[data["clube_visitante_id"]]
        placar_visitante = data["placar_oficial_visitante"]
        return cls(
            data_, local, clube_casa, placar_casa, clube_visitante, placar_visitante
        )


class Time(BaseModel):
    """Time"""

    def __init__(
        self,
        patrimonio: float,
        valor_time: float,
        ultima_pontuacao: float,
        atletas: List[Atleta],
        info: TimeInfo,
    ) -> None:
        self.patrimonio = patrimonio
        self.valor_time = valor_time
        self.ultima_pontuacao = ultima_pontuacao
        self.atletas = atletas
        self.info = info
        self.pontos = None

    @classmethod
    def from_dict(cls, data: dict, clubes: Dict[int, Clube], capitao: int) -> "Time":
        data["atletas"].sort(key=lambda a: a["posicao_id"])
        atletas = [
            Atleta.from_dict(atleta, clubes, is_capitao=atleta["atleta_id"] == capitao)
            for atleta in data["atletas"]
        ]
        info = TimeInfo.from_dict(data["time"])
        return cls(
            data["patrimonio"], data["valor_time"], data["pontos"], atletas, info
        )
