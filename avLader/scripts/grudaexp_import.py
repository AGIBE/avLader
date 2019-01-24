# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.fme_helper
import fmeobjects
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
    config = avLader.helpers.config_helper.get_config('grudaexp_import')
    logger = config['LOGGING']['logger']
    logger.info("GRUDAEXP-Import wird ausgeführt.")
    
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

    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = avLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory'])
    
    fme_script_qa = os.path.splitext(__file__)[0] + "_qa.fmw"
    fme_logfile_qa = avLader.helpers.fme_helper.prepare_fme_log(fme_script_qa, config['LOGGING']['log_directory'])
    
    qa_filename = "grudaexp_import_qa" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".xlsx"
    qa_file = os.path.join(config['LOGGING']['log_directory'], qa_filename)
    logger.info("Das QA-Excelfile lautet: " + qa_file)
    
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)

    # Import-Script
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'DATABASE': str(config['NORM_TEAM']['database']),
        'USERNAME': str(config['NORM_TEAM']['username']),
        'PASSWORD': str(config['NORM_TEAM']['password']),
        'CSVFOLDER': str(csv_folder_fme),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()    
    
    logger.info("Script " +  fme_script_qa + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile_qa)
    
    # QA-Script
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'NORM_DATABASE': str(config['NORM_TEAM']['database']),
        'NORM_USERNAME': str(config['NORM_TEAM']['username']),
        'NORM_PASSWORD': str(config['NORM_TEAM']['password']),
        'VEK1_DATABASE': str(config['GEO_VEK1']['database']),
        'VEK1_USERNAME': str(config['GEO_VEK1']['username']),
        'VEK1_PASSWORD': str(config['GEO_VEK1']['password']),
        'QA_EXCEL': str(qa_file),
        'LOGFILE': str(fme_logfile_qa)
    }
    try:
        runner.runWithParameters(str(fme_script_qa), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("QA-FME wird abgebrochen!")
        sys.exit()
    
    avLader.helpers.connection_helper.delete_connection_files(config, logger)

