# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.fme
import os

def run():
    subcommand = 'oereb_adressen'
    config = avLader.helpers.helper.get_config(subcommand)
    logger = config['LOGGING']['logger']
    logger.info("%s wird ausgeführt." % (subcommand))

    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_script_logfile = os.path.join(config['LOGGING']['log_directory'], subcommand + "_fme.log")

    parameters = {
        'TEAM_CONNECTIONFILE': config['NORM_TEAM']['connection_file'],
        'VEK2_CONNECTIONFILE': config['GEODB_VEK2']['connection_file'],
        'OEREB_PG_DATABASE': config['OEREB_VEK2_PG']['database'],
        'OEREB_PG_USERNAME': config['OEREB_VEK2_PG']['username'],
        'OEREB_PG_PASSWORD': config['OEREB_VEK2_PG']['password'],
        'OEREB_PG_HOST': config['OEREB_VEK2_PG']['host'],
        'OEREB_PG_PORT': unicode(config['OEREB_VEK2_PG']['port'])
    }

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile)

    fme_runner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()    
    
    avLader.helpers.helper.delete_connection_files(config, logger)
