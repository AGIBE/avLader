# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from avLader import __version__
import avLader.scripts.itf_download
import avLader.scripts.grudaexp_import
import avLader.scripts.mopube_import
import avLader.scripts.dipanu_import
import avLader.scripts.gebadr_import
import avLader.scripts.fds_import
import avLader.scripts.release
import avLader.scripts.oereb_liegenschaften
import avLader.scripts.oereb_adressen
import avLader.scripts.lk_import

def run_itf_download(args):
    avLader.scripts.itf_download.run()
    print("ITF-Download SUCCESSFUL!")
    
def run_grudaexp_import(args):
    avLader.scripts.grudaexp_import.run()
    print("GRUDAEXP-Import SUCCESSFUL!")
    
def run_mopube_import(args):
    avLader.scripts.mopube_import.run()
    print("MOPUBE-Import SUCCESSFUL!")
    
def run_dipanu_import(args):
    avLader.scripts.dipanu_import.run()
    print("DIPANU-Import SUCCESSFUL!")
    
def run_gebadr_import(args):
    avLader.scripts.gebadr_import.run()
    print("GEBADR-Import SUCCESSFUL!")
    
def run_fds_import(args):
    avLader.scripts.fds_import.run()
    print("FDS-Import SUCCESSFUL!")
    
def run_grudaexp_release(args):
    avLader.scripts.release.release('GRUDAEXP')
    print("GRUDAEXP-Release SUCCESSFUL!")
    
def run_mopube_release(args):
    avLader.scripts.release.release('MOPUBE')
    print("MOPUBE-Release SUCCESSFUL!")

def run_dipanu_release(args):
    avLader.scripts.release.release('DIPANU')
    print("DIPANU-Release SUCCESSFUL!")

def run_gebadr_release(args):
    avLader.scripts.release.release('GEBADR')
    print("GEBADR-Release SUCCESSFUL!")
    
def run_oereb_liegenschaften(args):
    avLader.scripts.oereb_liegenschaften.run()
    print("ÖREB-Liegenschaften SUCCESSFUL!")

def run_oereb_adressen(args):
    avLader.scripts.oereb_adressen.run()
    print("ÖREB-Adressen SUCCESSFUL!")
    
def run_lk_import(args):
    avLader.scripts.lk_import.run()
    print("LK-Import SUCCESSFUL!")

def run_lkmeta_release(args):
    avLader.scripts.release.release('LKMETA')
    print("LKMETA-Release SUCCESSFUL!")
    
def run_lkmap_release(args):
    avLader.scripts.release.release('LKMAP')
    print("LKMAP-Release SUCCESSFUL!")

def main():
    version_text = "avLader v" + __version__
    parser = argparse.ArgumentParser(description="Kommandozeile fuer den avLader. Führt die verschiedenen Tasks des wöchentlichen AV-Imports aus.", prog="avLader.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # ITF_DOWNLOAD-Befehl
    itf_download_parser = subparsers.add_parser('itf_download', help="Lädt die originalen ITF-Dateien aller Gemeinden herunter.")
    itf_download_parser.set_defaults(func=run_itf_download)
    
    # GRUDAEXP_IMPORT-Befehl
    grudaexp_import_parser = subparsers.add_parser('grudaexp_import', help='Produziert das Geoprodukt GRUDAEXP aus dem Gruda-Export-Interlis.')
    grudaexp_import_parser.set_defaults(func=run_grudaexp_import)
    
    # MOPUBE_IMPORT-Befehl
    mopube_import_parser = subparsers.add_parser('mopube_import', help='Importiert das Geoprodukt MOPUBE aus der gelieferten Filegeodatabase.')
    mopube_import_parser.set_defaults(func=run_mopube_import)
    
    # DIPANU_IMPORT-Befehl
    dipanu_import_parser = subparsers.add_parser('dipanu_import', help='Produziert das Geoprodukt DIPANU aus den AV-Daten und dem Gruda-Export.')
    dipanu_import_parser.set_defaults(func=run_dipanu_import)
    
    # GEBADR_IMPORT-Befehl
    gebadr_import_parser = subparsers.add_parser('gebadr_import', help='Produziert das Geoprodukt GEBADR aus den AV-Daten und dem Gruda-Export.')
    gebadr_import_parser.set_defaults(func=run_gebadr_import)
    
    # FDS_IMPORT-Befehl
    fds_import_parser = subparsers.add_parser('fds_import', help='Importiert den AV-Fachdatensatz aus der gelieferten Filegeodatabase.')
    fds_import_parser.set_defaults(func=run_fds_import)
    
    # GRUDAEXP_RELEASE-Befehl
    grudaexp_release_parser = subparsers.add_parser('grudaexp_release', help='Gibt GRUDAEXP frei für den iLader-Import.')
    grudaexp_release_parser.set_defaults(func=run_grudaexp_release)
    
    # MOPUBE_RELEASE-Befehl
    mopube_release_parser = subparsers.add_parser('mopube_release', help='Gibt MOPUBE frei für den iLader-Import.')
    mopube_release_parser.set_defaults(func=run_mopube_release)
    
    # DIPANU_RELEASE-Befehl
    dipanu_release_parser = subparsers.add_parser('dipanu_release', help='Gibt DIPANU frei für den iLader-Import.')
    dipanu_release_parser.set_defaults(func=run_dipanu_release)

    # GEBADR_RELEASE-Befehl
    gebadr_release_parser = subparsers.add_parser('gebadr_release', help='Gibt GEBADR frei für den iLader-Import.')
    gebadr_release_parser.set_defaults(func=run_gebadr_release)
    
    # OEREB_LIEGENSCHAFTEN-Befehl
    oereb_liegenschaften_parser = subparsers.add_parser('oereb_liegenschaften', help='Aktualisiert den ÖREBK-Liegenschaftslayer.')
    oereb_liegenschaften_parser.set_defaults(func=run_oereb_liegenschaften)

    # OEREB_ADRESSEN-Befehl
    oereb_adressen_parser = subparsers.add_parser('oereb_adressen', help='Aktualisiert den ÖREBK-Adresslayer.')
    oereb_adressen_parser.set_defaults(func=run_oereb_adressen)
    
    # LK_IMPORT-Befehl
    lk_import_parser = subparsers.add_parser('lk_import', help='Importiert LKMETA und LKMAP von der Rampe ins NORM.')
    lk_import_parser.set_defaults(func=run_lk_import)
    
    # LKMETA_RELEASE-Befehl
    gebadr_release_parser = subparsers.add_parser('lkmeta_release', help='Gibt LKMETA frei für den iLader-Import.')
    gebadr_release_parser.set_defaults(func=run_lkmeta_release)
    
    # LKMAP_RELEASE-Befehl
    gebadr_release_parser = subparsers.add_parser('lkmap_release', help='Gibt LKMAP frei für den iLader-Import.')
    gebadr_release_parser.set_defaults(func=run_lkmap_release)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()