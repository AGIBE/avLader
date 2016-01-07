# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import os
import fmeobjects
import sys
import datetime

def run():
    config = avLader.helpers.config_helper.get_config('dipanu_import')
    logger = config['LOGGING']['logger']
    logger.info("DIPANU-Import wird ausgeführt.")
    
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = avLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory'])
    
    fme_script_qa = os.path.splitext(__file__)[0] + "_qa.fmw"
    fme_logfile_qa = avLader.helpers.fme_helper.prepare_fme_log(fme_script_qa, config['LOGGING']['log_directory'])
    
    qa_filename = "dipanu_import_qa" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".xls"
    qa_file = os.path.join(config['LOGGING']['log_directory'], qa_filename)
 

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    # Import-Script
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'NORM_DATABASE': str(config['NORM_TEAM']['database']),
        'NORM_USERNAME': str(config['NORM_TEAM']['username']),
        'NORM_PASSWORD': str(config['NORM_TEAM']['password']),
        'AV01_DATABASE': str(config['AV01_WORKH']['database']),
        'AV01_USERNAME': str(config['AV01_WORKH']['username']),
        'AV01_PASSWORD': str(config['AV01_WORKH']['password']),
        'GPS1_DATABASE': str(config['GPS1_WORKH']['database']),
        'GPS1_USERNAME': str(config['GPS1_WORKH']['username']),
        'GPS1_PASSWORD': str(config['GPS1_WORKH']['password']),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
        pass
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
        logger.error("Import wird abgebrochen!")
        sys.exit()
    
    avLader.helpers.connection_helper.delete_connection_files(config, logger)