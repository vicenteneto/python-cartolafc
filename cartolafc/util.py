# -*- coding: utf-8 -*-

import json
import logging
import re
import unicodedata

from cartolafc.error import CartolaFCError, CartolaFCOverloadError


def _strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (NameError, TypeError):  # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)
    return str(text.encode('ascii', 'ignore').decode('utf-8'))


def convert_team_name_to_slug(name):
    """
    Convert input text to slug.

    :param name: The input string.
    :type name: String.

    :returns: The slug.
    :rtype: String.
    """
    slug = _strip_accents(name.lower())
    slug = re.sub(r'--', '-', re.sub(r'[^a-z0-9]', '-', slug))
    return slug[:-1] if slug.endswith('-') else slug


def parse_and_check_cartolafc(json_data):
    """
    Try and parse the JSON returned from Cartola FC API and return an empty dictionary if there is any error.
    This is a purely defensive check because during some Cartola FC API network outages it can return an error page.
    """
    try:
        data = json.loads(json_data)
        if 'mensagem' in data:
            logging.error(data['mensagem'])
            raise CartolaFCError(data['mensagem'].encode('utf-8'))
        return data
    except ValueError as error:
        logging.error('Error parsing and checking json data: %s', json_data)
        logging.error(error)
        raise CartolaFCOverloadError('Globo.com - Desculpe-nos, nossos servidores estão sobrecarregados.')
