# -*- coding: utf-8 -*-
import unittest
from datetime import datetime

import requests_mock

import cartolafc
from cartolafc.models import (
    Athlete,
    AthleteInfo,
    AthleteScore,
    Club,
    Highlight,
    Position,
    Status
)


class ApiTest(unittest.TestCase):
    with open('testdata/status.json', 'rb') as f:
        STATUS_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/market.json', 'rb') as f:
        MARKET_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/round_score.json', 'rb') as f:
        ROUND_SCORE_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/highlights.json', 'rb') as f:
        HIGHLIGHTS_SAMPLE_JSON = f.read().decode('utf8')

    def setUp(self):
        self.api = cartolafc.Api()
        self.base_url = self.api.base_url

    def test_status(self):
        """Test the cartolafc.Api status method"""

        # Arrange
        url = '%s/mercado/status' % (self.base_url,)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.STATUS_SAMPLE_JSON)
            status = self.api.status()

        # Assert
        self.assertIsInstance(status, Status)
        self.assertEqual(38, status.rodada_atual)
        self.assertEqual('Encerrado', status.status_mercado)
        self.assertEqual(2016, status.temporada)
        self.assertEqual(1702092, status.times_escalados)
        self.assertEqual(datetime.fromtimestamp(1481475600), status.fechamento)
        self.assertEqual(False, status.mercado_pos_rodada)
        self.assertEqual('', status.aviso)

    def test_market(self):
        """Test the cartolafc.Api market method"""

        # Arrange
        url = '%s/atletas/mercado' % (self.base_url,)
        escudos_dict = {
            '60x60': 'https://s.glbimg.com/es/sde/f/equipes/2015/07/21/fluminense_60x60.png',
            '45x45': 'https://s.glbimg.com/es/sde/f/equipes/2015/07/21/fluminense_45x45.png',
            '30x30': 'https://s.glbimg.com/es/sde/f/equipes/2015/07/21/Fluminense-escudo.png'
        }
        scout_dict = {
            'A': 1,
            'CA': 2,
            'FC': 37,
            'FD': 6,
            'FF': 16,
            'FS': 58,
            'G': 4,
            'I': 10,
            'PE': 39,
            'PP': 1,
            'RB': 15
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.MARKET_SAMPLE_JSON)
            market = self.api.market()
            first_athlete = market[0]

        # Assert
        self.assertIsInstance(market, list)
        self.assertIsInstance(first_athlete, Athlete)
        self.assertEqual(92081, first_athlete.atleta_id)
        self.assertEqual('Richarlison Andrade', first_athlete.nome)
        self.assertEqual('Richarlison ', first_athlete.apelido)
        self.assertEqual('https://s.glbimg.com/es/sde/f/2016/04/29/f6f08e1efa5ce7033db704164ac007f7_FORMATO.png',
                         first_athlete.foto)
        self.assertIsInstance(first_athlete.clube, Club)
        self.assertEqual(266, first_athlete.clube.id)
        self.assertEqual('Fluminense', first_athlete.clube.nome)
        self.assertEqual('FLU', first_athlete.clube.abreviacao)
        self.assertEqual(13, first_athlete.clube.posicao)
        self.assertDictEqual(escudos_dict, first_athlete.clube.escudos)
        self.assertIsInstance(first_athlete.posicao, Position)
        self.assertEqual(5, first_athlete.posicao.id)
        self.assertEqual('Atacante', first_athlete.posicao.nome)
        self.assertEqual('ata', first_athlete.posicao.abreviacao)
        self.assertEqual(u'Prov\xe1vel', first_athlete.status)
        self.assertEqual(-0.7, first_athlete.pontos)
        self.assertEqual(6.58, first_athlete.preco)
        self.assertEqual(-0.59, first_athlete.variacao)
        self.assertEqual(2.35, first_athlete.media)
        self.assertEqual(28, first_athlete.jogos)
        self.assertDictEqual(scout_dict, first_athlete.scout)

    def test_round_score(self):
        """Test the cartolafc.Api round_score method"""

        # Arrange
        url = '%s/atletas/pontuados' % (self.base_url,)
        escudos_dict = {
            '60x60': 'https://s.glbimg.com/es/sde/f/equipes/2016/05/03/inter65.png',
            '45x45': 'https://s.glbimg.com/es/sde/f/equipes/2016/05/03/inter45.png',
            '30x30': 'https://s.glbimg.com/es/sde/f/equipes/2016/05/03/inter30.png'
        }
        scout_dict = {
            'FC': 1,
            'G': 1,
            'PE': 1
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.ROUND_SCORE_SAMPLE_JSON)
            round_score = self.api.round_score()
            first_athlete = round_score[0]

        # Assert
        self.assertIsInstance(round_score, list)
        self.assertIsInstance(first_athlete, AthleteScore)
        self.assertEqual('Gustavo Ferrareis', first_athlete.apelido)
        self.assertEqual(7.2, first_athlete.pontuacao)
        self.assertEqual('https://s.glbimg.com/es/sde/f/2016/05/30/581e9d6f1052ed1c3bc00c0fb1bab53a_FORMATO.png',
                         first_athlete.foto)
        self.assertIsInstance(first_athlete.clube, Club)
        self.assertEqual(285, first_athlete.clube.id)
        self.assertEqual('Internacional', first_athlete.clube.nome)
        self.assertEqual('INT', first_athlete.clube.abreviacao)
        self.assertEqual(17, first_athlete.clube.posicao)
        self.assertDictEqual(escudos_dict, first_athlete.clube.escudos)
        self.assertIsInstance(first_athlete.posicao, Position)
        self.assertEqual(4, first_athlete.posicao.id)
        self.assertEqual('Meia', first_athlete.posicao.nome)
        self.assertEqual('mei', first_athlete.posicao.abreviacao)
        self.assertDictEqual(scout_dict, first_athlete.scout)

    def test_highlights(self):
        """Test the cartolafc.Api highlights method"""

        # Arrange
        url = '%s/mercado/destaques' % (self.base_url,)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.HIGHLIGHTS_SAMPLE_JSON)
            highlights = self.api.highlights()
            first_highlight = highlights[0]

        # Assert
        self.assertIsInstance(highlights, list)
        self.assertIsInstance(first_highlight, Highlight)
        self.assertIsInstance(first_highlight.atleta, AthleteInfo)
        self.assertEqual(68911, first_highlight.atleta.atleta_id)
        self.assertEqual('Diego Souza de Andrade', first_highlight.atleta.nome)
        self.assertEqual('Diego Souza', first_highlight.atleta.apelido)
        self.assertEqual('https://s.glbimg.com/es/sde/f/2016/05/01/4ca75c7b4c6ef9d48c9ffe43f89b8f78_FORMATO.png',
                         first_highlight.atleta.foto)
        self.assertEqual(21, first_highlight.atleta.preco_editorial)
        self.assertEqual(843626, first_highlight.escalacoes)
        self.assertEqual('SPO', first_highlight.clube)
        self.assertEqual('https://s.glbimg.com/es/sde/f/equipes/2015/07/21/sport65.png', first_highlight.escudo_clube)
        self.assertEqual('Meia', first_highlight.posicao)
