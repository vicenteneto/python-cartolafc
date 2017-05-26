# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

import requests_mock

import cartolafc
from cartolafc.api import MERCADO_ABERTO
from cartolafc.models import Mercado, TimeInfo


class ApiAttemptsTest(unittest.TestCase):
    def test_api_attempts_nao_inteiro(self):
        # Arrange and Act
        api = cartolafc.Api(attempts='texto')

        # Assert
        self.assertEqual(api.attempts, 1)

    def test_api_attempts_menor_que_1(self):
        # Arrange and Act
        api = cartolafc.Api(attempts=0)

        # Assert
        self.assertEqual(api.attempts, 1)

    def test_api_attempts(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            api = cartolafc.Api(attempts=2)

            url = '{api_url}/mercado/status'.format(api_url=api._api_url)
            error_message = 'Mensagem de erro'
            m.get(url, status_code=200, text='{"mensagem": "%s"}' % error_message)

            with self.assertRaisesRegexp(cartolafc.CartolaFCError, error_message):
                api.status()


class ApiAuthComErro(unittest.TestCase):
    def test_api_auth_sem_email(self):
        # Act and Assert
        with self.assertRaisesRegexp(cartolafc.CartolaFCError, 'E-mail ou senha ausente'):
            cartolafc.Api(password='s3nha')

    def test_api_auth_sem_password(self):
        # Act and Assert
        with self.assertRaisesRegexp(cartolafc.CartolaFCError, 'E-mail ou senha ausente'):
            cartolafc.Api(email='email@email.com')

    def test_api_auth_invalida(self):
        # Arrange
        with requests_mock.mock() as m:
            user_message = 'Seu e-mail ou senha estao incorretos.'
            m.post('https://login.globo.com/api/authentication', status_code=401,
                   text='{"id": "BadCredentials", "userMessage": "%s"}' % user_message)

            # Act and Assert
            with self.assertRaisesRegexp(cartolafc.CartolaFCError, user_message):
                cartolafc.Api(email='email@email.com', password='s3nha')

    def test_api_auth_com_sucesso(self):
        # Arrange
        with requests_mock.mock() as m:
            m.post('https://login.globo.com/api/authentication',
                   text='{"id": "Authenticated", "userMessage": "Usuario autenticado com sucesso", "glbId": "GLB_ID"}')

            # Act
            api = cartolafc.Api(email='email@email.com', password='s3nha')

            # Assert
            self.assertEqual(api._glb_id, 'GLB_ID')

    def test_api_auth_unauthorized(self):
        # Arrange
        with requests_mock.mock() as m:
            m.post('https://login.globo.com/api/authentication',
                   text='{"id": "Authenticated", "userMessage": "Usuario autenticado com sucesso", "glbId": "GLB_ID"}')

            api = cartolafc.Api(email='email@email.com', password='s3nha')

            url = '{api_url}/mercado/status'.format(api_url=api._api_url)
            m.get(url, status_code=401)

            # Act and Assert
            with self.assertRaises(cartolafc.CartolaFCOverloadError):
                api.status()


class ApiAuthTest(unittest.TestCase):
    with open('testdata/amigos.json', 'rb') as f:
        AMIGOS = f.read().decode('utf8')

    def setUp(self):
        with requests_mock.mock() as m:
            m.post('https://login.globo.com/api/authentication',
                   text='{"id": "Authenticated", "userMessage": "Usuario autenticado com sucesso", "glbId": "GLB_ID"}')

            self.api = cartolafc.Api(email='email@email.com', password='s3nha')
            self.api_url = self.api._api_url

    def test_amigos(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/auth/amigos'.format(api_url=self.api_url)
            m.get(url, text=self.AMIGOS)
            amigos = self.api.amigos()
            primeiro_time = amigos[0]

            # Assert
            self.assertIsInstance(amigos, list)
            self.assertIsInstance(primeiro_time, TimeInfo)
            self.assertEqual(primeiro_time.time_id, 22463)
            self.assertEqual(primeiro_time.nome, u'UNIÃO BRUNÃO F.C')
            self.assertEqual(primeiro_time.nome_cartola, 'Bruno Nascimento')
            self.assertEqual(primeiro_time.slug, 'uniao-brunao-f-c')
            self.assertFalse(primeiro_time.assinante)


class ApiTest(unittest.TestCase):
    with open('testdata/status_mercado_aberto.json', 'rb') as f:
        STATUS_MERCADO_ABERTO = f.read().decode('utf8')
    with open('testdata/times.json', 'rb') as f:
        TIMES = f.read().decode('utf-8')

    def setUp(self):
        self.api = cartolafc.Api()
        self.api_url = self.api._api_url

    def test_amigos_sem_autenticacao(self):
        # Act and Assert
        with self.assertRaisesRegexp(cartolafc.CartolaFCError, 'Esta função requer autenticação'):
            self.api.amigos()

    def test_status(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
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

    def test_times(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/times'.format(api_url=self.api_url)
            m.get(url, text=self.TIMES)
            times = self.api.times(query='Faly')
            primeiro_time = times[0]

            # Assert
            self.assertIsInstance(times, list)
            self.assertIsInstance(primeiro_time, TimeInfo)
            self.assertEqual(primeiro_time.time_id, 4626963)
            self.assertEqual(primeiro_time.nome, 'Falysson29')
            self.assertEqual(primeiro_time.nome_cartola, 'Alysson')
            self.assertEqual(primeiro_time.slug, 'falysson29')
            self.assertFalse(primeiro_time.assinante)

    def test_servidores_sobrecarregados(self):
        # Arrange
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url)

            # Act and Assert
            with self.assertRaises(cartolafc.CartolaFCOverloadError):
                self.api.status()
