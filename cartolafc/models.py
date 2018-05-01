# -*- coding: utf-8 -*-

import json
from collections import namedtuple
from datetime import datetime

import pytz

from .util import json_default

Posicao = namedtuple('Posicao', ['id', 'nome', 'abreviacao'])
Status = namedtuple('Status', ['id', 'nome'])

_posicoes = {
    1: Posicao(1, u'Goleiro', 'gol'),
    2: Posicao(2, u'Lateral', 'lat'),
    3: Posicao(3, u'Zagueiro', 'zag'),
    4: Posicao(4, u'Meia', 'mei'),
    5: Posicao(5, u'Atacante', 'ata'),
    6: Posicao(6, u'Técnico', 'tec')
}

_atleta_status = {
    2: Status(2, u'Dúvida'),
    3: Status(3, u'Suspenso'),
    5: Status(5, u'Contundido'),
    6: Status(6, u'Nulo'),
    7: Status(7, u'Provável')
}

_mercado_status = {
    1: Status(1, u'Mercado aberto'),
    2: Status(2, u'Mercado fechado'),
    3: Status(3, u'Mercado em atualização'),
    4: Status(4, u'Mercado em manutenção'),
    6: Status(6, u'Final de temporada')
}


class BaseModel(object):
    def __repr__(self):
        return json.dumps(self, default=json_default)


class Atleta(BaseModel):
    """ Representa um atleta (jogador ou técnico), e possui informações como o apelido, clube e pontuação obtida """

    def __init__(self, atleta_id, apelido, pontos, scout, posicao_id, clube, status_id=None, is_capitao=None):
        self.id = atleta_id
        self.apelido = apelido
        self.pontos = pontos
        self.scout = scout
        self.posicao = _posicoes[posicao_id]
        self.clube = clube
        self.status = _atleta_status[status_id] if status_id else None
        self.is_capitao = is_capitao

    @classmethod
    def from_dict(cls, data, clubes, atleta_id=None, is_capitao=None):
        atleta_id = atleta_id if atleta_id else data['atleta_id']
        pontos = data['pontos_num'] if 'pontos_num' in data else data['pontuacao']
        clube = clubes[data['clube_id']]
        return cls(atleta_id, data['apelido'], pontos, data['scout'], data['posicao_id'], clube,
                   data.get('status_id', None), is_capitao)


class Clube(BaseModel):
    """ Representa um dos 20 clubes presentes no campeonato, e possui informações como o nome e a abreviação """

    def __init__(self, id, nome, abreviacao):
        self.id = id
        self.nome = nome
        self.abreviacao = abreviacao

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['nome'], data['abreviacao'])


class DestaqueRodada(BaseModel):
    """ Destaque Rodada"""

    def __init__(self, media_cartoletas, media_pontos, mito_rodada):
        self.media_cartoletas = media_cartoletas
        self.media_pontos = media_pontos
        self.mito_rodada = mito_rodada

    @classmethod
    def from_dict(cls, data):
        mito_rodada = TimeInfo.from_dict(data['mito_rodada'])
        return cls(data['media_cartoletas'], data['media_pontos'], mito_rodada)


class Liga(BaseModel):
    """ Liga """

    def __init__(self, liga_id, nome, slug, descricao, times):
        self.id = liga_id
        self.nome = nome
        self.slug = slug
        self.descricao = descricao
        self.times = times

    @classmethod
    def from_dict(cls, data, ranking=None):
        data_liga = data.get('liga', data)
        times = [TimeInfo.from_dict(time, ranking=ranking) for time in data['times']] if 'times' in data else None
        return cls(data_liga['liga_id'], data_liga['nome'], data_liga['slug'], data_liga['descricao'], times)


class LigaPatrocinador(BaseModel):
    """ Liga Patrocinador """

    def __init__(self, liga_id, nome, url_link):
        self.id = liga_id
        self.nome = nome
        self.url_link = url_link

    @classmethod
    def from_dict(cls, data):
        return cls(data['liga_id'], data['nome'], data['url_link'])


class Mercado(BaseModel):
    """ Mercado """

    def __init__(self, rodada_atual, status_mercado, times_escalados, aviso, fechamento):
        self.rodada_atual = rodada_atual
        self.status = _mercado_status[status_mercado]
        self.times_escalados = times_escalados
        self.aviso = aviso
        self.fechamento = fechamento

    @classmethod
    def from_dict(cls, data):
        fechamento = datetime(data['fechamento']['ano'], data['fechamento']['mes'], data['fechamento']['dia'],
                              data['fechamento']['hora'], data['fechamento']['minuto'],
                              tzinfo=pytz.timezone('America/Sao_Paulo'))
        return cls(data['rodada_atual'], data['status_mercado'], data['times_escalados'], data['aviso'], fechamento)


class Partida(BaseModel):
    """ Partida """

    def __init__(self, data, local, clube_casa, placar_casa, clube_visitante, placar_visitante):
        self.data = data
        self.local = local
        self.clube_casa = clube_casa
        self.placar_casa = placar_casa
        self.clube_visitante = clube_visitante
        self.placar_visitante = placar_visitante

    @classmethod
    def from_dict(cls, data, clubes):
        data_ = datetime.strptime(data['partida_data'], '%Y-%m-%d %H:%M:%S')
        local = data['local']
        clube_casa = clubes[data['clube_casa_id']]
        placar_casa = data['placar_oficial_mandante']
        clube_visitante = clubes[data['clube_visitante_id']]
        placar_visitante = data['placar_oficial_visitante']
        return cls(data_, local, clube_casa, placar_casa, clube_visitante, placar_visitante)


class PontuacaoInfo(BaseModel):
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


class Time(BaseModel):
    """ Time """

    def __init__(self, patrimonio, valor_time, ultima_pontuacao, atletas, info):
        self.patrimonio = patrimonio
        self.valor_time = valor_time
        self.ultima_pontuacao = ultima_pontuacao
        self.atletas = atletas
        self.info = info

    @classmethod
    def from_dict(cls, data, clubes, capitao):
        data['atletas'].sort(key=lambda a: a['posicao_id'])
        atletas = [Atleta.from_dict(atleta, clubes, is_capitao=atleta['atleta_id'] == capitao) for atleta in
                   data['atletas']]
        info = TimeInfo.from_dict(data['time'])
        return cls(data['patrimonio'], data['valor_time'], data['pontos'], atletas, info)


class TimeInfo(BaseModel):
    """ Time Info """

    def __init__(self, time_id, nome, nome_cartola, slug, assinante, pontos):
        self.id = time_id
        self.nome = nome
        self.nome_cartola = nome_cartola
        self.slug = slug
        self.assinante = assinante
        self.pontos = pontos

    @classmethod
    def from_dict(cls, data, ranking=None):
        pontos = data['pontos'][ranking] if ranking and ranking in data['pontos'] else None
        return cls(data['time_id'], data['nome'], data['nome_cartola'], data['slug'], data['assinante'], pontos)
