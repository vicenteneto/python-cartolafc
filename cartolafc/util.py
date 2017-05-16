import re
import unicodedata


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
    except NameError:  # unicode is a default on python 3
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
