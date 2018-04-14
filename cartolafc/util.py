# -*- coding: utf-8 -*-

import datetime
import json
import logging
import re
import unicodedata

from .errors import CartolaFCError, CartolaFCOverloadError


def _strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except (NameError, TypeError):  # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)
    return str(text.encode('ascii', 'ignore').decode('utf-8'))


def convert_team_name_to_slug(name):
    slug = _strip_accents(name.lower())
    slug = re.sub(r'--', '-', re.sub(r'[^a-z0-9]', '-', slug))
    return slug[:-1] if slug.endswith('-') else slug


def json_default(value):
    if isinstance(value, datetime.datetime):
        return dict(year=value.year, month=value.month, day=value.day, hour=value.hour, minute=value.minute,
                    second=value.second, microsecond=value.microsecond, tzinfo=value.tzinfo)
    return value.__dict__


def parse_and_check_cartolafc(json_data):
    try:
        data = json.loads(json_data)
        if 'mensagem' in data and data['mensagem']:
            logging.error(data['mensagem'])
            raise CartolaFCError(data['mensagem'].encode('utf-8'))
        return data
    except ValueError as error:
        logging.error('Error parsing and checking json data: %s', json_data)
        logging.error(error)
        raise CartolaFCOverloadError('Globo.com - Desculpe-nos, nossos servidores estão sobrecarregados.')
