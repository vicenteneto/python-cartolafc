# -*- coding: utf-8 -*-

from .errors import CartolaFCError


class RequiresAuthentication(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def __call__(self, *args, **kwargs):
        if not self.instance._glb_id:
            raise CartolaFCError('Esta função requer autenticação')

        return self.func(self.instance, *args, **kwargs)
