.. _quickstart:

Quickstart
==========

Ansioso para começar? Esta página fornece uma boa introdução ao CartolaFC API. Ele assume que você já tem o projeto
instalado. Se não o fizer, dirija-se à sessão :ref:`installation`.

Este projeto destina-se a mapear os objetos no CartolaFC (por exemplo, Atleta, Clube, Liga, Equipe) em objetos Python
facilmente gerenciados.


Um exemplo básico
-----------------

Um uso mínimo desta biblioteca se parece com algo assim::

    from cartolafc import Api


    api = Api()
    time = api.time('Falydos FC')


Então, o que este código faz?

1. Primeiro importamos a classe :class:`~cartolafc.Api`. Uma instância desta classe será a nossa interface para a API do
CartolaFC.
2. Em seguida, criamos uma instância dessa classe.
3. Em seguida, usamos o método :meth:`~cartolafc.Api.time`. Para obter mais informações, consulte a documentação.


Mais exemplos
-------------

Mais exemplos disponíveis no `Github <https://github.com/vicenteneto/python-cartolafc/tree/master/examples>`__.
