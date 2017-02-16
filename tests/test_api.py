# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import requests_mock

import cartolafc


class ApiTest(unittest.TestCase):
    with open('testdata/status.json', 'rb') as f:
        STATUS_SAMPLE_JSON = str(f.read().decode('utf8'))

    def setUp(self):
        self.api = cartolafc.Api()
        self.base_url = self.api.base_url

    def testGetStatus(self):
        """Test the cartolafc.Api status method"""

        # Arrange
        url = '%s/mercado/status' % (self.base_url,)

        # Act
        with requests_mock.mock() as m:
            m.get(url, content=self.STATUS_SAMPLE_JSON)
            status = self.api.status()

        # Assert
        self.assertEqual(38, status.rodada_atual)
        self.assertEqual('Encerrado', status.status_mercado)
        self.assertEqual(2016, status.temporada)
        self.assertEqual(1702092, status.times_escalados)
        self.assertEqual(datetime.fromtimestamp(1481475600), status.fechamento)
        self.assertEqual(False, status.mercado_pos_rodada)
        self.assertEqual('', status.aviso)
