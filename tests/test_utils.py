import json
import unittest
from datetime import datetime

from cartolafc.models import Liga
from cartolafc.util import json_default


class ApiAttemptsTest(unittest.TestCase):
    with open("tests/testdata/liga.json", "rb") as f:
        LIGA = f.read().decode("utf8")

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
        liga = Liga.from_dict(json.loads(self.LIGA))
        result = json_default(liga)
        assert isinstance(result, dict)
