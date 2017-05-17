"""
    Python Cartola FC API
    ---------------------
    A python interface into the Cartola FC API.

    :copyright: (c) 2017 by Vicente Neto.
    :license: MIT, see LICENSE for more details.

    Links
    `````

    * `documentation <https://pythonhosted.org/Python-CartolaFC>`_
    * `development version <http://github.com/vicenteneto/python-cartolafc/zipball/master#egg=Python-CartolaFC-dev>`_
"""
from setuptools import setup

version = '0.5.17'
packages = ['cartolafc']
install_requires = ['requests']
python_cartolafc_pkg_data = []

setup(
    name='Python-CartolaFC',
    version=version,
    description='A python interface into the Cartola FC API',
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
