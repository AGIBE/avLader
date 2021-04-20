# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.fme
import AGILib.folder_files
import os
import datetime
import sys

def run():
    subcommand = 'gebadr_import'
    config = avLader.helpers.helper.get_config(subcommand)
    logger = config['LOGGING']['logger']
    logger.info("%s wird ausgeführt." % (subcommand))
    
    # Import-Script ausführen
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_script_logfile = os.path.join(config['LOGGING']['log_directory'], subcommand + "_fme.log")

    parameters = {
        'NORM_CONNECTIONFILE': config['NORM_TEAM']['connection_file'],
        'AV01_CONNECTIONFILE': config['AV01_WORK']['connection_file'],
        'GPS1_CONNECTIONFILE': config['GPS1_WORKH']['connection_file'],
        'VEK1_CONNECTIONFILE': config['GEO_VEK1']['connection_file']
    }

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile)
    fme_runner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()    
    if fme_runner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))

    # QA-Script ausführen
    fme_script_qa = os.path.splitext(__file__)[0] + "_qa.fmw"
    fme_script_logfile_qa = os.path.join(config['LOGGING']['log_directory'], subcommand + "_qa_fme.log")
    
    qa_filename = os.path.join(config['LOGGING']['log_directory'], subcommand + "_qa.xlsx")
    if os.path.exists(qa_filename):
        AGILib.folder_files.rename_file_with_timestamp(qa_filename)
    logger.info("Das QA-Excelfile lautet: " + qa_filename)

    parameters_qa = {
        'NORM_DATABASE': config['NORM_TEAM']['database'],
        'NORM_USERNAME': config['NORM_TEAM']['username'],
        'NORM_PASSWORD': config['NORM_TEAM']['password'],
        'VEK1_DATABASE': config['GEO_VEK1']['database'],
        'VEK1_USERNAME': config['GEO_VEK1']['username'],
        'VEK1_PASSWORD': config['GEO_VEK1']['password'],
        'QA_EXCEL': qa_filename
    }
    
    logger.info("Script " +  fme_script_qa + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile_qa)
    fme_runner_qa = AGILib.FMERunner(fme_workbench=fme_script_qa, fme_workbench_parameters=parameters_qa, fme_logfile=fme_script_logfile_qa, fme_logfile_archive=True)
    fme_runner_qa.run()
    if fme_runner_qa.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script_qa))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script_qa))

    avLader.helpers.helper.delete_connection_files(config, logger)