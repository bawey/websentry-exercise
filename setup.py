from setuptools import setup, find_packages

setup(
    name='websentry',
    version='0.1.0',
    author='Tomek Bawej',
    packages=find_packages(include=['websentry', 'websentry.*']),
    install_requires=[
        'pykafka>=2.8.0',
        'requests>=2.22.0',
        'psycopg2-binary>=2.8.6',
    ]
)
