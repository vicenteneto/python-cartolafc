import json
import unittest
from datetime import datetime

from cartolafc.models import Mercado
from cartolafc.util import json_default


class ApiAttemptsTest(unittest.TestCase):
    with open("tests/testdata/mercado_status_aberto.json", "rb") as f:
        MERCADO = f.read().decode("utf8")

    def test_json_default_datetime(self):
        date = datetime(
            year=2019,
            month=10,
            day=10,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        result = json_default(date)
        assert isinstance(result, dict)

    def test_json_default_cartolafc_model(self):
        mercado = Mercado.from_dict(json.loads(self.MERCADO))
        result = json_default(mercado)
        assert isinstance(result, dict)
