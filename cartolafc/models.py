# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import datetime

Posicao = namedtuple('Posicao', ['id', 'nome', 'abreviacao'])
Status = namedtuple('Status', ['id', 'nome'])

_posicoes = {
    1: Posicao(1, 'Goleiro', 'gol'),
    2: Posicao(2, 'Lateral', 'lat'),
    3: Posicao(3, 'Zagueiro', 'zag'),
    4: Posicao(4, 'Meia', 'mei'),
    5: Posicao(5, 'Atacante', 'ata'),
    6: Posicao(6, 'Técnico', 'tec')
}

_atleta_status = {
    2: Status(2, 'Dúvida'),
    3: Status(3, 'Suspenso'),
    5: Status(5, 'Contundido'),
    6: Status(6, 'Nulo'),
    7: Status(7, 'Provável')
}

_mercado_status = {
    1: Status(1, 'Mercado aberto'),
    2: Status(2, 'Mercado fechado'),
    3: Status(3, 'Mercado em atualização'),
    4: Status(4, 'Mercado em manutenção'),
    6: Status(6, 'Final de temporada')
}


class Atleta(object):
    """ Atleta """

    def __init__(self, atleta_id, nome, apelido, pontos_num, scout, posicao_id, status_id, clube):
        self.atleta_id = atleta_id
        self.nome = nome
        self.apelido = apelido
        self.pontos_num = pontos_num
        self.scout = scout
        self.posicao = _posicoes[posicao_id]
        self.status = _atleta_status[status_id]
        self.clube = clube

    @classmethod
    def from_dict(cls, data, clubes):
        clube = clubes[data['clube_id']]
        return cls(data['atleta_id'], data['nome'], data['apelido'], data['pontos_num'], data['scout'],
                   data['posicao_id'], data['status_id'], clube)


class Clube(object):
    """ Clube """

    def __init__(self, id, nome, abreviacao):
        self.id = id
        self.nome = nome
        self.abreviacao = abreviacao

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['nome'], data['abreviacao'])


class DestaqueRodada(object):
    """ Destaque Rodada"""

    def __init__(self, media_cartoletas, media_pontos, mito_rodada):
        self.media_cartoletas = media_cartoletas
        self.media_pontos = media_pontos
        self.mito_rodada = mito_rodada

    @classmethod
    def from_dict(cls, data):
        mito_rodada = TimeInfo.from_dict(data['mito_rodada'])
        return cls(data['media_cartoletas'], data['media_pontos'], mito_rodada)


class Liga(object):
    """ Liga """

    def __init__(self, id, nome, slug, times):
        self.id = id
        self.nome = nome
        self.slug = slug
        self.times = times

    @classmethod
    def from_dict(cls, data):
        times = [TimeInfo.from_dict(time) for time in data['times']]
        return cls(data['liga']['liga_id'], data['liga']['nome'], data['liga']['slug'], times)


class LigaInfo(object):
    """ Liga Info"""

    def __init__(self, liga_id, nome, slug, descricao, tipo):
        self.liga_id = liga_id
        self.nome = nome
        self.slug = slug
        self.descricao = descricao
        self.tupo = tipo

    @classmethod
    def from_dict(cls, data):
        return cls(data['liga_id'], data['nome'], data['slug'], data['descricao'], data['tipo'])


class Mercado(object):
    """ Mercado """

    def __init__(self, rodada_atual, status_mercado, times_escalados, aviso, fechamento):
        self.rodada_atual = rodada_atual
        self.status_mercado = _mercado_status[status_mercado]
        self.times_escalados = times_escalados
        self.aviso = aviso
        self.fechamento = fechamento

    @classmethod
    def from_dict(cls, data):
        fechamento = datetime.fromtimestamp(data['fechamento']['timestamp'])
        return cls(data['rodada_atual'], data['status_mercado'], data['times_escalados'], data['aviso'], fechamento)


class Patrocinador(object):
    """ Patrocinador """

    def __init__(self, liga_id, nome, url_link):
        self.liga_id = liga_id
        self.nome = nome
        self.url_link = url_link

    @classmethod
    def from_dict(cls, data):
        return cls(data['liga_id'], data['nome'], data['url_link'])


class PontuacaoAtleta(object):
    """ Pontuação Atleta """

    def __init__(self, apelido, pontuacao, scout, posicao_id, clube):
        self.apelido = apelido
        self.pontuacao = pontuacao
        self.scout = scout
        self.posicao = _posicoes[posicao_id]
        self.clube = clube

    @classmethod
    def from_dict(cls, data, clubes):
        clube = clubes[data['clube_id']]
        return cls(data['apelido'], data['pontuacao'], data['scout'], data['posicao_id'], clube)


class PontuacaoInfo(object):
    """ Pontuação Info """

    def __init__(self, atleta_id, rodada_id, pontos, preco, variacao, media):
        self.atleta_id = atleta_id
        self.rodada_id = rodada_id
        self.pontos = pontos
        self.preco = preco
        self.variacao = variacao
        self.media = media

    @classmethod
    def from_dict(cls, data):
        return cls(data['atleta_id'], data['rodada_id'], data['pontos'], data['preco'], data['variacao'], data['media'])


class Time(object):
    """ Time """

    def __init__(self, patrimonio, valor_time, ultima_pontuacao, atletas, info):
        self.patrimonio = patrimonio
        self.valor_time = valor_time
        self.ultima_pontuacao = ultima_pontuacao
        self.atletas = atletas
        self.info = info

    @classmethod
    def from_dict(cls, data, clubes):
        data['atletas'].sort(key=lambda a: a['posicao_id'])
        atletas = [Atleta.from_dict(atleta, clubes) for atleta in data['atletas']]
        info = TimeInfo.from_dict(data['time'])
        return cls(data['patrimonio'], data['valor_time'], data['pontos'], atletas, info)


class TimeInfo(object):
    """ Time Info """

    def __init__(self, time_id, nome, nome_cartola, slug, assinante):
        self.time_id = time_id
        self.nome = nome
        self.nome_cartola = nome_cartola
        self.slug = slug
        self.assinante = assinante

    @classmethod
    def from_dict(cls, data):
        return cls(data['time_id'], data['nome'], data['nome_cartola'], data['slug'], data['assinante'])
