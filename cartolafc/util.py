import datetime
import json
import logging
from typing import Any

from .errors import CartolaFCError, CartolaFCGameOverError, CartolaFCOverloadError


def json_default(value: Any) -> dict:
    if isinstance(value, datetime.datetime):
        return dict(
            year=value.year,
            month=value.month,
            day=value.day,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
            microsecond=value.microsecond,
            tzinfo=value.tzinfo,
        )
    return value.__dict__


def parse_and_check_cartolafc(json_data: str) -> dict:
    try:
        data = json.loads(json_data)
        if "game_over" in data and data["game_over"]:
            logging.info(
                "Desculpe-nos, o jogo acabou e não podemos obter os dados solicitados"
            )
            raise CartolaFCGameOverError(
                "Desculpe-nos, o jogo acabou e não podemos obter os dados solicitados"
            )
        if "mensagem" in data and data["mensagem"]:
            logging.error(data["mensagem"])
            raise CartolaFCError(data["mensagem"].encode("utf-8"))
        return data
    except ValueError as error:
        logging.error("Error parsing and checking json data: %s", json_data)
        logging.error(error)
        raise CartolaFCOverloadError(
            "Globo.com - Desculpe-nos, nossos servidores estão sobrecarregados."
        )
