import unittest
from datetime import datetime

import requests_mock
from requests.status_codes import codes

import cartolafc
from cartolafc.constants import MERCADO_ABERTO
from cartolafc.models import (
    Atleta,
    Clube,
    DestaqueRodada,
    Liga,
    LigaPatrocinador,
    Mercado,
    Partida,
)
from cartolafc.models import Time, TimeInfo
from cartolafc.models import _atleta_status, _posicoes


class ApiAttemptsTest(unittest.TestCase):
    def test_api_attempts_menor_que_1(self):
        # Arrange and Act
        api = cartolafc.Api(attempts=0)

        # Assert
        self.assertEqual(api._attempts, 1)

    def test_api_attempts_com_erros(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            api = cartolafc.Api(attempts=2)

            url = f"{api._api_url}/mercado/status"
            error_message = "Mensagem de erro"
            m.get(url, status_code=codes.ok, text='{"mensagem": "%s"}' % error_message)

            with self.assertRaisesRegex(cartolafc.CartolaFCError, error_message):
                api.mercado()

    def test_api_attempts_com_servidores_sobrecarregados(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            api = cartolafc.Api(attempts=2)

            url = f"{api._api_url}/mercado/status"
            error_message = (
                "Globo.com - Desculpe-nos, nossos servidores estão sobrecarregados."
            )
            m.get(
                url,
                response_list=[
                    dict(
                        status_code=codes.ok, text='{"mensagem": "%s"}}' % error_message
                    ),
                    dict(
                        status_code=codes.ok, text='{"mensagem": "%s"}}' % error_message
                    ),
                ],
            )

            with self.assertRaisesRegex(cartolafc.CartolaFCError, error_message):
                api.mercado()


class ApiTest(unittest.TestCase):
    with open("tests/testdata/clubes.json", "rb") as f:
        CLUBES = f.read().decode("utf8")
    with open("tests/testdata/ligas.json", "rb") as f:
        LIGAS = f.read().decode("utf8")
    with open("tests/testdata/ligas_patrocinadores.json", "rb") as f:
        LIGAS_PATROCINADORES = f.read().decode("utf8")
    with open("tests/testdata/mercado_atletas.json", "rb") as f:
        MERCADO_ATLETAS = f.read().decode("utf8")
    with open("tests/testdata/mercado_status_aberto.json", "rb") as f:
        MERCADO_STATUS_ABERTO = f.read().decode("utf8")
    with open("tests/testdata/mercado_status_fechado.json", "rb") as f:
        MERCADO_STATUS_FECHADO = f.read().decode("utf8")
    with open("tests/testdata/partidas.json", "rb") as f:
        PARTIDAS = f.read().decode("utf8")
    with open("tests/testdata/parciais.json", "rb") as f:
        PARCIAIS = f.read().decode("utf8")
    with open("tests/testdata/pos_rodada_destaques.json", "rb") as f:
        POS_RODADA_DESTAQUES = f.read().decode("utf8")
    with open("tests/testdata/time.json", "rb") as f:
        TIME = f.read().decode("utf8")
    with open("tests/testdata/times.json", "rb") as f:
        TIMES = f.read().decode("utf-8")
    with open("tests/testdata/game_over.json", "rb") as f:
        GAME_OVER = f.read().decode("utf-8")

    def setUp(self):
        self.api = cartolafc.Api()
        self.api_url = self.api._api_url

    def test_clubes(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/clubes"
            m.get(url, text=self.CLUBES)
            clubes = self.api.clubes()
            clube_flamengo = clubes[262]

            # Assert
            self.assertIsInstance(clubes, dict)
            self.assertIsInstance(clube_flamengo, Clube)
            self.assertEqual(clube_flamengo.id, 262)
            self.assertEqual(clube_flamengo.nome, "Flamengo")
            self.assertEqual(clube_flamengo.abreviacao, "FLA")

    def test_ligas(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/ligas"
            m.get(url, text=self.LIGAS)
            ligas = self.api.ligas(query="premiere")
            primeira_liga = ligas[0]

            # Assert
            self.assertIsInstance(ligas, list)
            self.assertIsInstance(primeira_liga, Liga)
            self.assertEqual(primeira_liga.id, 2362309)
            self.assertEqual(primeira_liga.nome, "Time Cartola Oficial")
            self.assertEqual(primeira_liga.slug, "time-cartola-oficial")
            self.assertEqual(primeira_liga.descricao, "Valendo um card no board")
            self.assertIsNone(primeira_liga.times)

    def test_mercado(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url, text=self.MERCADO_STATUS_ABERTO)
            status = self.api.mercado()

            # Assert
            fechamento = datetime(2023, 4, 15, 23, 59)

            self.assertIsInstance(status, Mercado)
            self.assertEqual(status.rodada_atual, 3)
            self.assertEqual(status.status.id, MERCADO_ABERTO)
            self.assertEqual(status.times_escalados, 3601523)
            self.assertIsInstance(status.fechamento, datetime)
            self.assertEqual(status.fechamento, fechamento)

    def test_mercado_atletas(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/atletas/mercado"
            m.get(url, text=self.MERCADO_ATLETAS)
            mercado = self.api.mercado_atletas()
            primeiro_atleta = mercado[0]

            # Assert
            self.assertIsInstance(mercado, list)
            self.assertIsInstance(primeiro_atleta, Atleta)
            self.assertEqual(primeiro_atleta.id, 63013)
            self.assertEqual(primeiro_atleta.apelido, "Marcos Rocha")
            self.assertEqual(primeiro_atleta.pontos, 0)
            self.assertEqual(
                # TODO: Teste com scouts
                primeiro_atleta.scout,
                {},
            )
            self.assertEqual(primeiro_atleta.posicao, _posicoes[2])
            self.assertIsInstance(primeiro_atleta.clube, Clube)
            self.assertEqual(primeiro_atleta.clube.id, 275)
            self.assertEqual(primeiro_atleta.clube.nome, "Palmeiras")
            self.assertEqual(primeiro_atleta.clube.abreviacao, "PAL")
            self.assertEqual(primeiro_atleta.status, _atleta_status[7])

    def test_parciais_mercado_aberto(self):
        # Arrange
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url, text=self.MERCADO_STATUS_ABERTO)

            # Act and Assert
            with self.assertRaisesRegex(
                cartolafc.CartolaFCError,
                "As pontuações parciais só ficam disponíveis com o mercado fechado.",
            ):
                self.api.parciais()

    def test_parciais_mercado_fechado(self):
        # Arrange
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url, text=self.MERCADO_STATUS_FECHADO)

            url = f"{self.api_url}/atletas/pontuados"
            m.get(url, text=self.PARCIAIS)

            # Act
            parciais = self.api.parciais()
            parcial_juan = parciais[36540]

            # Assert
            self.assertIsInstance(parciais, dict)
            self.assertIsInstance(parcial_juan, Atleta)
            self.assertEqual(parcial_juan.id, 36540)
            self.assertEqual(parcial_juan.apelido, "Juan")
            self.assertEqual(parcial_juan.pontos, 2.9)
            self.assertEqual(
                parcial_juan.scout, {"CA": 1, "FC": 1, "FS": 2, "PE": 2, "SG": 1}
            )
            self.assertEqual(parcial_juan.posicao, _posicoes[3])
            self.assertIsInstance(parcial_juan.clube, Clube)
            self.assertEqual(parcial_juan.clube.id, 262)
            self.assertEqual(parcial_juan.clube.nome, "Flamengo")
            self.assertEqual(parcial_juan.clube.abreviacao, "FLA")

    def test_partidas(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/partidas/1"
            m.get(url, text=self.PARTIDAS)
            partidas = self.api.partidas(1)
            primeira_partida = partidas[0]

            # Assert
            self.assertIsInstance(partidas, list)
            self.assertIsInstance(primeira_partida, Partida)
            self.assertIsInstance(primeira_partida.data, datetime)
            # TODO: Teste partidas com local e placar
            # self.assertEqual(primeira_partida.local, "Maracanã")
            self.assertEqual(primeira_partida.clube_casa.nome, "Flamengo")
            # self.assertEqual(primeira_partida.placar_casa, 1)
            self.assertEqual(primeira_partida.clube_visitante.nome, "Coritiba")
            # self.assertEqual(primeira_partida.placar_visitante, 1)

    def test_patrocinadores(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/patrocinadores"
            m.get(url, text=self.LIGAS_PATROCINADORES)
            ligas = self.api.ligas_patrocinadores()
            liga_gato_mestre = ligas[62]

            # Assert
            self.assertIsInstance(ligas, dict)
            self.assertIsInstance(liga_gato_mestre, LigaPatrocinador)
            self.assertEqual(liga_gato_mestre.id, 62)
            self.assertEqual(liga_gato_mestre.nome, "Liga Gato Mestre")
            self.assertEqual(
                liga_gato_mestre.url_link, "https://gatomestre.ge.globo.com/"
            )

    def test_pos_rodada_destaques_com_mercado_aberto(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url, text=self.MERCADO_STATUS_ABERTO)

            url = f"{self.api_url}/pos-rodada/destaques"
            m.get(url, text=self.POS_RODADA_DESTAQUES)
            destaque_rodada = self.api.pos_rodada_destaques()

            # Assert
            self.assertIsInstance(destaque_rodada, DestaqueRodada)
            self.assertEqual(destaque_rodada.media_cartoletas, 115.8235753058391)
            self.assertEqual(destaque_rodada.media_pontos, 46.6480728839843)
            self.assertIsInstance(destaque_rodada.mito_rodada, TimeInfo)
            self.assertEqual(destaque_rodada.mito_rodada.id, 896224)
            self.assertEqual(destaque_rodada.mito_rodada.nome, "gama campos fc")
            self.assertEqual(destaque_rodada.mito_rodada.nome_cartola, "malmal")
            self.assertEqual(destaque_rodada.mito_rodada.slug, "gama-campos-fc")
            self.assertFalse(destaque_rodada.mito_rodada.assinante)

    def test_pos_rodada_destaques_com_mercado_fechado(self):
        # Arrange
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url, text=self.MERCADO_STATUS_FECHADO)

            # Act and Assert
            with self.assertRaisesRegex(cartolafc.CartolaFCError, ""):
                self.api.pos_rodada_destaques()

    def test_time_com_id(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/time/id/471815"
            m.get(url, text=self.TIME)
            time = self.api.time(time_id=471815)
            primeiro_atleta = time.atletas[0] if len(time.atletas) else None

            # Assert
            self.assertIsInstance(time, Time)
            self.assertEqual(time.patrimonio, 100)
            self.assertEqual(time.valor_time, 0)
            # TODO: Revisar depois que a primeira rodada fechar
            # self.assertEqual(time.ultima_pontuacao, 70.02978515625)
            self.assertIsInstance(time.atletas, list)

            # TODO: Revisar depois que a primeira rodada fechar
            if primeiro_atleta:
                self.assertIsInstance(primeiro_atleta, Atleta)
                self.assertEqual(primeiro_atleta.id, 38140)
                self.assertEqual(primeiro_atleta.apelido, "Fernando Prass")
                self.assertEqual(primeiro_atleta.pontos, 7.5)
                self.assertEqual(primeiro_atleta.scout, {"DD": 3, "FS": 1, "GS": 1})
                self.assertEqual(primeiro_atleta.posicao, _posicoes[1])
                self.assertIsInstance(primeiro_atleta.clube, Clube)
                self.assertEqual(primeiro_atleta.clube.id, 275)
                self.assertEqual(primeiro_atleta.clube.nome, "Palmeiras")
                self.assertEqual(primeiro_atleta.clube.abreviacao, "PAL")
                self.assertEqual(primeiro_atleta.status, _atleta_status[7])

            self.assertIsInstance(time.info, TimeInfo)
            self.assertEqual(time.info.id, 471815)
            self.assertEqual(time.info.nome, "Falydos FC")
            self.assertEqual(time.info.nome_cartola, "Vicente Neto")
            self.assertEqual(time.info.slug, "falydos-fc")
            self.assertTrue(time.info.assinante)

    def test_time_parcial_mercado_aberto(self):
        # Arrange
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url, text=self.MERCADO_STATUS_ABERTO)

            # Act and Assert
            with self.assertRaisesRegex(
                cartolafc.CartolaFCError,
                "As pontuações parciais só ficam disponíveis com o mercado fechado.",
            ):
                self.api.time_parcial(471815)

    def test_time_parcial_mercado_fechado(self):
        # Arrange
        with requests_mock.mock() as m:
            mercado_url = f"{self.api_url}/mercado/status"
            parciais_url = f"{self.api_url}/atletas/pontuados"
            time_url = f"{self.api_url}/time/id/471815"

            m.get(mercado_url, text=self.MERCADO_STATUS_FECHADO)
            m.get(parciais_url, text=self.PARCIAIS)
            m.get(time_url, text=self.TIME)

            time = self.api.time_parcial(471815)
            primeiro_atleta = time.atletas[0] if len(time.atletas) else None

            # Assert
            self.assertIsInstance(time, Time)
            self.assertEqual(time.patrimonio, 100)
            self.assertEqual(time.valor_time, 0)
            # TODO: Revisar depois que a primeira rodada fechar
            # self.assertEqual(time.ultima_pontuacao, 70.02978515625)
            # self.assertEqual(time.pontos, 13.299999999999999)
            self.assertIsInstance(time.atletas, list)

            # TODO: Revisar depois que a primeira rodada fechar
            if primeiro_atleta:
                self.assertIsInstance(primeiro_atleta, Atleta)
                self.assertEqual(primeiro_atleta.id, 38140)
                self.assertEqual(primeiro_atleta.apelido, "Fernando Prass")
                self.assertEqual(primeiro_atleta.pontos, 0)
                self.assertEqual(primeiro_atleta.scout, {})
                self.assertEqual(primeiro_atleta.posicao, _posicoes[1])
                self.assertIsInstance(primeiro_atleta.clube, Clube)
                self.assertEqual(primeiro_atleta.clube.id, 275)
                self.assertEqual(primeiro_atleta.clube.nome, "Palmeiras")
                self.assertEqual(primeiro_atleta.clube.abreviacao, "PAL")
                self.assertEqual(primeiro_atleta.status, _atleta_status[7])

            self.assertIsInstance(time.info, TimeInfo)
            self.assertEqual(time.info.id, 471815)
            self.assertEqual(time.info.nome, "Falydos FC")
            self.assertEqual(time.info.nome_cartola, "Vicente Neto")
            self.assertEqual(time.info.slug, "falydos-fc")
            self.assertTrue(time.info.assinante)

    def test_time_parcial_key_invalida(self):
        # Arrange
        with requests_mock.mock() as m:
            error_message = "Time ou parciais não são válidos."
            time_url = f"{self.api_url}/time/id/471815"

            m.get(time_url, text=self.TIME)

            with self.assertRaisesRegex(cartolafc.CartolaFCError, error_message):
                self.api.time_parcial(time_id=471815, parciais=dict(key="valor"))

    def test_time_parcial_valor_invalido(self):
        # Arrange
        with requests_mock.mock() as m:
            error_message = "Time ou parciais não são válidos."
            time_url = f"{self.api_url}/time/id/471815"

            m.get(time_url, text=self.TIME)

            with self.assertRaisesRegex(cartolafc.CartolaFCError, error_message):
                self.api.time_parcial(time_id=471815, parciais={1: "valor"})

    def test_times(self):
        # Arrange and Act
        with requests_mock.mock() as m:
            url = f"{self.api_url}/times"
            m.get(url, text=self.TIMES)
            times = self.api.times(query="Faly")
            primeiro_time = times[0]

            # Assert
            self.assertIsInstance(times, list)
            self.assertIsInstance(primeiro_time, TimeInfo)
            self.assertEqual(primeiro_time.id, 471815)
            self.assertEqual(primeiro_time.nome, "Falydos FC")
            self.assertEqual(primeiro_time.nome_cartola, "Vicente Neto")
            self.assertEqual(primeiro_time.slug, "falydos-fc")
            self.assertTrue(primeiro_time.assinante)

    def test_servidores_sobrecarregados(self):
        # Arrange
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url)

            # Act and Assert
            with self.assertRaises(cartolafc.CartolaFCOverloadError):
                self.api.mercado()

    def test_game_over(self):
        # Arrange
        with requests_mock.mock() as m:
            url = f"{self.api_url}/mercado/status"
            m.get(url, text=self.GAME_OVER)

            # Act and Assert
            with self.assertRaises(cartolafc.CartolaFCGameOverError):
                self.api.mercado()
