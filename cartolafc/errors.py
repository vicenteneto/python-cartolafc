# -*- coding: utf-8 -*-


class CartolaFCError(Exception):
    """ Classe base para os erros da API do Cartola FC """
    pass


class CartolaFCOverloadError(Exception):
    """ Erro lançado quando o servidores estão sobrecarregados e a biblioteca não consegue obter os dados
    requisitados """
    pass
