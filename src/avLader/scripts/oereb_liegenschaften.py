# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib
import os

def get_avdate(sysdate_string, connection):
    # to_char muss nach NVARCHAR" gecastet werden, da cx_Oracle char nach str mappt,
    # erst NVARCHAR2 mappt nach unicode.
    avdate_sql = "SELECT CAST (to_char(" + sysdate_string + ",'YYYYMMDD') AS nvarchar2(8)) FROM dual"
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
        'TEAM_CONNECTIONFILE': config['NORM_TEAM']['connection_file'],
        'TEAM_DATABASE': config['NORM_TEAM']['database'],
        'TEAM_USERNAME': config['NORM_TEAM']['username'],
        'TEAM_PASSWORD': config['NORM_TEAM']['password'],
        'VEK2_CONNECTIONFILE': config['GEODB_VEK2']['connection_file'],
        'GEODB_PG_DATABASE': config['GEODB_VEK2_PG']['database'],
        'GEODB_PG_USERNAME': config['GEODB_VEK2_PG']['username'],
        'GEODB_PG_PASSWORD': config['GEODB_VEK2_PG']['password'],
        'GEODB_PG_HOST': config['GEODB_VEK2_PG']['host'],
        'GEODB_PG_PORT': unicode(config['GEODB_VEK2_PG']['port']),
        'OEREB_PG_DATABASE': config['OEREB_VEK2_PG']['database'],
        'OEREB_PG_USERNAME': config['OEREB_VEK2_PG']['username'],
        'OEREB_PG_PASSWORD': config['OEREB_VEK2_PG']['password'],
        'OEREB_PG_HOST': config['OEREB_VEK2_PG']['host'],
        'OEREB_PG_PORT': unicode(config['OEREB_VEK2_PG']['port']),
        'WHERE_CLAUSE': config['OEREB']['dipanu_where_clause'],
        'AV_DATE': get_avdate(config['NACHFUEHRUNG']['mopube'], config['NORM_TEAM']['connection'])
    }

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile)

    fme_runner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()    
    if fme_runner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
   
    avLader.helpers.helper.delete_connection_files(config, logger)
