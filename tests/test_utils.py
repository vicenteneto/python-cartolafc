from cartolafc.util import json_default
from datetime import datetime

def test_json_default():
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