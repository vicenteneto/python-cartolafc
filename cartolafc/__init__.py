"""
    cartolafc
    ~~~~~~~~~

    Uma API em Python para o Cartola FC.

    :copyright: (c) 2023 por Vicente Ramos.
    :license: MIT, veja LICENSE para mais detalhes.
"""

from .api import Api
from .errors import CartolaFCError, CartolaFCGameOverError, CartolaFCOverloadError

__all__ = [
    "Api",
    "CartolaFCError",
    "CartolaFCGameOverError",
    "CartolaFCOverloadError",
]
