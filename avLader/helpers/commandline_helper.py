# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from avLader import __version__
import avLader.scripts.gruda_upload
import avLader.scripts.grudaexp_import
import avLader.scripts.mopube_import
import avLader.scripts.dipanu_import
import avLader.scripts.gebadr_import
import avLader.scripts.fds_import

def run_gruda_upload(args):
    avLader.scripts.gruda_upload.run()
    print("GRUDA-Upload SUCCESSFUL!")
    
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

def main():
    version_text = "avLader v" + __version__
    parser = argparse.ArgumentParser(description="Kommandozeile fuer den avLader. Führt die verschiedenen Tasks des wöchentlichen AV-Imports aus.", prog="avLader.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # GRUDA_UPLOAD-Befehl
    gruda_upload_parser = subparsers.add_parser('gruda_upload', help='Lädt den Gruda-Export per FTP herunter und lädt ihn auf den infoGrips-Server.')
    gruda_upload_parser.set_defaults(func=run_gruda_upload)
    
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
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()