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
      install_requires = ["configobj==5.0.6", "cx-Oracle>=5.1.3", "python-keyczar==0.715", "chromalog==1.0.4"],
      # PyPI metadata
      author = "Peter Schär",
      author_email = "peter.schaer@bve.be.ch",
      description = "Import-Applikation AV-Daten Kanton Bern",
      url = "http://www.be.ch/geoportal",
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
    entry_points={
         'console_scripts': [
              'avLader = avLader.helpers.commandline_helper:main',
              'al = avLader.helpers.commandline_helper:main'
          ]
    }
)