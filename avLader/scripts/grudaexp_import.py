# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.fme
import AGILib.folder_files
import os
import sys
import datetime
import shutil
import glob
import zipfile

def getSuffix(filename):
    filename_only = os.path.basename(filename)
    without_extension = os.path.splitext(filename_only)[0]
    suffix = without_extension.split("gruda_export")[1]
    return suffix

def renameCSVFile(prefix, dirname, suffix):
    old_name = os.path.join(dirname, prefix + suffix + ".csv")
    new_name = os.path.join(dirname, prefix + ".csv")
    os.rename(old_name, new_name)

def run():
    subcommand = 'grudaexp_import'
    config = avLader.helpers.helper.get_config(subcommand)
    logger = config['LOGGING']['logger']
    logger.info("%s wird ausgeführt." % (subcommand))
    
    # GRUDA-Export herunterladen und vorbereiten
    logger.info("Daten werden vorbereitet.")
    list_of_files = glob.glob(config['DIRECTORIES']['gruda_lieferung']) 
    latest_file = max(list_of_files, key=os.path.getctime)

    # Die CSV-Files heissen bei jedem Export anders.
    # Sie haben immer ein Zeit- und Datumsbasiertes Suffix
    # Es wird ermittelt, damit die CSV-Filenamen manipuliert
    # werden können.
    suffix = getSuffix(latest_file)
    logger.info("Suffix: " + suffix)
    
    zip_file_ori = os.path.join(config['DIRECTORIES']['gruda_lieferung'], latest_file)
    zip_filename = config['DIRECTORIES']['gruda_filename']

    zip_file = os.path.join(config['DIRECTORIES']['local_data_dir'], zip_filename)
    
    # copy and replace old zip-file
    shutil.copyfile(zip_file_ori, zip_file)
    logger.info("Datei wird kopiert von " + zip_file_ori + " nach " + zip_file)

    # Lösche allfällige CSV-Files in local_data_dir
    filestodelete = glob.glob(os.path.join(config['DIRECTORIES']['local_data_dir'], "*.csv"))
    logger.info("Lösche CSV-Files in " + config['DIRECTORIES']['local_data_dir'])
    for f in filestodelete:
        logger.info(f)
        os.remove(os.path.join(config['DIRECTORIES']['local_data_dir'], f))
    
    # Zipfile entpacken
    with zipfile.ZipFile(zip_file) as grudazip:
        logger.info("Entpacke Zipfile " + zip_file)
        grudazip.extractall(config['DIRECTORIES']['local_data_dir'])

    # CSV-Files umbenennen
    csv_filenames = ["gebaeude", "grundstueck_gebaeude", "gebaeude_eingang_adresse", "grundstueck", "bodenbedeckung_anteil"]
    for csv_filename in csv_filenames:
        logger.info("Benenne CSV-File um: " + csv_filename)
        renameCSVFile(csv_filename, config['DIRECTORIES']['local_data_dir'], suffix)

    csv_folder_fme = os.path.join(config['DIRECTORIES']['local_data_dir'], "*.csv")

    # FME-Import ausführen
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_script_logfile = os.path.join(config['LOGGING']['log_directory'], subcommand + "_fme.log")

    parameters = {
        'DATABASE': str(config['NORM_TEAM']['database']),
        'USERNAME': str(config['NORM_TEAM']['username']),
        'PASSWORD': str(config['NORM_TEAM']['password']),
        'CSVFOLDER': str(csv_folder_fme)
    }  

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile)
    fme_runner = AGILib.fme.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()         

    # QA-Script ausführen
    fme_script_qa = os.path.splitext(__file__)[0] + "_qa.fmw"
    fme_script_logfile_qa = os.path.join(config['LOGGING']['log_directory'], subcommand + "_qa_fme.log")
    
    qa_filename = os.path.join(config['LOGGING']['log_directory'], subcommand + "_qa.xlsx")
    AGILib.folder_files.rename_file_with_timestamp(qa_filename)
    logger.info("Das QA-Excelfile lautet: " + qa_filename)

    parameters_qa = {
        'NORM_DATABASE': str(config['NORM_TEAM']['database']),
        'NORM_USERNAME': str(config['NORM_TEAM']['username']),
        'NORM_PASSWORD': str(config['NORM_TEAM']['password']),
        'VEK1_DATABASE': str(config['GEO_VEK1']['database']),
        'VEK1_USERNAME': str(config['GEO_VEK1']['username']),
        'VEK1_PASSWORD': str(config['GEO_VEK1']['password']),
        'QA_EXCEL': str(qa_filename)
    }

    logger.info("Script " +  fme_script_qa + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile_qa)
    fme_runner_qa = AGILib.fme.FMERunner(fme_workbench=fme_script_qa, fme_workbench_parameters=parameters_qa, fme_logfile=fme_script_logfile_qa, fme_logfile_archive=True)
    fme_runner_qa.run()
    
    avLader.helpers.helper.delete_connection_files(config, logger)

