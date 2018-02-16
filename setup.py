from setuptools import setup

setup(name='facebookmarketing-python',
      version='0.1',
      description='API wrapper for Facebook written in Python',
      url='https://github.com/GearPlug/facebookmarketing-python',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      license='GPL',
      packages=['facebookmarketing'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
