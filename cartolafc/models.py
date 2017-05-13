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
        data['clube'] = kwargs['clubs'][data['clube_id']]
        data['posicao'] = kwargs['positions'][data['posicao_id']]
        data['status'] = kwargs['status'][data['status_id']]['nome']
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
        data['clube'] = kwargs['clubs'][data['clube_id']]
        data['posicao'] = kwargs['positions'][data['posicao_id']]
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
        data['clube_casa'] = kwargs['clubs'][data['clube_casa_id']]
        data['clube_visitante'] = kwargs['clubs'][data['clube_visitante_id']]
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


class Round(BaseModel):
    """ Round. """

    rodada_id = None
    inicio = None
    fim = None

    def __init__(self, **kwargs):
        param_defaults = ('rodada_id', 'inicio', 'fim')
        super(Round, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        date_format = '%Y-%m-%d %H:%M:%S'
        data['inicio'] = datetime.strptime(data['inicio'], date_format)
        data['fim'] = datetime.strptime(data['fim'], date_format)
        return super(cls, cls).from_dict(data)


class RoundHighlights(BaseModel):
    """ RoundHighlights. """

    media_cartoletas = None
    media_pontos = None
    mito_rodada = None

    def __init__(self, **kwargs):
        param_defaults = ('media_cartoletas', 'media_pontos', 'mito_rodada')
        super(RoundHighlights, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        if data['mito_rodada']:
            data['mito_rodada'] = TeamInfo.from_dict(data['mito_rodada'])
        return super(cls, cls).from_dict(data)


class Scheme(BaseModel):
    """ Scheme. """

    esquema_id = None
    nome = None
    posicoes = None

    def __init__(self, **kwargs):
        param_defaults = ('esquema_id', 'nome', 'posicoes')
        super(Scheme, self).__init__(param_defaults, **kwargs)


class Sponsor(BaseModel):
    """ Sponsor. """

    liga_editorial_id = None
    liga_id = None
    tipo_ranking = None
    url_link = None
    url_editoria_ge = None
    img_background = None
    img_marca_patrocinador = None
    nome = None

    def __init__(self, **kwargs):
        param_defaults = ('liga_editorial_id', 'liga_id', 'tipo_ranking', 'url_link', 'url_editoria_ge',
                          'img_background', 'img_marca_patrocinador', 'nome')
        super(Sponsor, self).__init__(param_defaults, **kwargs)


class Status(BaseModel):
    """ Status. """

    rodada_atual = None
    status_mercado = None
    temporada = None
    times_escalados = None
    fechamento = None
    mercado_pos_rodada = None
    aviso = None

    def __init__(self, **kwargs):
        param_defaults = ('rodada_atual', 'status_mercado', 'temporada', 'times_escalados', 'fechamento',
                          'mercado_pos_rodada', 'aviso')
        super(Status, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        status_mercado = {
            1: 'Aberto',
            2: 'Fechado',
            3: 'Atualização',
            4: 'Manutenção',
            6: 'Encerrado'
        }

        data['status_mercado'] = status_mercado.get(data['status_mercado'], 'Desconhecido')
        data['fechamento'] = datetime.fromtimestamp(data['fechamento']['timestamp'])
        return super(cls, cls).from_dict(data)


class Team(BaseModel):
    """ Team. """

    atletas = None
    esquema_id = None
    patrimonio = None
    pontos = None
    info = None
    valor_time = None

    def __init__(self, **kwargs):
        param_defaults = ('atletas', 'esquema_id', 'patrimonio', 'pontos', 'info', 'valor_time')
        super(Team, self).__init__(param_defaults, **kwargs)

    @classmethod
    def from_dict(cls, data, **kwargs):
        clubs = {club['id']: Club.from_dict(club) for club in data['clubes'].values()}
        positions = {position['id']: Position.from_dict(position) for position in data['posicoes'].values()}
        status = {status['id']: status for status in data['status'].values()}
        data['atletas'] = [Athlete.from_dict(athlete, clubs=clubs, positions=positions, status=status) for athlete
                           in data['atletas']]
        data['info'] = TeamInfo.from_dict(data['time'])
        return super(cls, cls).from_dict(data)


class TeamInfo(BaseModel):
    """ TeamInfo. """

    time_id = None
    clube_id = None
    esquema_id = None
    facebook_id = None
    foto_perfil = None
    nome = None
    nome_cartola = None
    slug = None
    url_escudo_png = None
    url_escudo_svg = None
    url_camisa_png = None
    url_camisa_svg = None
    url_escudo_placeholder_png = None
    url_camisa_placeholder_png = None
    assinante = None

    def __init__(self, **kwargs):
        param_defaults = ('time_id', 'clube_id', 'esquema_id', 'facebook_id', 'foto_perfil', 'nome', 'nome_cartola',
                          'slug', 'url_escudo_png', 'url_escudo_svg', 'url_camisa_png', 'url_camisa_svg',
                          'url_escudo_placeholder_png', 'url_camisa_placeholder_png', 'assinante')
        super(TeamInfo, self).__init__(param_defaults, **kwargs)
