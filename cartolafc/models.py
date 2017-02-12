# -*- coding: utf-8 -*-
from datetime import datetime


class BaseModel(object):
    """ Base class from which all Cartola FC models will inherit. """

    def __init__(self, **kwargs):
        pass

    @classmethod
    def from_dict(cls, data, **kwargs):
        """
        Create a new instance based on a JSON dict. Any kwargs should be supplied by the inherited, calling class.
        Args:
            data: A JSON dict, as converted from the JSON in the Cartola FC API.
        """

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        return cls(**json_data)


class Status(BaseModel):
    def __init__(self, **kwargs):
        super(Status, self).__init__(**kwargs)

        param_defaults = {
            'rodada_atual': None,
            'status_mercado': None,
            'temporada': None,
            'times_escalados': None,
            'fechamento': None,
            'mercado_pos_rodada': None,
            'aviso': None
        }
        for (param, default) in param_defaults.items():
            setattr(self, param, kwargs.get(param, default))

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
        return super(cls, cls).from_dict(data=data)
