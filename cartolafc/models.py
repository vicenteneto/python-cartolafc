# -*- coding: utf-8 -*-

from datetime import datetime


class BaseModel(object):
    """  Base class from which all Cartola FC models will inherit. """

    def __init__(self, param_defaults, **kwargs):
        for param in param_defaults:
            setattr(self, param, kwargs.get(param, getattr(self, param, None)))

    @classmethod
    def from_dict(cls, data, **kwargs):
        """
        Create a new instance based on a JSON dict. Any kwargs should be supplied by the inherited, calling class.
        Args:
            data: A JSON dict, as converted from the JSON in the Cartola FC API.
        """

        json_data = data.copy()
        return cls(**json_data)


class Athlete(BaseModel):
    """  Athlete. """

    atleta_id = None
    nome = None
    apelido = None
    foto = None
    clube = None
    posicao = None
    status = None
    pontos = None
    preco = None
    variacao = None
    media = None
    jogos = None
    scout = None

    def __init__(self, **kwargs):
        param_defaults = ('atleta_id', 'nome', 'apelido', 'foto', 'clube', 'posicao', 'status', 'pontos', 'preco',
                          'variacao', 'media', 'jogos', 'scout')
        super(Athlete, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        try:
            data['clube'] = kwargs['clubs'][data['clube_id']]
        except KeyError:
            pass
        try:
            data['posicao'] = kwargs['positions'][data['posicao_id']]
        except KeyError:
            pass
        try:
            data['status'] = kwargs['status'][data['status_id']]['nome']
        except KeyError:
            pass
        data['pontos'] = data['pontos_num']
        data['preco'] = data['preco_num']
        data['variacao'] = data['variacao_num']
        data['media'] = data['media_num']
        data['jogos'] = data['jogos_num']
        return super(cls, cls).from_dict(data)


class AthleteInfo(BaseModel):
    """  AthleteInfo. """

    atleta_id = None
    nome = None
    apelido = None
    foto = None
    preco_editorial = None

    def __init__(self, **kwargs):
        param_defaults = ('atleta_id', 'nome', 'apelido', 'foto', 'preco_editorial')
        super(AthleteInfo, self).__init__(param_defaults, **kwargs)


class AthleteScore(BaseModel):
    """ AthleteScore. """

    apelido = None
    pontuacao = None
    foto = None
    clube = None
    posicao = None
    scout = None

    def __init__(self, **kwargs):
        param_defaults = ('apelido', 'pontuacao', 'foto', 'clube', 'posicao', 'scout')
        super(AthleteScore, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        try:
            data['clube'] = kwargs['clubs'][data['clube_id']]
        except KeyError:
            pass
        try:
            data['posicao'] = kwargs['positions'][data['posicao_id']]
        except KeyError:
            pass
        return super(cls, cls).from_dict(data)


class Club(BaseModel):
    """ Club. """

    id = None
    nome = None
    abreviacao = None
    posicao = None
    escudos = None

    def __init__(self, **kwargs):
        param_defaults = ('id', 'nome', 'abreviacao', 'posicao', 'escudos')
        super(Club, self).__init__(param_defaults, **kwargs)


class Highlight(BaseModel):
    """ Highlight. """

    atleta = None
    escalacoes = None
    clube = None
    escudo_clube = None
    posicao = None

    def __init__(self, **kwargs):
        param_defaults = ('atleta', 'escalacoes', 'clube', 'escudo_clube', 'posicao')
        super(Highlight, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        data['atleta'] = AthleteInfo.from_dict(data['Atleta'])
        return super(cls, cls).from_dict(data)


class LeagueInfo(BaseModel):
    """ LeagueInfo. """

    liga_id = None
    nome = None
    descricao = None
    slug = None
    imagem = None
    quantidade_times = None
    mata_mata = None
    tipo = None

    def __init__(self, **kwargs):
        param_defaults = ('liga_id', 'nome', 'descricao', 'slug', 'imagem', 'quantidade_times', 'mata_mata', 'tipo')
        super(LeagueInfo, self).__init__(param_defaults, **kwargs)


class Match(BaseModel):
    """ Match. """

    clube_casa = None
    clube_casa_posicao = None
    clube_visitante = None
    clube_visitante_posicao = None
    partida_data = None
    local = None

    def __init__(self, **kwargs):
        param_defaults = ('clube_casa', 'clube_casa_posicao', 'clube_visitante', 'clube_visitante_posicao',
                          'partida_data', 'local')
        super(Match, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        date_format = '%Y-%m-%d %H:%M:%S'
        try:
            data['clube_casa'] = kwargs['clubs'][data['clube_casa_id']]
        except KeyError:
            pass
        try:
            data['clube_visitante'] = kwargs['clubs'][data['clube_visitante_id']]
        except KeyError:
            pass
        data['partida_data'] = datetime.strptime(data['partida_data'], date_format)
        return super(cls, cls).from_dict(data)


class Position(BaseModel):
    """ Position. """

    id = None
    nome = None
    abreviacao = None

    def __init__(self, **kwargs):
        param_defaults = ('id', 'nome', 'abreviacao')
        super(Position, self).__init__(param_defaults, **kwargs)


class Scheme(BaseModel):
    """ Scheme. """

    esquema_id = None
    nome = None
    posicoes = None

    def __init__(self, **kwargs):
        param_defaults = ('esquema_id', 'nome', 'posicoes')
        super(Scheme, self).__init__(param_defaults, **kwargs)


class Atleta(object):
    """ Atleta. """

    def __init__(self, id_, apelido, posicao, clube, pontos, scout):
        self.id = id_
        self.apelido = apelido
        self.posicao = posicao
        self.clube = clube
        self.pontos = pontos
        self.scout = scout

    @classmethod
    def from_dict(cls, data, posicoes, clubes):
        posicao = Posicao.from_dict(posicoes[str(data['posicao_id'])])
        clube = Clube.from_dict(clubes[str(data['clube_id'])])
        return cls(data['atleta_id'], data['apelido'], posicao, clube, data['pontos_num'], data['scout'])


class Clube(object):
    """ Clube. """

    def __init__(self, id_, nome, abreviacao):
        self.id = id_
        self.nome = nome
        self.abreviacao = abreviacao

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['nome'], data['abreviacao'])


class TimeInfo(object):
    """ Info. """

    def __init__(self, id_, nome, cartola, slug, esquema_id=None):
        self.id = id_
        self.nome = nome
        self.cartola = cartola
        self.slug = slug
        self.esquema_id = esquema_id

    @classmethod
    def from_dict(cls, data):
        return cls(data['time_id'], data['nome'], data['nome_cartola'], data['slug'], data.get('esquema_id', None))


class Liga(object):
    """ Liga. """

    def __init__(self, id_, nome, slug, times):
        self.id = id_
        self.nome = nome
        self.slug = slug
        self.times = times

    @classmethod
    def from_dict(cls, data):
        times = [TimeInfo.from_dict(time) for time in data['times']]
        return cls(data['liga']['liga_id'], data['liga']['nome'], data['liga']['slug'], times)


class Posicao(object):
    """ Posição. """

    def __init__(self, id_, nome, abreviacao):
        self.id = id_
        self.nome = nome
        self.abreviavao = abreviacao

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['nome'], data['abreviacao'])


class Status(object):
    """ Status. """

    def __init__(self, rodada_atual, status_mercado, times_escalados, fechamento, aviso):
        self.rodada_atual = rodada_atual
        self.status_mercado = status_mercado
        self.times_escalados = times_escalados
        self.fechamento = fechamento
        self.aviso = aviso

    @classmethod
    def from_dict(cls, data):
        possible_states = {
            1: 'Mercado aberto',
            2: 'Mercado fechado',
            3: 'Mercado em atualização',
            4: 'Mercado em manutenção',
            6: 'Final de temporada'
        }

        status_mercado = possible_states.get(data['status_mercado'], 'Desconhecido')
        fechamento = datetime.fromtimestamp(data['fechamento']['timestamp'])
        return cls(data['rodada_atual'], status_mercado, data['times_escalados'], fechamento, data['aviso'])


class Time(object):
    """ Time. """

    def __init__(self, patrimonio, valor_time, ultima_pontuacao, atletas, info):
        self.patrimonio = patrimonio
        self.valor_time = valor_time
        self.ultima_pontuacao = ultima_pontuacao
        self.atletas = atletas
        self.info = info

    @classmethod
    def from_dict(cls, data):
        data['atletas'].sort(key=lambda a: a['posicao_id'])
        atletas = [Atleta.from_dict(atleta, data['posicoes'], data['clubes']) for atleta in data['atletas']]
        info = TimeInfo.from_dict(data['time'])
        return cls(data['patrimonio'], data['valor_time'], data['pontos'], atletas, info)
