# Python Cartola FC API

[![PyPi Version](https://img.shields.io/pypi/v/python-cartolafc.svg)](https://pypi.org/project/python-cartolafc/)
[![Build Status](https://github.com/vicenteneto/python-cartolafc/actions/workflows/main.yml/badge.svg)](https://github.com/vicenteneto/python-cartolafc/actions/workflows/main.yml)
[![Development Status](http://img.shields.io/:status-production/stable-brightgreen.svg)](https://github.com/vicenteneto/python-cartolafc)
[![License](http://img.shields.io/:license-mit-blue.svg)](https://github.com/vicenteneto/python-cartolafc/blob/main/LICENSE)

Uma interface em Python para a API Rest do Cartola FC.


# Índice

- [Sobre este projeto](#sobre-este-projeto)
- [Versões](#versoes)
- [Instalação](#instalacao)
- [Exemplo](#exemplo)
- [Contribuintes](#contribuintes)
- [Direitos autorais e licença](#direitos-autorais-e-licenca)


## Sobre este projeto

Este projeto é uma interface em Python para a API REST do Cartola FC. [Cartola FC](https://cartolafc.globo.com/) é um 
esporte fantasy sobre futebol, ou seja, é um jogo fictício no qual as pessoas montam seus times com jogadores de futebol 
da vida real. Foi lançado no ano de 2005.

Criado e mantido por [Globo.com](http://www.globo.com/) e promovido pelo canal de TV por assinatura 
[Sportv](http://sportv.globo.com/), este jogo de futebol virtual conta com mais de 5 milhões de usuários registrados. 
Logo na abertura da temporada 2016, o jogo registrou a sua melhor marca entre times escalados em uma única rodada em 12 
anos de história do fantasy, incríveis 2.723.915 de usuários montaram as suas equipes para a primeira rodada do 
Campeonato Brasileiro de 2016. A 10ª rodada do Campeonato Brasileiro de 2017 instituiu um novo recorde, onde 5.540.835
times foram escalados no jogo.


## Versões

Este projeto foi testado e funciona em Python 3.8, 3.9 e 3.10.


## Instalação

PyPI:

```bash
    $ pip install Python-CartolaFC
```

Ou baixando o código fonte e executando:

```bash
    $ python setup.py install
```

Versão em desenvolvimento:

```bash
    $ pip install git+https://github.com/vicenteneto/python-cartolafc.git#egg=Python-CartolaFC
```


## Exemplo

A API Python-CartolaFC destina-se a mapear os objetos no CartolaFC (por exemplo, Atleta, Clube, Liga, Equipe) em objetos 
Python facilmente gerenciados:

```python
>>> import cartolafc
>>> api = cartolafc.Api()
>>> time = api.time(nome='Falydos FC')
>>> time.ultima_pontuacao
48.889892578125
>>> time.info.nome
'Falydos FC'
```

Mais exemplos disponíveis no Github:
[https://github.com/vicenteneto/python-cartolafc/tree/main/examples](https://github.com/vicenteneto/python-cartolafc/tree/main/examples)


## Contribuintes

Identificou algum bug ou tem alguma requisição de funcionalidade nova?
[Por favor, abra uma nova issue](https://github.com/vicenteneto/python-cartolafc/issues/new>).


## Direitos autorais e licença

Copyright 2017-, Vicente Neto. Este projeto é licenciado sob a 
[Licença MIT](https://github.com/vicenteneto/python-cartolafc/blob/main/LICENSE).
