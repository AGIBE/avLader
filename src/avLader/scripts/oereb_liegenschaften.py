# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.connection
import os

def get_avdate(sysdate_string, connection):

    avdate_sql = "select to_char(" + sysdate_string + ", 'YYYYMMDD') from dual"
    avdate_result = connection.db_read(avdate_sql)

    return avdate_result[0][0]

def run():
    subcommand = 'oereb_liegenschaften'
    config = avLader.helpers.helper.get_config(subcommand)
    logger = config['LOGGING']['logger']
    logger.info("%s wird ausgeführt." % (subcommand))

    fme_script = os.path.splitext(__file__)[0] + ".fmw"
    fme_script_logfile = os.path.join(config['LOGGING']['log_directory'], subcommand + "_fme.log")

    parameters = {
        'TEAM_CONNECTIONFILE': str(config['NORM_TEAM']['connection_file']),
        'TEAM_DATABASE': str(config['NORM_TEAM']['database']),
        'TEAM_USERNAME': str(config['NORM_TEAM']['username']),
        'TEAM_PASSWORD': str(config['NORM_TEAM']['password']),
        'VEK2_CONNECTIONFILE': str(config['GEODB_VEK2']['connection_file']),
        'GEODB_PG_DATABASE': str(config['GEODB_VEK2_PG']['database']),
        'GEODB_PG_USERNAME': str(config['GEODB_VEK2_PG']['username']),
        'GEODB_PG_PASSWORD': str(config['GEODB_VEK2_PG']['password']),
        'GEODB_PG_HOST': str(config['GEODB_VEK2_PG']['host']),
        'GEODB_PG_PORT': str(config['GEODB_VEK2_PG']['port']),
        'OEREB_PG_DATABASE': str(config['OEREB_VEK2_PG']['database']),
        'OEREB_PG_USERNAME': str(config['OEREB_VEK2_PG']['username']),
        'OEREB_PG_PASSWORD': str(config['OEREB_VEK2_PG']['password']),
        'OEREB_PG_HOST': str(config['OEREB_VEK2_PG']['host']),
        'OEREB_PG_PORT': str(config['OEREB_VEK2_PG']['port']),
        'WHERE_CLAUSE': str(config['OEREB']['dipanu_where_clause']),
        'AV_DATE': get_avdate(config['NACHFUEHRUNG']['mopube'], config['NORM_TEAM']['connection'])
    }

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile)

    fme_runner = AGILib.fme.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()    
    
    avLader.helpers.helper.delete_connection_files(config, logger)
