# -*- coding: utf-8 -*-

import types

from cartolafc.error import CartolaFCError


class RequiresAuthentication(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return types.MethodType(self, instance, owner)

    def __call__(self, api, *args, **kwargs):
        if not api._glb_id:
            raise CartolaFCError('Esta função requer autenticação')

        return self.func(api, *args, **kwargs)
