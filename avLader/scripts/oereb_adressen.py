# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import fmeobjects
import sys
import os

def run():
    config = avLader.helpers.config_helper.get_config('oereb_adressen')
    
    logger = config['LOGGING']['logger']
    logger.info("ÖREB-Adresslayer wird aktualisiert.")

    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_logfile = avLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory'])

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'TEAM_CONNECTIONFILE': str(config['NORM_TEAM']['connection_file']),
        'VEK2_CONNECTIONFILE': str(config['GEODB_VEK2']['connection_file']),
        'OEREB_PG_DATABASE': str(config['OEREB_VEK2_PG']['database']),
        'OEREB_PG_USERNAME': str(config['OEREB_VEK2_PG']['username']),
        'OEREB_PG_PASSWORD': str(config['OEREB_VEK2_PG']['password']),
        'OEREB_PG_HOST': str(config['OEREB_VEK2_PG']['host']),
        'OEREB_PG_PORT': str(config['OEREB_VEK2_PG']['port']),
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
