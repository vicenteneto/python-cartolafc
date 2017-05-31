"""
    cartolafc
    ~~~~~~~~~

    Uma API em Python para o Cartola FC.

    :copyright: \(c\) 2017 por Vicente Neto.
    :license: MIT, veja LICENSE para mais detalhes.
"""

from .api import Api, CAMPEONATO, TURNO, MERCADO_ABERTO, MERCADO_FECHADO, MES, RODADA, PATRIMONIO
from .error import CartolaFCError, CartolaFCOverloadError
