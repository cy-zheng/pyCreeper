from setuptools import setup, find_packages

setup(
    name="pycreeper",
    version="1.0.0",
    description='''Creepers feel like a web crawler:
                    slow growth and and wide coverage.''',
    author="zcy",
    author_email="zhengchenyu.backend@gmail.com",
    url="https://github.com/ZcyAndWt/pyCreeper",
    license="LGPL",
    packages=find_packages(exclude=('doc', 'doc.*', 'tests', 'tests.*', 'examples', 'examples.*')),
    install_requires=[
        'gevent>=1.2.1',
        'importlib>=1.0.4',
        'requests>=2.8.1',
        'chardet>=2.3.0',
        'w3lib>=1.16.0',
        'six>=1.9.0',
        'pybloom>=1.1',
        'selenium>=2.48.0'
    ],
    )
