from setuptools import setup, find_packages

setup(
      name="pycreeper",
      version="0.0.1",
      description='''Creepers feel like a web crawler:
                       slow growth and and wide coverage.''',
      author="zcy",
      author_email="zhengchenyu.backend@gmail.com",
      url="http://blog.csdn.net/zcy19941015",
      license="LGPL",
      packages=find_packages(exclude=('tests', 'tests.*'))
      )
