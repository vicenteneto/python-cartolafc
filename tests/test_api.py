# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

import requests_mock
from requests.status_codes import codes

import cartolafc
from cartolafc.api import MERCADO_ABERTO
from cartolafc.models import Atleta, Clube, DestaqueRodada, Liga, LigaPatrocinador, Mercado, Partida, PontuacaoInfo
from cartolafc.models import Time, TimeInfo
from cartolafc.models import _atleta_status, _posicoes


class ApiAttemptsTest(unittest.TestCase):
    def test_api_attempts_nao_inteiro(self):
        # Arrange and Act
        api = cartolafc.Api(attempts='texto')

        # Assert
        self.assertEqual(api._attempts, 1)

    def test_api_attempts_menor_que_1(self):
        # Arrange and Act
        api = cartolafc.Api(attempts=0)

        # Assert
        self.assertEqual(api._attempts, 1)

    def test_api_attempts(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            api = cartolafc.Api(attempts=2)

            url = '{api_url}/mercado/status'.format(api_url=api._api_url)
            error_message = 'Mensagem de erro'
            m.get(url, status_code=codes.ok, text='{"mensagem": "%s"}' % error_message)

            with self.assertRaisesRegex(cartolafc.CartolaFCError, error_message):
                api.mercado()


class ApiAuthTest(unittest.TestCase):
    def test_api_auth_sem_email(self):
        # Act and Assert
        with self.assertRaisesRegex(cartolafc.CartolaFCError, 'E-mail ou senha ausente'):
            cartolafc.Api(password='s3nha')

    def test_api_auth_sem_password(self):
        # Act and Assert
        with self.assertRaisesRegex(cartolafc.CartolaFCError, 'E-mail ou senha ausente'):
            cartolafc.Api(email='email@email.com')

    def test_api_auth_invalida(self):
        # Arrange
        with requests_mock.mock() as m:
            user_message = 'Seu e-mail ou senha estao incorretos.'
            m.post('https://login.globo.com/api/authentication', status_code=codes.unauthorized,
                   text='{"id": "BadCredentials", "userMessage": "%s"}' % user_message)

            # Act and Assert
            with self.assertRaisesRegex(cartolafc.CartolaFCError, user_message):
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
            m.get(url, status_code=codes.unauthorized)

            # Act and Assert
            with self.assertRaises(cartolafc.CartolaFCOverloadError):
                api.mercado()


class ApiRedisTest(unittest.TestCase):
    with open('testdata/mercado_status_aberto.json', 'rb') as f:
        MERCADO_STATUS_ABERTO = f.read().decode('utf8')

    def setUp(self):
        with requests_mock.mock() as m:
            m.post('https://login.globo.com/api/authentication',
                   text='{"id": "Authenticated", "userMessage": "Usuario autenticado com sucesso", "glbId": "GLB_ID"}')

            self.api = cartolafc.Api(email='email@email.com', password='s3nha', redis_url='redis://localhost:6379/0')
            self.api_url = self.api._api_url

    def test_api_redis_invalid_server(self):
        # Act and Assert
        with self.assertRaisesRegex(cartolafc.CartolaFCError, 'Erro conectando ao servidor Redis.'):
            cartolafc.Api(redis_url='redis://localhost:1234')

    def test_api_redis_invalid_url(self):
        # Arrange
        api = cartolafc.Api(redis_url='invalid-url')

        # Act and Assert
        self.assertTrue(api._redis.ping())

    def test_mercado_with_redis_hit(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_ABERTO)
            status = self.api.mercado()

            # Assert
            self.assertIsInstance(status, Mercado)
            self.assertEqual(status.rodada_atual, 3)
            self.assertEqual(status.status.id, MERCADO_ABERTO)
            self.assertEqual(status.times_escalados, 3601523)
            self.assertIsInstance(status.fechamento, datetime)
            self.assertEqual(status.fechamento, datetime.fromtimestamp(1495904400))
            self.assertEqual(status.aviso, '')

    def test_mercado_with_redis_miss(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_ABERTO)
            status = self.api.mercado()

            # Assert
            self.assertIsInstance(status, Mercado)
            self.assertEqual(status.rodada_atual, 3)
            self.assertEqual(status.status.id, MERCADO_ABERTO)
            self.assertEqual(status.times_escalados, 3601523)
            self.assertIsInstance(status.fechamento, datetime)
            self.assertEqual(status.fechamento, datetime.fromtimestamp(1495904400))
            self.assertEqual(status.aviso, '')


class ApiAuthenticatedTest(unittest.TestCase):
    with open('testdata/amigos.json', 'rb') as f:
        AMIGOS = f.read().decode('utf8')
    with open('testdata/liga.json', 'rb') as f:
        LIGA = f.read().decode('utf8')
    with open('testdata/pontuacao_atleta.json', 'rb') as f:
        PONTUACAO_ATLETA = f.read().decode('utf8')
    with open('testdata/time_logado.json', 'rb') as f:
        TIME_LOGADO = f.read().decode('utf8')

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
            self.assertEqual(primeiro_time.id, 22463)
            self.assertEqual(primeiro_time.nome, u'UNIÃO BRUNÃO F.C')
            self.assertEqual(primeiro_time.nome_cartola, 'Bruno Nascimento')
            self.assertEqual(primeiro_time.slug, 'uniao-brunao-f-c')
            self.assertFalse(primeiro_time.assinante)

    def test_liga_sem_nome_e_slug(self):
        # Act and Assert
        with self.assertRaisesRegex(cartolafc.CartolaFCError,
                                    'Você precisa informar o nome ou o slug da liga que deseja obter'):
            self.api.liga()

    def test_liga_com_nome(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/auth/liga/{slug}'.format(api_url=self.api_url, slug='falydos-fc')
            m.get(url, text=self.LIGA)
            liga = self.api.liga(nome='Falydos FC')
            primeiro_time = liga.times[0]

            # Assert
            self.assertIsInstance(liga, Liga)
            self.assertEqual(liga.id, 6407)
            self.assertEqual(liga.nome, 'Virtus Premier League')
            self.assertEqual(liga.slug, 'virtus-premier-league')
            self.assertEqual(liga.descricao,
                             u'Prêmios para: \n\n- Melhor de cada Mês (R$50,00)\n- Melhor do 1º e 2º Turno (R$150,00)\n- 2º Lugar Geral (R$50)\n- 1º Lugar Geral (R$250,00)\n\nBoa sorte!')
            self.assertIsInstance(liga.times, list)
            self.assertIsInstance(primeiro_time, TimeInfo)
            self.assertEqual(primeiro_time.id, 453420)
            self.assertEqual(primeiro_time.nome, 'Mosqueteiros JPB')
            self.assertEqual(primeiro_time.nome_cartola, 'Erick Costa')
            self.assertEqual(primeiro_time.slug, 'mosqueteiros-jpb')
            self.assertTrue(primeiro_time.assinante)

    def test_liga_com_slug(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/auth/liga/{slug}'.format(api_url=self.api_url, slug='falydos-fc')
            m.get(url, text=self.LIGA)
            liga = self.api.liga(slug='falydos-fc')

            # Assert
            self.assertIsInstance(liga, Liga)

    def test_liga_com_nome_e_slug(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/auth/liga/{slug}'.format(api_url=self.api_url, slug='falydos-fc')
            m.get(url, text=self.LIGA)
            liga = self.api.liga(nome='Falydos FC', slug='falydos-fc')

            # Assert
            self.assertIsInstance(liga, Liga)

    def test_pontuacao_atleta(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/auth/mercado/atleta/{id}/pontuacao'.format(api_url=self.api_url, id=81682)
            m.get(url, text=self.PONTUACAO_ATLETA)
            pontuacoes = self.api.pontuacao_atleta(81682)
            primeira_rodada = pontuacoes[0]

            # Assert
            self.assertIsInstance(pontuacoes, list)
            self.assertIsInstance(primeira_rodada, PontuacaoInfo)
            self.assertEqual(primeira_rodada.atleta_id, 81682)
            self.assertEqual(primeira_rodada.rodada_id, 1)
            self.assertEqual(primeira_rodada.pontos, 1.1)
            self.assertEqual(primeira_rodada.preco, 6.44)
            self.assertEqual(primeira_rodada.variacao, -1.56)
            self.assertEqual(primeira_rodada.media, 1.1)

    def test_time_logado(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/auth/time'.format(api_url=self.api_url)
            m.get(url, text=self.TIME_LOGADO)
            time = self.api.time_logado()
            primeiro_atleta = time.atletas[0]

            # Assert
            self.assertIsInstance(time, Time)
            self.assertEqual(time.patrimonio, 144.74)
            self.assertEqual(time.valor_time, 143.84961)
            self.assertEqual(time.ultima_pontuacao, 70.02978515625)
            self.assertIsInstance(time.atletas, list)
            self.assertIsInstance(primeiro_atleta, Atleta)
            self.assertEqual(primeiro_atleta.id, 38140)
            self.assertEqual(primeiro_atleta.apelido, 'Fernando Prass')
            self.assertEqual(primeiro_atleta.pontos, 7.5)
            self.assertEqual(primeiro_atleta.scout, {'DD': 5, 'FS': 1, 'GS': 1, 'PE': 1, 'SG': 1})
            self.assertEqual(primeiro_atleta.posicao, _posicoes[1])
            self.assertIsInstance(primeiro_atleta.clube, Clube)
            self.assertEqual(primeiro_atleta.clube.id, 275)
            self.assertEqual(primeiro_atleta.clube.nome, 'Palmeiras')
            self.assertEqual(primeiro_atleta.clube.abreviacao, 'PAL')
            self.assertEqual(primeiro_atleta.status, _atleta_status[7])
            self.assertIsInstance(time.info, TimeInfo)
            self.assertEqual(time.info.id, 471815)
            self.assertEqual(time.info.nome, 'Falydos FC')
            self.assertEqual(time.info.nome_cartola, 'Vicente Neto')
            self.assertEqual(time.info.slug, 'falydos-fc')
            self.assertTrue(time.info.assinante)


class ApiTest(unittest.TestCase):
    with open('testdata/clubes.json', 'rb') as f:
        CLUBES = f.read().decode('utf8')
    with open('testdata/ligas.json', 'rb') as f:
        LIGAS = f.read().decode('utf8')
    with open('testdata/ligas_patrocinadores.json', 'rb') as f:
        LIGAS_PATROCINADORES = f.read().decode('utf8')
    with open('testdata/mercado_atletas.json', 'rb') as f:
        MERCADO_ATLETAS = f.read().decode('utf8')
    with open('testdata/mercado_status_aberto.json', 'rb') as f:
        MERCADO_STATUS_ABERTO = f.read().decode('utf8')
    with open('testdata/mercado_status_fechado.json', 'rb') as f:
        MERCADO_STATUS_FECHADO = f.read().decode('utf8')
    with open('testdata/partidas.json', 'rb') as f:
        PARTIDAS = f.read().decode('utf8')
    with open('testdata/parciais.json', 'rb') as f:
        PARCIAIS = f.read().decode('utf8')
    with open('testdata/pos_rodada_destaques.json', 'rb') as f:
        POS_RODADA_DESTAQUES = f.read().decode('utf8')
    with open('testdata/time.json', 'rb') as f:
        TIME = f.read().decode('utf8')
    with open('testdata/times.json', 'rb') as f:
        TIMES = f.read().decode('utf-8')

    def setUp(self):
        self.api = cartolafc.Api()
        self.api_url = self.api._api_url

    def test_amigos_sem_autenticacao(self):
        # Act and Assert
        with self.assertRaisesRegex(cartolafc.CartolaFCError, 'Esta função requer autenticação'):
            self.api.amigos()

    def test_clubes(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/clubes'.format(api_url=self.api_url)
            m.get(url, text=self.CLUBES)
            clubes = self.api.clubes()
            clube_flamengo = clubes[262]

            # Assert
            self.assertIsInstance(clubes, dict)
            self.assertIsInstance(clube_flamengo, Clube)
            self.assertEqual(clube_flamengo.id, 262)
            self.assertEqual(clube_flamengo.nome, 'Flamengo')
            self.assertEqual(clube_flamengo.abreviacao, 'FLA')

    def test_ligas(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/ligas'.format(api_url=self.api_url)
            m.get(url, text=self.LIGAS)
            ligas = self.api.ligas(query='premiere')
            primeira_liga = ligas[0]

            # Assert
            self.assertIsInstance(ligas, list)
            self.assertIsInstance(primeira_liga, Liga)
            self.assertEqual(primeira_liga.id, 36741)
            self.assertEqual(primeira_liga.nome, 'PREMIERE_LIGA_ENTEL')
            self.assertEqual(primeira_liga.slug, 'premiere-liga-entel')
            self.assertEqual(primeira_liga.descricao, u'“Vale tudo, só não vale...”')
            self.assertIsNone(primeira_liga.times)

    def test_mercado(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_ABERTO)
            status = self.api.mercado()

            # Assert
            self.assertIsInstance(status, Mercado)
            self.assertEqual(status.rodada_atual, 3)
            self.assertEqual(status.status.id, MERCADO_ABERTO)
            self.assertEqual(status.times_escalados, 3601523)
            self.assertIsInstance(status.fechamento, datetime)
            self.assertEqual(status.fechamento, datetime.fromtimestamp(1495904400))
            self.assertEqual(status.aviso, '')

    def test_mercado_atletas(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/atletas/mercado'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_ATLETAS)
            mercado = self.api.mercado_atletas()
            primeiro_atleta = mercado[0]

            # Assert
            self.assertIsInstance(mercado, list)
            self.assertIsInstance(primeiro_atleta, Atleta)
            self.assertEqual(primeiro_atleta.id, 86935)
            self.assertEqual(primeiro_atleta.apelido, 'Rodrigo')
            self.assertEqual(primeiro_atleta.pontos, 0)
            self.assertEqual(primeiro_atleta.scout, {'CA': 1, 'FC': 3, 'FS': 1, 'PE': 2, 'RB': 2})
            self.assertEqual(primeiro_atleta.posicao, _posicoes[4])
            self.assertIsInstance(primeiro_atleta.clube, Clube)
            self.assertEqual(primeiro_atleta.clube.id, 292)
            self.assertEqual(primeiro_atleta.clube.nome, 'Sport')
            self.assertEqual(primeiro_atleta.clube.abreviacao, 'SPO')
            self.assertEqual(primeiro_atleta.status, _atleta_status[6])

    def test_parciais_mercado_aberto(self):
        # Arrange
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_ABERTO)

            # Act and Assert
            with self.assertRaisesRegex(cartolafc.CartolaFCError,
                                        'As pontuações parciais só ficam disponíveis com o mercado fechado.'):
                self.api.parciais()

    def test_parciais_mercado_fechado(self):
        # Arrange
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_FECHADO)

            url = '{api_url}/atletas/pontuados'.format(api_url=self.api_url)
            m.get(url, text=self.PARCIAIS)

            # Act
            parciais = self.api.parciais()
            parcial_juan = parciais[36540]

            # Assert
            self.assertIsInstance(parciais, dict)
            self.assertIsInstance(parcial_juan, Atleta)
            self.assertEqual(parcial_juan.id, 36540)
            self.assertEqual(parcial_juan.apelido, 'Juan')
            self.assertEqual(parcial_juan.pontos, 2.9)
            self.assertEqual(parcial_juan.scout, {'CA': 1, 'FC': 1, 'FS': 2, 'PE': 2, 'SG': 1})
            self.assertEqual(parcial_juan.posicao, _posicoes[3])
            self.assertIsInstance(parcial_juan.clube, Clube)
            self.assertEqual(parcial_juan.clube.id, 262)
            self.assertEqual(parcial_juan.clube.nome, 'Flamengo')
            self.assertEqual(parcial_juan.clube.abreviacao, 'FLA')

    def test_partidas(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/partidas/{rodada}'.format(api_url=self.api_url, rodada=1)
            m.get(url, text=self.PARTIDAS)
            partidas = self.api.partidas(1)
            primeira_partida = partidas[0]

            # Assert
            self.assertIsInstance(partidas, list)
            self.assertIsInstance(primeira_partida, Partida)
            self.assertIsInstance(primeira_partida.data, datetime)
            self.assertEqual(primeira_partida.local, u'Maracanã')
            self.assertEqual(primeira_partida.clube_casa.nome, 'Flamengo')
            self.assertEqual(primeira_partida.placar_casa, 1)
            self.assertEqual(primeira_partida.clube_visitante.nome, u'Atlético-MG')
            self.assertEqual(primeira_partida.placar_visitante, 1)

    def test_patrocinadores(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/patrocinadores'.format(api_url=self.api_url)
            m.get(url, text=self.LIGAS_PATROCINADORES)
            ligas = self.api.ligas_patrocinadores()
            liga_brahma = ligas[62]

            # Assert
            self.assertIsInstance(ligas, dict)
            self.assertIsInstance(liga_brahma, LigaPatrocinador)
            self.assertEqual(liga_brahma.id, 62)
            self.assertEqual(liga_brahma.nome, 'Cerveja Brahma')
            self.assertEqual(liga_brahma.url_link, 'http://brahma.com.br')

    def test_pos_rodada_destaques_com_mercado_aberto(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_ABERTO)

            url = '{api_url}/pos-rodada/destaques'.format(api_url=self.api_url)
            m.get(url, text=self.POS_RODADA_DESTAQUES)
            destaque_rodada = self.api.pos_rodada_destaques()

            # Assert
            self.assertIsInstance(destaque_rodada, DestaqueRodada)
            self.assertEqual(destaque_rodada.media_cartoletas, 115.8235753058391)
            self.assertEqual(destaque_rodada.media_pontos, 46.6480728839843)
            self.assertIsInstance(destaque_rodada.mito_rodada, TimeInfo)
            self.assertEqual(destaque_rodada.mito_rodada.id, 896224)
            self.assertEqual(destaque_rodada.mito_rodada.nome, 'gama campos fc')
            self.assertEqual(destaque_rodada.mito_rodada.nome_cartola, 'malmal')
            self.assertEqual(destaque_rodada.mito_rodada.slug, 'gama-campos-fc')
            self.assertFalse(destaque_rodada.mito_rodada.assinante)

    def test_pos_rodada_destaques_com_mercado_fechado(self):
        # Arrange
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_FECHADO)

            # Act and Assert
            with self.assertRaisesRegex(cartolafc.CartolaFCError, ''):
                self.api.pos_rodada_destaques()

    def test_time_sem_id_sem_nome_e_sem_slug(self):
        # Act and Assert
        with self.assertRaisesRegex(cartolafc.CartolaFCError,
                                    'Você precisa informar o nome ou o slug do time que deseja obter'):
            self.api.time()

    def test_time_com_id(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/time/id/{id}'.format(api_url=self.api_url, id=471815)
            m.get(url, text=self.TIME)
            time = self.api.time(id=471815)
            primeiro_atleta = time.atletas[0]

            # Assert
            self.assertIsInstance(time, Time)
            self.assertEqual(time.patrimonio, 0)
            self.assertEqual(time.valor_time, 0)
            self.assertEqual(time.ultima_pontuacao, 70.02978515625)
            self.assertIsInstance(time.atletas, list)
            self.assertIsInstance(primeiro_atleta, Atleta)
            self.assertEqual(primeiro_atleta.id, 38140)
            self.assertEqual(primeiro_atleta.apelido, 'Fernando Prass')
            self.assertEqual(primeiro_atleta.pontos, 7.5)
            self.assertEqual(primeiro_atleta.scout, {'DD': 3, 'FS': 1, 'GS': 1})
            self.assertEqual(primeiro_atleta.posicao, _posicoes[1])
            self.assertIsInstance(primeiro_atleta.clube, Clube)
            self.assertEqual(primeiro_atleta.clube.id, 275)
            self.assertEqual(primeiro_atleta.clube.nome, 'Palmeiras')
            self.assertEqual(primeiro_atleta.clube.abreviacao, 'PAL')
            self.assertEqual(primeiro_atleta.status, _atleta_status[7])
            self.assertIsInstance(time.info, TimeInfo)
            self.assertEqual(time.info.id, 471815)
            self.assertEqual(time.info.nome, 'Falydos FC')
            self.assertEqual(time.info.nome_cartola, 'Vicente Neto')
            self.assertEqual(time.info.slug, 'falydos-fc')
            self.assertTrue(time.info.assinante)

    def test_time_com_nome(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/time/slug/{slug}'.format(api_url=self.api_url, slug='falydos-fc')
            m.get(url, text=self.TIME)
            time = self.api.time(nome='Falydos FC')

            # Assert
            self.assertIsInstance(time, Time)

    def test_time_com_slug(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/time/slug/{slug}'.format(api_url=self.api_url, slug='falydos-fc')
            m.get(url, text=self.TIME)
            time = self.api.time(slug='falydos-fc')

            # Assert
            self.assertIsInstance(time, Time)

    def test_time_com_id_com_nome_e_com_slug(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/time/id/{id}'.format(api_url=self.api_url, id=471815)
            m.get(url, text=self.TIME)
            time = self.api.time(id=471815, nome='Falydos FC', slug='falydos-fc')

            # Assert
            self.assertIsInstance(time, Time)

    def test_time_com_json(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = '{api_url}/time/id/{id}'.format(api_url=self.api_url, id=471815)
            m.get(url, text=self.TIME)
            time = self.api.time(id=471815, as_json=True)

            # Assert
            self.assertIsInstance(time, dict)

    def test_time_parcial_mercado_aberto(self):
        # Arrange
        with requests_mock.mock() as m:
            url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            m.get(url, text=self.MERCADO_STATUS_ABERTO)

            # Act and Assert
            with self.assertRaisesRegex(cartolafc.CartolaFCError,
                                        'As pontuações parciais só ficam disponíveis com o mercado fechado.'):
                self.api.time_parcial(nome='Falydos FC')

    def test_time_parcial_mercado_fechado(self):
        # Arrange
        with requests_mock.mock() as m:
            mercado_url = '{api_url}/mercado/status'.format(api_url=self.api_url)
            parciais_url = '{api_url}/atletas/pontuados'.format(api_url=self.api_url)
            time_url = '{api_url}/time/slug/falydos-fc'.format(api_url=self.api_url)

            m.get(mercado_url, text=self.MERCADO_STATUS_FECHADO)
            m.get(parciais_url, text=self.PARCIAIS)
            m.get(time_url, text=self.TIME)

            time = self.api.time_parcial(nome='Falydos FC')
            primeiro_atleta = time.atletas[0]

            # Assert
            self.assertIsInstance(time, Time)
            self.assertEqual(time.patrimonio, 0)
            self.assertEqual(time.valor_time, 0)
            self.assertEqual(time.ultima_pontuacao, 70.02978515625)
            self.assertEqual(time.pontos, 13.299999999999999)
            self.assertIsInstance(time.atletas, list)
            self.assertIsInstance(primeiro_atleta, Atleta)
            self.assertEqual(primeiro_atleta.id, 38140)
            self.assertEqual(primeiro_atleta.apelido, 'Fernando Prass')
            self.assertEqual(primeiro_atleta.pontos, 0)
            self.assertEqual(primeiro_atleta.scout, {})
            self.assertEqual(primeiro_atleta.posicao, _posicoes[1])
            self.assertIsInstance(primeiro_atleta.clube, Clube)
            self.assertEqual(primeiro_atleta.clube.id, 275)
            self.assertEqual(primeiro_atleta.clube.nome, 'Palmeiras')
            self.assertEqual(primeiro_atleta.clube.abreviacao, 'PAL')
            self.assertEqual(primeiro_atleta.status, _atleta_status[7])
            self.assertIsInstance(time.info, TimeInfo)
            self.assertEqual(time.info.id, 471815)
            self.assertEqual(time.info.nome, 'Falydos FC')
            self.assertEqual(time.info.nome_cartola, 'Vicente Neto')
            self.assertEqual(time.info.slug, 'falydos-fc')
            self.assertTrue(time.info.assinante)

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
            self.assertEqual(primeiro_time.id, 4626963)
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
                self.api.mercado()
