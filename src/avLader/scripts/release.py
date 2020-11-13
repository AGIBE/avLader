# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.connection
import sys

def get_objectid(config):
    sequence_sql = "select GDBBE_SEQ.NEXTVAL as OBJECTID FROM dual"
    objectid_res = config['GEODB_DD_TEAM']['connection'].db_read(sequence_sql)
    objectid = objectid_res[0][0]
    return unicode(objectid)
    
def release(gprcode):
    config = avLader.helpers.helper.get_config(gprcode.lower() + '_release')
    logger = config['LOGGING']['logger']
    logger.info(gprcode + "-Release wird ausgeführt.")
    
    task_objectid = get_objectid(config)
    flag_objectid = get_objectid(config)
    logger.info("TASK_OBJECTID geholt: " + task_objectid)
    logger.info("FLAG_OBJECTID geholt: " + flag_objectid)
    
    gzs_objectid_sql = "select GZS_OBJECTID from VW_GEOPRODUKT_ZEITSTAND where GPR_BEZEICHNUNG='" + gprcode + "' and GZS_AKTUELL=1"
    gzs_objectid_res = config['GEODB_DD_TEAM']['connection'].db_read(gzs_objectid_sql)
    if len(gzs_objectid_res) != 1:
        logger.error("Für das Geoprodukt " + gprcode + " konnte im DD kein aktueller Zeitstand gefunden werden.")
        logger.error("Die Freigabe kann nicht erteilt werden.")
        avLader.helpers.helper.delete_connection_files(config, logger)
        sys.exit()
    else:
        gzs_objectid = unicode(gzs_objectid_res[0][0])
        logger.info("GZS_OBJECTID geholt: " + gzs_objectid)
        check_sql ="SELECT TASK_OBJECTID FROM TB_TASK WHERE GZS_OBJECTID=%s AND TASK_STATUS=2" % (gzs_objectid)
        check_result = config['GEODB_DD_TEAM']['connection'].db_read(check_sql)
        sysdate = config['NACHFUEHRUNG'][gprcode.lower()]
        usecase = unicode(config['ILADER_USESCASES'][gprcode.lower()])
        if len(check_result) == 0:
            task_sql = "INSERT INTO tb_task (TASK_OBJECTID, GZS_OBJECTID, UC_OBJECTID, TASK_STATUS, FLAG_OBJECTID) VALUES (%s, %s, %s, 2, %s)" % (task_objectid, gzs_objectid, usecase, flag_objectid)
            logger.info("TB_TASK wird aktualisiert:")
            logger.info(task_sql)
            flag_sql = "INSERT INTO tb_flag_agi (FLAG_OBJECTID, GPR_BEZEICHNUNG, FLAG_DATUM, TASK_OBJECTID) VALUES (%s, '%s', %s, %s)" % (flag_objectid, gprcode, sysdate, task_objectid)
            logger.info("TB_FLAG_AGI wird aktualisiert:")
            logger.info(flag_sql)
            try:
                config['GEODB_DD_TEAM']['connection'].db_write(task_sql)
                config['GEODB_DD_TEAM']['connection'].db_write(flag_sql)
            except Exception as ex:
                logger.error("Fehler beim Schreiben von TB_TASK/TB_FLAG_AGI.")
                logger.error("Die Freigabe kann nicht erteilt werden.")
                logger.error(unicode(ex))
                avLader.helpers.helper.delete_connection_files(config, logger)
                sys.exit()
        else:
            logger.error("Es gibt bereits einen Task für diese GZS_OBJECTID mit Status=2.")
            logger.error("Die Freigabe kann nicht erteilt werden.")
            avLader.helpers.helper.delete_connection_files(config, logger)
            sys.exit()
            
    logger.info("Die iLader-Importnummer lautet: " + task_objectid)
    logger.info("Der iLader kann gestartet werden mit: iLader run " + task_objectid)
    avLader.helpers.helper.delete_connection_files(config, logger)    