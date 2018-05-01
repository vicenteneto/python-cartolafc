# -*- coding: utf-8 -*-

"""
    Python Cartola FC API
    ---------------------
    Uma interface em Python para a API Rest do Cartola FC.

    :copyright: (c) 2017 por Vicente Neto.
    :license: MIT, veja LICENSE para mais detalhes.

    Links
    `````

    * `documentation <https://pythonhosted.org/Python-CartolaFC>`_
    * `development version <http://github.com/vicenteneto/python-cartolafc/zipball/master#egg=Python-CartolaFC-dev>`_
"""
from setuptools import setup

version = '1.5.1'
packages = ['cartolafc']
install_requires = ['pytz', 'redis', 'requests']
python_cartolafc_pkg_data = []

try:
    long_description = unicode(open('README.md').read(), errors='ignore')
except Exception:
    long_description = open('README.md', errors='ignore').read()

setup(
    name='Python-CartolaFC',
    version=version,
    description='Uma interface em Python para a API Rest do Cartola FC',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vicenteneto/python-cartolafc',
    author='Vicente Neto',
    author_email='sneto.vicente@gmail.com',
    license='MIT',
    packages=packages,
    install_requires=install_requires,
    package_data={'cartolafc': python_cartolafc_pkg_data},
    zip_safe=False,
    keywords=['python', 'cartolafc', 'api'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
