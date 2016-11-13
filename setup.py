from setuptools import setup, find_packages
setup(
      name="zcy_test",
      version="0.0.1",
      description="My test module",
      author="zcy",
      author_email="zcy19941015@qq.com",
      url="http://www.csdn.net",
      license="LGPL",
      packages= find_packages(),
      scripts=["zcy_test/test1.py"],
      )