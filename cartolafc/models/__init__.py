"""Typed domain models for the Cartola FC public API.

All models inherit from **Pydantic v2** `BaseModel` and ignore
unknown fields so minor API changes won’t break the client.

Usage example
-------------
```python
from cartolafc.models import Mercado

mercado = Mercado.model_validate(api.mercado_status())
print(mercado.status)
```
"""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "Posicao",
    "AtletaStatus",
    "MercadoStatus",
    "Clube",
    "Atleta",
    "Fechamento",
    "Mercado",
    "TimeInfo",
    "Time",
    "Liga",
]

# ──────────────────────────────────────────────────────────────────────
# Enumerations
# ──────────────────────────────────────────────────────────────────────


class Posicao(IntEnum):
    GOLEIRO = 1
    LATERAL = 2
    ZAGUEIRO = 3
    MEIA = 4
    ATACANTE = 5
    TECNICO = 6

    def __str__(self) -> str:  # pragma: no cover
        return self.name.capitalize()


class AtletaStatus(IntEnum):
    DUVIDA = 2
    SUSPENSO = 3
    CONTUNDIDO = 5
    NULO = 6
    PROVAVEL = 7

    def __str__(self) -> str:  # pragma: no cover
        return self.name.capitalize()


class MercadoStatus(IntEnum):
    ABERTO = 1
    FECHADO = 2
    ATUALIZACAO = 3
    MANUTENCAO = 4
    FIM_TEMPORADA = 6

    def __str__(self) -> str:  # pragma: no cover
        return self.name.capitalize()


# ──────────────────────────────────────────────────────────────────────
# Base config
# ──────────────────────────────────────────────────────────────────────


class _CartolaBase(BaseModel):
    """Common Pydantic config: ignore extra fields, allow alias access."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True, frozen=True)


# ──────────────────────────────────────────────────────────────────────
# Core models
# ──────────────────────────────────────────────────────────────────────


class Clube(_CartolaBase):
    id: int
    nome: str
    abreviacao: str


class Atleta(_CartolaBase):
    id: int = Field(alias="atleta_id")
    apelido: str
    pontos: float = Field(alias="pontos_num")
    scout: Dict[str, int]
    posicao_id: Posicao = Field(alias="posicao_id")
    clube_id: int = Field(alias="clube_id")
    status_id: Optional[AtletaStatus] = Field(default=None, alias="status_id")

    # convenient helpers
    @property
    def posicao(self) -> Posicao:  # pragma: no cover
        return self.posicao_id

    @property
    def status(self) -> Optional[AtletaStatus]:  # pragma: no cover
        return self.status_id


class Fechamento(_CartolaBase):
    timestamp: int
    dia: Optional[int] = None
    mes: Optional[int] = None
    ano: Optional[int] = None
    hora: Optional[str] = None

    @property
    def as_datetime(self) -> datetime:  # pragma: no cover
        return datetime.fromtimestamp(self.timestamp)


class Mercado(_CartolaBase):
    rodada_atual: int
    status_mercado: MercadoStatus
    times_escalados: int
    aviso: str
    fechamento: Fechamento

    # alias for older naming
    @property
    def status(self) -> MercadoStatus:  # pragma: no cover
        return self.status_mercado


class TimeInfo(_CartolaBase):
    id: int = Field(alias="time_id")
    nome: str
    nome_cartola: str
    slug: str
    assinante: bool
    pontos: Optional[float] = None


class Time(_CartolaBase):
    patrimonio: float
    valor_time: float
    ultima_pontuacao: float = Field(alias="pontos")
    atletas: List[Atleta]
    info: TimeInfo = Field(alias="time_info")


class Liga(_CartolaBase):
    id: int = Field(alias="liga_id")
    nome: str
    slug: str
    descricao: str
    times: Optional[List[TimeInfo]] = None
