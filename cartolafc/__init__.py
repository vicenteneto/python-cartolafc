"""
    cartolafc
    ~~~~~~~~~

    Uma API em Python para o Cartola FC.

    :copyright: (c) 2017 por Vicente Neto.
    :license: MIT, veja LICENSE para mais detalhes.
"""

from .api import Api
from .constants import MERCADO_ABERTO, MERCADO_FECHADO, CAMPEONATO, TURNO, MES, RODADA, PATRIMONIO
from .errors import CartolaFCError, CartolaFCOverloadError

__all__ = [
    'Api',
    'MERCADO_ABERTO',
    'MERCADO_FECHADO',
    'CAMPEONATO',
    'TURNO',
    'MES',
    'RODADA',
    'PATRIMONIO',
    'CartolaFCError',
    'CartolaFCOverloadError',
]
