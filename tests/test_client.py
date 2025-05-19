from cartolafc import CartolaClient


def test_basic_call():
    api = CartolaClient()
    assert "status_mercado" in api.mercado_status()
