# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.fme_helper
import fmeobjects
import os
import sys

def run():
    config = avLader.helpers.config_helper.get_config('grudaexp_import')
    logger = config['LOGGING']['logger']
    logger.info("GRUDAEXP-Import wird ausgeführt.")
    
    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = avLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory'])

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    itf_file = os.path.join(config['DIRECTORIES']['gruda'], config['GRUDA_FTP']['filename'])
    
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'DATABASE': str(config['NORM_TEAM']['database']),
        'USERNAME': str(config['NORM_TEAM']['username']),
        'PASSWORD': str(config['NORM_TEAM']['password']),
        'MODELLABLAGE': str(config['DIRECTORIES']['models']),
        'ITF_FILE': str(itf_file),
        'LOGFILE': str(fme_logfile)
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()    
    
    avLader.helpers.connection_helper.delete_connection_files(config, logger)

