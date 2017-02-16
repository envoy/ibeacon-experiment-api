# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='ibeacon_api',
    version='1.0.0',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'pytz',
        'psycopg2',
        'iso8601',
    ],
)
