from setuptools import setup, find_packages

with open("requierements.txt") as f:
    requierements = f.read()

classifiers = [
    'Programming Language :: Python :: 3.6'
]

setup(
  name='ApiGitHub_Connector',
  description='This packages is a wrapper for the GitHub API',
  author='Justin Valet',
  author_email='jv.datamail@gmail.com',
  version='0.0.1',
  classifiers=classifiers,
  requierements=requierements,
  packages=find_packages(),
  url='https://github.com/JustinValet/ApiGitHub_Connector',
  license=''
)