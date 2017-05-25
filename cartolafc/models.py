# -*- coding: utf-8 -*-

from datetime import datetime


class Atleta(object):
    """ Atleta """

    def __init__(self, atleta_id, nome, apelido, pontos_num, scout, posicao, clube, status):
        self.atleta_id = atleta_id
        self.nome = nome
        self.apelido = apelido
        self.pontos_num = pontos_num
        self.scout = scout
        self.posicao = posicao
        self.clube = clube
        self.status = status

    @classmethod
    def from_dict(cls, data, posicoes, clubes, mercado_status):
        posicao = posicoes[data['posicao_id']]
        clube = clubes[data['clube_id']]
        status = mercado_status[data['status_id']]
        return cls(data['atleta_id'], data['nome'], data['apelido'], data['pontos_num'], data['scout'], posicao, clube,
                   status)


class Clube(object):
    """ Clube """

    def __init__(self, id_, nome, abreviacao):
        self.id = id_
        self.nome = nome
        self.abreviacao = abreviacao

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['nome'], data['abreviacao'])


class Liga(object):
    """ Liga """

    def __init__(self, id_, nome, slug, times):
        self.id = id_
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

    def __init__(self, rodada_atual, status_mercado, times_escalados, fechamento, aviso):
        self.rodada_atual = rodada_atual
        self.status_mercado = status_mercado
        self.times_escalados = times_escalados
        self.fechamento = fechamento
        self.aviso = aviso

    @classmethod
    def from_dict(cls, data):
        status = {
            1: 'Mercado aberto',
            2: 'Mercado fechado',
            3: 'Mercado em atualização',
            4: 'Mercado em manutenção',
            6: 'Final de temporada'
        }

        status_mercado = status.get(data['status_mercado'], 'Desconhecido')
        fechamento = datetime.fromtimestamp(data['fechamento']['timestamp'])
        return cls(data['rodada_atual'], status_mercado, data['times_escalados'], fechamento, data['aviso'])


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

    def __init__(self, apelido, pontuacao, scout, posicao, clube):
        self.apelido = apelido
        self.pontuacao = pontuacao
        self.scout = scout
        self.posicao = posicao
        self.clube = clube

    @classmethod
    def from_dict(cls, data, clubes, posicoes):
        data['clube'] = clubes[data['clube_id']]
        data['posicao'] = posicoes[data['posicao_id']]
        return cls(data['apelido'], data['pontuacao'], data['scout'], data['posicao'], data['clube'])


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


class Posicao(object):
    """ Posição """

    def __init__(self, id_, nome, abreviacao):
        self.id = id_
        self.nome = nome
        self.abreviavao = abreviacao

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['nome'], data['abreviacao'])


class Status(object):
    """ Status """

    def __init__(self, id_, nome):
        self.id = id_
        self.nome = nome


class Time(object):
    """ Time """

    def __init__(self, patrimonio, valor_time, ultima_pontuacao, atletas, info):
        self.patrimonio = patrimonio
        self.valor_time = valor_time
        self.ultima_pontuacao = ultima_pontuacao
        self.atletas = atletas
        self.info = info

    @classmethod
    def from_dict(cls, data, posicoes, clubes, mercado_status):
        data['atletas'].sort(key=lambda a: a['posicao_id'])
        atletas = [Atleta.from_dict(atleta, posicoes, clubes, mercado_status) for atleta in data['atletas']]
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
