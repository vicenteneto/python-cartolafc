# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import requests_mock

import cartolafc
from cartolafc.api import MERCADO_ABERTO
from cartolafc.models import Mercado


class ApiTest(unittest.TestCase):
    with open('testdata/status_mercado_aberto.json', 'rb') as f:
        STATUS_MERCADO_ABERTO = f.read().decode('utf8')

    def setUp(self):
        self.api = cartolafc.Api()
        self.base_url = self.api._base_url

    def test_status(self):
        # Arrange
        url = '%s/mercado/status' % (self.base_url,)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.STATUS_MERCADO_ABERTO)
            status = self.api.status()

        # Assert
        self.assertIsInstance(status, Mercado)
        self.assertEqual(status.rodada_atual, 3)
        self.assertEqual(status.status_mercado.id, MERCADO_ABERTO)
        self.assertEqual(status.times_escalados, 3601523)
        self.assertIsInstance(status.fechamento, datetime)
        self.assertEqual(status.fechamento, datetime.fromtimestamp(1495904400))
        self.assertEqual(status.aviso, '')

    def test_servidores_sobrecarregados(self):
        # Arrange
        url = '%s/mercado/status' % (self.base_url,)

        # Act and Assert
        with requests_mock.mock() as m:
            m.get(url)

            with self.assertRaises(cartolafc.CartolaFCOverloadError):
                self.api.status()
