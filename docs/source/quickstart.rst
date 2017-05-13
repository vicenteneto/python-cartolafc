.. _quickstart:

Quickstart
==========

Eager to get started?  This page gives a good introduction to Python CartolaFC API. It assumes you already have Python
CartolaFC installed.  If you do not, head over to the :ref:`installation` section.

Python-CartolaFC API is intended to map the objects in CartolaFC (e.g. Athlete, Club, League, Team) into easily managed
Python objects.

A Minimal Usage
---------------

A minimal Python Cartola FC API usage looks something like this::

    from cartolafc import Api


    api = Api()
    team = api.get_team('Falydos FC')


So what did that code do?

1. First we imported the :class:`~cartolafc.Api` class. An instance of this class will be our interface into the
   CartolaFC API.
2. Next we create an instance of this class.
3. We then use the :meth:`~cartolafc.Api.get_team`. For more information have a look at the documentation.


More examples
-------------

More examples available on `Github <https://github.com/vicenteneto/python-cartolafc/tree/master/examples>`__.