import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='facebookmarketing-python',
      version='1.1.1',
      description='API wrapper for Facebook written in Python',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      url='https://github.com/GearPlug/facebookmarketing-python',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      license='MIT',
      packages=['facebookmarketing'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
