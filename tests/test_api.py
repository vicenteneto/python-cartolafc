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
    LeagueInfo,
    Match,
    Position,
    Round,
    RoundHighlights,
    Scheme,
    Sponsor,
    Status,
    Team,
    TeamInfo
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
    with open('testdata/round_highlights.json', 'rb') as f:
        ROUND_HIGHLIGHTS_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/sponsors.json', 'rb') as f:
        SPONSORS_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/schemes.json', 'rb') as f:
        SCHEMES_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/rounds.json', 'rb') as f:
        ROUNDS_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/matches.json', 'rb') as f:
        MATCHES_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/clubs.json', 'rb') as f:
        CLUBS_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/search_team.json', 'rb') as f:
        SEARCH_TEAM_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/get_team.json', 'rb') as f:
        GET_TEAM_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/get_team_by_round.json', 'rb') as f:
        GET_TEAM_BY_ROUND_SAMPLE_JSON = f.read().decode('utf8')
    with open('testdata/search_league.json', 'rb') as f:
        SEARCH_LEAGUE_SAMPLE_JSON = f.read().decode('utf8')

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
        self.assertEqual('Mercado encerrado', status.status_mercado)
        self.assertEqual(2016, status.temporada)
        self.assertEqual(1702092, status.times_escalados)
        self.assertIsInstance(status.fechamento, datetime)
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
            '60x60': 'https://s.glbimg.com/es/sde/f/equipes/2014/04/14/flamengo_60x60.png',
            '45x45': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_45x45.png',
            '30x30': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_30x30.png'
        }
        scout_dict = {
            'CA': 1,
            'FC': 1,
            'FS': 2,
            'PE': 2,
            'SG': 1
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.ROUND_SCORE_SAMPLE_JSON)
            round_score = self.api.round_score()
            first_athlete = round_score['36540']

        # Assert
        self.assertIsInstance(round_score, dict)
        self.assertIsInstance(first_athlete, AthleteScore)
        self.assertEqual('Juan', first_athlete.apelido)
        self.assertEqual(2.9, first_athlete.pontuacao)
        self.assertEqual('https://s.glbimg.com/es/sde/f/2016/04/20/cac9ebd94cc82a0b98f4055f9667d4e6_FORMATO.png',
                         first_athlete.foto)
        self.assertIsInstance(first_athlete.clube, Club)
        self.assertEqual(262, first_athlete.clube.id)
        self.assertEqual('Flamengo', first_athlete.clube.nome)
        self.assertEqual('FLA', first_athlete.clube.abreviacao)
        self.assertEqual(3, first_athlete.clube.posicao)
        self.assertDictEqual(escudos_dict, first_athlete.clube.escudos)
        self.assertIsInstance(first_athlete.posicao, Position)
        self.assertEqual(3, first_athlete.posicao.id)
        self.assertEqual('Zagueiro', first_athlete.posicao.nome)
        self.assertEqual('zag', first_athlete.posicao.abreviacao)
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

    def test_round_highlights(self):
        """Test the cartolafc.Api round_highlights method"""

        # Arrange
        url = '%s/pos-rodada/destaques' % (self.base_url,)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.ROUND_HIGHLIGHTS_SAMPLE_JSON)
            round_highlights = self.api.round_highlights()

        # Assert
        self.assertIsInstance(round_highlights, RoundHighlights)
        self.assertEqual(128.04772232227782, round_highlights.media_cartoletas)
        self.assertEqual(31.459999543855716, round_highlights.media_pontos)
        self.assertIsInstance(round_highlights.mito_rodada, TeamInfo)
        self.assertEqual(1549512, round_highlights.mito_rodada.time_id)
        self.assertEqual(262, round_highlights.mito_rodada.clube_id)
        self.assertEqual(3, round_highlights.mito_rodada.esquema_id)
        self.assertIsNone(round_highlights.mito_rodada.facebook_id)
        self.assertEqual('https://cartolafc.globo.com/static/img/placeholder_perfil.png',
                         round_highlights.mito_rodada.foto_perfil)
        self.assertEqual('MB2 F.C', round_highlights.mito_rodada.nome)
        self.assertEqual(u'M\xe1rio Barreto', round_highlights.mito_rodada.nome_cartola)
        self.assertEqual('mb2-f-c', round_highlights.mito_rodada.slug)
        self.assertEqual('https://s2.glbimg.com/OdFgAz9xQCNxWwWoPQ2CzQlv0bs=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_22/escudo/64/58/51/004169596420160826015851',
                         round_highlights.mito_rodada.url_escudo_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_22/escudo/64/58/'
                         '51/004169596420160826015851', round_highlights.mito_rodada.url_escudo_svg)
        self.assertEqual('https://s2.glbimg.com/UIUs5mFAyFMxyZ51ne8qAFjQyvI=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_22/camisa/64/58/51/004169596420160826015851',
                         round_highlights.mito_rodada.url_camisa_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_22/camisa/64/58/'
                         '51/004169596420160826015851', round_highlights.mito_rodada.url_camisa_svg)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/placeholder/escudo.png',
                         round_highlights.mito_rodada.url_escudo_placeholder_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/placeholder/camisa.png',
                         round_highlights.mito_rodada.url_camisa_placeholder_png)
        self.assertFalse(round_highlights.mito_rodada.assinante)

    def test_sponsors(self):
        """Test the cartolafc.Api sponsors method"""

        # Arrange
        url = '%s/patrocinadores' % (self.base_url,)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.SPONSORS_SAMPLE_JSON)
            sponsors = self.api.sponsors()
            first_sponsor = sponsors['62']

        # Assert
        self.assertIsInstance(sponsors, dict)
        self.assertIsInstance(first_sponsor, Sponsor)
        self.assertEqual(2, first_sponsor.liga_editorial_id)
        self.assertEqual(62, first_sponsor.liga_id)
        self.assertEqual('mes', first_sponsor.tipo_ranking)
        self.assertEqual('http://www.listerine.com.br/', first_sponsor.url_link)
        self.assertEqual('http://globoesporte.globo.com/cartola-fc/ep/monstros/listerine/monstro-listerine/',
                         first_sponsor.url_editoria_ge)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/default/background-liga/'
                         'header-liga-monstro-listerine.jpg', first_sponsor.img_background)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/default/patrocinador/'
                         'marca-listerine.svg', first_sponsor.img_marca_patrocinador)
        self.assertEqual('#SOLTAESSEMONSTRO', first_sponsor.nome)

    def test_rounds(self):
        """Test the cartolafc.Api rounds method"""

        # Arrange
        url = '%s/rodadas' % (self.base_url,)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.ROUNDS_SAMPLE_JSON)
            rounds = self.api.rounds()
            first_round = rounds[0]

        # Assert
        self.assertIsInstance(rounds, list)
        self.assertIsInstance(first_round, Round)
        self.assertEqual(1, first_round.rodada_id)
        self.assertIsInstance(first_round.inicio, datetime)
        self.assertEqual(datetime(2016, 5, 14, 16), first_round.inicio)
        self.assertIsInstance(first_round.fim, datetime)
        self.assertEqual(datetime(2016, 5, 15, 18, 30), first_round.fim)

    def test_matches(self):
        """Test the cartolafc.Api matches method"""

        # Arrange
        url = '%s/partidas' % (self.base_url,)
        clube_casa_escudos_dict = {
            '60x60': 'https://s.glbimg.com/es/sde/f/equipes/2014/04/14/vitoria_60x60.png',
            '45x45': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/vitoria_45x45.png',
            '30x30': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/vitoria_30x30.png'
        }
        clube_visitante_escudos_dict = {
            '60x60': 'https://s.glbimg.com/es/sde/f/equipes/2014/04/14/palmeiras_60x60.png',
            '45x45': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/palmeiras_45x45.png',
            '30x30': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/palmeiras_30x30.png'
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.MATCHES_SAMPLE_JSON)
            matches = self.api.matches()
            first_match = matches[0]

        # Assert
        self.assertIsInstance(matches, list)
        self.assertIsInstance(first_match, Match)
        self.assertIsInstance(first_match.clube_casa, Club)
        self.assertEqual(287, first_match.clube_casa.id)
        self.assertEqual(u'Vit\xf3ria', first_match.clube_casa.nome)
        self.assertEqual('VIT', first_match.clube_casa.abreviacao)
        self.assertEqual(16, first_match.clube_casa.posicao)
        self.assertDictEqual(clube_casa_escudos_dict, first_match.clube_casa.escudos)
        self.assertEqual(16, first_match.clube_casa_posicao)
        self.assertIsInstance(first_match.clube_visitante, Club)
        self.assertEqual(275, first_match.clube_visitante.id)
        self.assertEqual('Palmeiras', first_match.clube_visitante.nome)
        self.assertEqual('PAL', first_match.clube_visitante.abreviacao)
        self.assertEqual(1, first_match.clube_visitante.posicao)
        self.assertDictEqual(clube_visitante_escudos_dict, first_match.clube_visitante.escudos)
        self.assertEqual(1, first_match.clube_visitante_posicao)
        self.assertIsInstance(first_match.partida_data, datetime)
        self.assertEqual(datetime(2016, 12, 11, 17), first_match.partida_data)
        self.assertEqual(u'Barrad\xe3o', first_match.local)

    def test_clubs(self):
        """Test the cartolafc.Api clubs method"""

        # Arrange
        url = '%s/clubes' % (self.base_url,)
        escudos_dict = {
            '60x60': '',
            '45x45': '',
            '30x30': ''
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.CLUBS_SAMPLE_JSON)
            clubs = self.api.clubs()
            first_club = clubs['1']

        # Assert
        self.assertIsInstance(clubs, dict)
        self.assertIsInstance(first_club, Club)
        self.assertEqual(1, first_club.id)
        self.assertEqual('Outros', first_club.nome)
        self.assertEqual('OUT', first_club.abreviacao)
        self.assertDictEqual(escudos_dict, first_club.escudos)

    def test_schemes(self):
        """Test the cartolafc.Api schemes method"""

        # Arrange
        url = '%s/esquemas' % (self.base_url,)
        posicoes_dict = {
            'ata': 3,
            'gol': 1,
            'lat': 0,
            'mei': 4,
            'tec': 1,
            'zag': 3
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.SCHEMES_SAMPLE_JSON)
            schemes = self.api.schemes()
            first_scheme = schemes[0]

        # Assert
        self.assertIsInstance(schemes, list)
        self.assertIsInstance(first_scheme, Scheme)
        self.assertEqual(1, first_scheme.esquema_id)
        self.assertEqual('3-4-3', first_scheme.nome)
        self.assertDictEqual(posicoes_dict, first_scheme.posicoes)

    def test_search_team(self):
        """Test the cartolafc.Api search_team_info_by_name method"""

        # Arrange
        team_name = 'Falydos FC'
        url = '%s/times?q=%s' % (self.base_url, team_name)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.SEARCH_TEAM_SAMPLE_JSON)
            teams_found = self.api.search_team_info_by_name(team_name)
            first_team = teams_found[0]

        # Assert
        self.assertIsInstance(teams_found, list)
        self.assertIsInstance(first_team, TeamInfo)
        self.assertEqual(471815, first_team.time_id)
        self.assertEqual(100000083906892, first_team.facebook_id)
        self.assertEqual('https://graph.facebook.com/v2.2/100000083906892/picture?width=100&height=100',
                         first_team.foto_perfil)
        self.assertEqual('Falydos FC', first_team.nome)
        self.assertEqual('Vicente Neto', first_team.nome_cartola)
        self.assertEqual('falydos-fc', first_team.slug)
        self.assertEqual('https://s2.glbimg.com/Hysm88FeHV4IxqX9E180IIEPUkA=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/escudo/29/22/08/004692352920160827072208',
                         first_team.url_escudo_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/escudo/29/22/'
                         '08/004692352920160827072208', first_team.url_escudo_svg)
        self.assertFalse(first_team.assinante)

    def test_search_team_empty(self):
        """Test the cartolafc.Api search_team_info_by_name method"""

        # Arrange
        team_name = 'Inexistent team'
        url = '%s/times?q=%s' % (self.base_url, team_name)

        # Act
        with requests_mock.mock() as m:
            m.get(url, json=[])
            teams_found = self.api.search_team_info_by_name(team_name)

        # Assert
        self.assertIsInstance(teams_found, list)
        self.assertEqual(0, len(teams_found))

    def test_get_team(self):
        """Test the cartolafc.Api get_team method"""

        # Arrange
        team_name = 'Falydos FC'
        team_slug = 'falydos-fc'
        url = '%s/time/slug/%s' % (self.base_url, team_slug)
        escudos_dict = {
            '60x60': 'https://s.glbimg.com/es/sde/f/equipes/2014/04/14/flamengo_60x60.png',
            '45x45': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_45x45.png',
            '30x30': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_30x30.png'
        }
        scout_dict = {
            'FC': 1,
            'PE': 3,
            'SG': 1
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.GET_TEAM_SAMPLE_JSON)
            team = self.api.get_team(team_name)
            first_athlete = team.atletas[0]

        # Assert
        self.assertIsInstance(team, Team)
        self.assertIsInstance(first_athlete, Athlete)
        self.assertEqual(52253, first_athlete.atleta_id)
        self.assertEqual(u'R\xe9ver Humberto Alves Ara\xfajo', first_athlete.nome)
        self.assertEqual(u'R\xe9ver', first_athlete.apelido)
        self.assertEqual('https://s.glbimg.com/es/sde/f/2016/06/28/b3229ad78369684e9d9ac48e51678043_FORMATO.jpeg',
                         first_athlete.foto)
        self.assertIsInstance(first_athlete.clube, Club)
        self.assertEqual(262, first_athlete.clube.id)
        self.assertEqual('Flamengo', first_athlete.clube.nome)
        self.assertEqual('FLA', first_athlete.clube.abreviacao)
        self.assertEqual(3, first_athlete.clube.posicao)
        self.assertDictEqual(escudos_dict, first_athlete.clube.escudos)
        self.assertIsInstance(first_athlete.posicao, Position)
        self.assertEqual(3, first_athlete.posicao.id)
        self.assertEqual('Zagueiro', first_athlete.posicao.nome)
        self.assertEqual('zag', first_athlete.posicao.abreviacao)
        self.assertEqual(u'Prov\xe1vel', first_athlete.status)
        self.assertEqual(3.6, first_athlete.pontos)
        self.assertEqual(8.24, first_athlete.preco)
        self.assertEqual(-0.25, first_athlete.variacao)
        self.assertEqual(4.09, first_athlete.media)
        self.assertEqual(29, first_athlete.jogos)
        self.assertDictEqual(scout_dict, first_athlete.scout)
        self.assertEqual(3, team.esquema_id)
        self.assertEqual(0, team.patrimonio)
        self.assertEqual(48.889892578125, team.pontos)
        self.assertIsInstance(team.info, TeamInfo)
        self.assertEqual(471815, team.info.time_id)
        self.assertEqual(100000083906892, team.info.facebook_id)
        self.assertEqual('https://graph.facebook.com/v2.2/100000083906892/picture?width=100&height=100',
                         team.info.foto_perfil)
        self.assertEqual('Falydos FC', team.info.nome)
        self.assertEqual('Vicente Neto', team.info.nome_cartola)
        self.assertEqual('falydos-fc', team.info.slug)
        self.assertEqual('https://s2.glbimg.com/Hysm88FeHV4IxqX9E180IIEPUkA=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/escudo/29/22/08/004692352920160827072208',
                         team.info.url_escudo_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/escudo/29/22/'
                         '08/004692352920160827072208', team.info.url_escudo_svg)
        self.assertEqual('https://s2.glbimg.com/JyYGSWyMFmHwzgL39uZIBJKEbTM=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/camisa/29/22/08/004692352920160827072208',
                         team.info.url_camisa_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/camisa/29/22/'
                         '08/004692352920160827072208', team.info.url_camisa_svg)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/placeholder/escudo.png',
                         team.info.url_escudo_placeholder_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/placeholder/camisa.png',
                         team.info.url_camisa_placeholder_png)
        self.assertFalse(team.info.assinante)
        self.assertEqual(0, team.valor_time)

    def test_get_team_using_slug(self):
        """Test the cartolafc.Api get_team method"""

        # Arrange
        team_slug = 'falydos-fc'
        url = '%s/time/slug/%s' % (self.base_url, team_slug)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.GET_TEAM_SAMPLE_JSON)
            team = self.api.get_team(team_slug, is_slug=True)
            first_athlete = team.atletas[0]

        # Assert
        self.assertIsInstance(team, Team)
        self.assertIsInstance(first_athlete, Athlete)

    def test_get_inexistent_team(self):
        """Test the cartolafc.Api get_team method"""

        # Arrange
        team_slug = 'inexistent-slug'
        url = '%s/time/slug/%s' % (self.base_url, team_slug)

        # Act and Assert
        with requests_mock.mock() as m:
            m.get(url, json={'mensagem': 'Time não encontrado'})

            with self.assertRaises(cartolafc.CartolaFCError):
                self.api.get_team(team_slug)

    def test_get_team_by_round(self):
        """Test the cartolafc.Api get_team_by_round method"""

        # Arrange
        team_name = 'Falydos FC'
        team_slug = 'falydos-fc'
        round_ = 15
        url = '%s/time/slug/%s/%s' % (self.base_url, team_slug, round_)
        escudos_dict = {
            '60x60': 'https://s.glbimg.com/es/sde/f/equipes/2014/04/14/gremio_60x60.png',
            '45x45': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/gremio_45x45.png',
            '30x30': 'https://s.glbimg.com/es/sde/f/equipes/2013/12/16/gremio_30x30.png'
        }
        scout_dict = {
            'FF': 1,
            'FS': 2,
            'FT': 1,
            'I': 1,
            'PE': 4
        }

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.GET_TEAM_BY_ROUND_SAMPLE_JSON)
            team = self.api.get_team_by_round(team_name, round_)
            first_athlete = team.atletas[0]

        # Assert
        self.assertIsInstance(team, Team)
        self.assertIsInstance(first_athlete, Athlete)
        self.assertEqual(86759, first_athlete.atleta_id)
        self.assertEqual('Luan Guilherme de Jesus Vieira', first_athlete.nome)
        self.assertEqual('Luan', first_athlete.apelido)
        self.assertEqual('https://s.glbimg.com/es/sde/f/2016/04/30/48dd7ee31224c5846fad2dbe7a73178c_FORMATO.png',
                         first_athlete.foto)
        self.assertIsInstance(first_athlete.clube, Club)
        self.assertEqual(284, first_athlete.clube.id)
        self.assertEqual(u'Gr\xeamio', first_athlete.clube.nome)
        self.assertEqual('GRE', first_athlete.clube.abreviacao)
        self.assertEqual(9, first_athlete.clube.posicao)
        self.assertDictEqual(escudos_dict, first_athlete.clube.escudos)
        self.assertIsInstance(first_athlete.posicao, Position)
        self.assertEqual(5, first_athlete.posicao.id)
        self.assertEqual('Atacante', first_athlete.posicao.nome)
        self.assertEqual('ata', first_athlete.posicao.abreviacao)
        self.assertEqual('Nulo', first_athlete.status)
        self.assertEqual(3.5, first_athlete.pontos)
        self.assertEqual(19.23, first_athlete.preco)
        self.assertEqual(-0.45, first_athlete.variacao)
        self.assertEqual(6.78, first_athlete.media)
        self.assertEqual(14, first_athlete.jogos)
        self.assertDictEqual(scout_dict, first_athlete.scout)
        self.assertEqual(1, team.esquema_id)
        self.assertEqual(0, team.patrimonio)
        self.assertEqual(70.89013671875, team.pontos)
        self.assertIsInstance(team.info, TeamInfo)
        self.assertEqual(471815, team.info.time_id)
        self.assertEqual(100000083906892, team.info.facebook_id)
        self.assertEqual('https://graph.facebook.com/v2.2/100000083906892/picture?width=100&height=100',
                         team.info.foto_perfil)
        self.assertEqual('Falydos FC', team.info.nome)
        self.assertEqual('Vicente Neto', team.info.nome_cartola)
        self.assertEqual('falydos-fc', team.info.slug)
        self.assertEqual('https://s2.glbimg.com/Hysm88FeHV4IxqX9E180IIEPUkA=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/escudo/29/22/08/004692352920160827072208',
                         team.info.url_escudo_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/escudo/29/22/'
                         '08/004692352920160827072208', team.info.url_escudo_svg)
        self.assertEqual('https://s2.glbimg.com/JyYGSWyMFmHwzgL39uZIBJKEbTM=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/camisa/29/22/08/004692352920160827072208',
                         team.info.url_camisa_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/cartola_svg_27/camisa/29/22/'
                         '08/004692352920160827072208', team.info.url_camisa_svg)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/placeholder/escudo.png',
                         team.info.url_escudo_placeholder_png)
        self.assertEqual('https://s3.glbimg.com/v1/AUTH_58d78b787ec34892b5aaa0c7a146155f/placeholder/camisa.png',
                         team.info.url_camisa_placeholder_png)
        self.assertFalse(team.info.assinante)
        self.assertEqual(0, team.valor_time)

    def test_get_team_by_round_using_slug(self):
        """Test the cartolafc.Api get_team_by_round method"""

        # Arrange
        team_slug = 'falydos-fc'
        round_ = 15
        url = '%s/time/slug/%s/%s' % (self.base_url, team_slug, round_)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.GET_TEAM_BY_ROUND_SAMPLE_JSON)
            team = self.api.get_team_by_round(team_slug, round_, is_slug=True)
            first_athlete = team.atletas[0]

        # Assert
        self.assertIsInstance(team, Team)
        self.assertIsInstance(first_athlete, Athlete)

    def test_get_inexistent_team_by_round(self):
        """Test the cartolafc.Api get_team_by_round method"""

        # Arrange
        team_slug = 'inexistent-slug'
        round_ = 15
        url = '%s/time/slug/%s/%s' % (self.base_url, team_slug, round_)

        # Act and Assert
        with requests_mock.mock() as m:
            m.get(url, json={'mensagem': 'Time não encontrado'})

            with self.assertRaises(cartolafc.CartolaFCError):
                self.api.get_team_by_round(team_slug, round_)

    def test_search_league_info_by_name(self):
        """Test the cartolafc.Api search_league_info_by_name method"""

        # Arrange
        league_name = 'Virtus Premier League'
        url = '%s/ligas?q=%s' % (self.base_url, league_name)

        # Act
        with requests_mock.mock() as m:
            m.get(url, text=self.SEARCH_LEAGUE_SAMPLE_JSON)
            leagues_found = self.api.search_league_info_by_name(league_name)
            first_league = leagues_found[0]

        # Assert
        self.assertIsInstance(leagues_found, list)
        self.assertIsInstance(first_league, LeagueInfo)
        self.assertEqual(262881, first_league.liga_id)
        self.assertEqual('Virtus Premier League', first_league.nome)
        self.assertEqual(u'Pr\xeamio:\n- O melhor de cada turno ganha R$65,00.\n- 1\xba Lugar geral  ganha a  Camisa '
                         u'Oficial do time do Cora\xe7\xe3o.', first_league.descricao)
        self.assertEqual('virtus-premier-league', first_league.slug)
        self.assertEqual('https://s2.glbimg.com/7r-JR3GCpYmIZLbcBIM1xZF1pyg=/https://s3.glbimg.com/v1/AUTH_'
                         '58d78b787ec34892b5aaa0c7a146155f/cartola_svg_1/flamula/81/51/44/0026288120160726165144',
                         first_league.imagem)
        self.assertEqual(0, first_league.quantidade_times)
        self.assertFalse(first_league.mata_mata)
        self.assertEqual('Fechada', first_league.tipo)

    def test_search_league_info_by_name_empty(self):
        """Test the cartolafc.Api search_league_info_by_name method"""

        # Arrange
        league_name = 'Inexistent league'
        url = '%s/ligas?q=%s' % (self.base_url, league_name)

        # Act
        with requests_mock.mock() as m:
            m.get(url, json=[])
            leagues_found = self.api.search_league_info_by_name(league_name)

        # Assert
        self.assertIsInstance(leagues_found, list)
        self.assertEqual(0, len(leagues_found))

    def test_overloaded_servers(self):
        """Test the cartolafc.Api with overloaded services"""

        # Arrange
        url = '%s/mercado/status' % (self.base_url,)

        # Act and Assert
        with requests_mock.mock() as m:
            m.get(url)

            with self.assertRaises(cartolafc.CartolaFCError):
                self.api.status()
