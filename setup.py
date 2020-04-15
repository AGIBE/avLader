# -*- coding: utf-8 -*-
# übernommen aus: https://pythonhosted.org/setuptools/setuptools.html#id24
import ez_setup
from avLader import __version__
import avLader
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
      name = "avLader",
      packages = find_packages(),
      version = __version__,
      # .fmw-Files werden von Python nicht erkannt. Deshalb müssen sie explizit als Package-Inhalt aufgelistet werden.
      package_data={'': ["*.fmw"]},
      # Abhängigkeiten
      install_requires = ["AGILib>=0.3"],
      # PyPI metadata
      author = "Peter Schär, Martina Köhli",
      author_email = "peter.schaer@be.ch,martina.koehli@be.ch",
      description = "Import-Applikation AV- und LK-Daten Kanton Bern",
      url = "http://www.be.ch/geoportal",
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
    entry_points={
         'console_scripts': [
              'avLader = avLader.helpers.commandline_helper:main',
              'al = avLader.helpers.commandline_helper:main'
          ]
    }
)