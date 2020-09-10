# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.downloader
import AGILib.fme
import AGILib.folder_files
import zipfile
import os
import arcpy
import sys
import shutil
import time
import datetime

def run():
    subcommand = 'mopube_import'
    config = avLader.helpers.helper.get_config(subcommand)
    logger = config['LOGGING']['logger']
    logger.info("%s wird ausgeführt." % (subcommand))
    
    mopube_objects = [
        'MOPUBE_BBARTT',
        'MOPUBE_BBF',
        'MOPUBE_BBPRJF',
        'MOPUBE_BBPRJTXT',
        'MOPUBE_BBTXT',
        'MOPUBE_EOARTT',
        'MOPUBE_EOF',
        'MOPUBE_EOFTXT',
        'MOPUBE_EOL',
        'MOPUBE_EOLTXT',
        'MOPUBE_EOP',
        'MOPUBE_EOPTXT',
        'MOPUBE_FIXP',
        'MOPUBE_FPKATT',
        'MOPUBE_GAEINP',
        'MOPUBE_GAEINTXT',
        'MOPUBE_GASTRNA',
        'MOPUBE_GASTRNAT',
        'MOPUBE_GUELTIGT',
        'MOPUBE_HGABSCHL',
        'MOPUBE_HGARTT',
        'MOPUBE_HGF',
        'MOPUBE_HGL',
        'MOPUBE_HGP',
        'MOPUBE_HGPRJF',
        'MOPUBE_HGTYPT',
        'MOPUBE_HOAUSPAT',
        'MOPUBE_HOAUSSPA',
        'MOPUBE_HOEHEP',
        'MOPUBE_HOGELKAN',
        'MOPUBE_HOGELKAT',
        'MOPUBE_HOHK',
        'MOPUBE_LAGEZUVT',
        'MOPUBE_LIARTT',
        'MOPUBE_LIF',
        'MOPUBE_LIGP',
        'MOPUBE_LIL',
        'MOPUBE_LILARTT',
        'MOPUBE_LIPRJF',
        'MOPUBE_LIPRJTXT',
        'MOPUBE_LISRF',
        'MOPUBE_LISRL',
        'MOPUBE_LISRPRJF',
        'MOPUBE_LISRPRJT',
        'MOPUBE_LISRTXT',
        'MOPUBE_LITXT',
        'MOPUBE_LIVOLLT',
        'MOPUBE_NOKATT',
        'MOPUBE_NONAMF',
        'MOPUBE_NONAMTXT',
        'MOPUBE_NUMNAMET',
        'MOPUBE_OFFBEZT',
        'MOPUBE_PKTZT',
        'MOPUBE_QUALIT',
        'MOPUBE_RLF',
        'MOPUBE_RLFTXT',
        'MOPUBE_RLL',
        'MOPUBE_RLLTXT',
        'MOPUBE_RLMEDIT',
        'MOPUBE_RLP',
    ]
    
    mopube_zipfile = config['ZAV_FTP']['mopube_filename']
    downloaded_zip = os.path.join(config['DIRECTORIES']['local_data_dir'], mopube_zipfile)
    source_fgdb = os.path.splitext(downloaded_zip)[0]

    avLader.helpers.helper.download_zav_fgdb(mopube_zipfile, downloaded_zip, source_fgdb, config)

    export_zip = os.path.join(config['DIRECTORIES']['zips'], "MOPUBE.zip")
    logger.info("Export-ZIP wird kopiert nach " + export_zip)
    shutil.copy2(downloaded_zip, export_zip)
      
    target_sde = config['NORM_TEAM']['connection_file']
      
    for mopube_object in mopube_objects:
        logger.info("Importiere " + mopube_object)
        source_object = os.path.join(source_fgdb, mopube_object)
        target_object = os.path.join(target_sde, config['NORM_TEAM']['username'] + "." + mopube_object)
        avLader.helpers.helper.append(object=mopube_object, source_object=source_object, target_object=target_object, config=config)

    # QA-Script ausführen
    fme_script_qa = os.path.splitext(__file__)[0] + "_qa.fmw"
    fme_script_logfile = os.path.join(config['LOGGING']['log_directory'], subcommand + "_qa_fme.log")
    qa_filename = os.path.join(config['LOGGING']['log_directory'], subcommand + "_qa.xlsx")

    # Wenn das QA-File bereits existiert, wird es umbenannt
    if os.path.exists(qa_filename):
        AGILib.folder_files.rename_file_with_timestamp(qa_filename)
    logger.info("Das QA-Excelfile lautet: " + qa_filename)

    parameters = {
        'NORM_DATABASE': str(config['NORM_TEAM']['database']),
        'NORM_USERNAME': str(config['NORM_TEAM']['username']),
        'NORM_PASSWORD': str(config['NORM_TEAM']['password']),
        'VEK1_DATABASE': str(config['GEO_VEK1']['database']),
        'VEK1_USERNAME': str(config['GEO_VEK1']['username']),
        'VEK1_PASSWORD': str(config['GEO_VEK1']['password']),
        'QA_EXCEL': str(qa_filename)
    }

    fme_runner = AGILib.fme.FMERunner(fme_workbench=fme_script_qa, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()    
    
    avLader.helpers.helper.delete_connection_files(config, logger)