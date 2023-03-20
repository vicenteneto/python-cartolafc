class CartolaFCError(Exception):
    """Classe base para os erros da API do Cartola FC"""

    pass


class CartolaFCOverloadError(CartolaFCError):
    """Erro lançado quando o servidores estão sobrecarregados e a biblioteca não consegue obter os dados
    requisitados"""

    pass


class CartolaFCGameOverError(CartolaFCError):
    """Erro lançado quando o jogo termina e a biblioteca não consegue obter os dados requisitados"""

    pass
