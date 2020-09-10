# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.agilogger
import AGILib.configuration
import AGILib.downloader
import arcpy
import os
import time
import shutil
import datetime
import zipfile
import sys

def download_zav_fgdb(file_to_download, downloaded_zip, source_fgdb, config):
    logger = config['LOGGING']['logger']
    # Wenn das zu herunterladende File schon existiert, wird es gelöscht
    if os.path.exists(downloaded_zip):
        logger.info("Datei %s existiert bereits. Sie wird gelöscht." % (downloaded_zip))
        os.remove(downloaded_zip)

    # Wenn die entpackte FGDB schon existiert, wird sie gelöscht
    if os.path.exists(source_fgdb):
        logger.info("Verzeichnis %s existiert bereits. Es wird gelöscht." % source_fgdb)
        shutil.rmtree(source_fgdb)

    # FTP-Download
    logger.info("ZIP-File %s wird vom FTP-Server %s heruntergeladen..." % (file_to_download, config['ZAV_FTP']['host']))
    ftp = AGILib.downloader.FTPDownloader(ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['directory'], ftp_filenames=file_to_download, dest_dir=config['DIRECTORIES']['local_data_dir'])
    ftp.download()

    # Archiv-Kopie
    archiv_dir = config['DIRECTORIES']['archiv']
    archiv_filename = os.path.splitext(file_to_download)[0] + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + os.path.splitext(file_to_download)[1]
    archived_file = os.path.join(archiv_dir, archiv_filename)
    logger.info("Das ZIP-File wird ins Archiv (%s) kopiert." % (archiv_dir))
    logger.info("Archiv-Filename: %s" % (archiv_filename))
    shutil.copy2(downloaded_zip, archived_file)
    
    # Entpacken
    logger.info("Heruntergeladenes ZIP-File wird entpackt...")
    with zipfile.ZipFile(downloaded_zip) as avzip:
        avzip.extractall(config['DIRECTORIES']['local_data_dir'])

def calculate_grid_size(fc):
    '''
    Berechnet die Grid Size einer Feature Class.
    Der von arcpy berechnete Wert wird dabei auf
    eine ganze Zahl gerundet.
    :param fc: Feature Class, für die die Grid Size gerechnet wird.
    '''
    fc_count = int(arcpy.GetCount_management(fc)[0])
    grid_size = 0
    if fc_count > 0:
        # CalculateDefaultGridIndex_management bricht mit Fehler ab,
        # wenn die Featureclass nur aus Features mit leerer Geometrie
        # besteht. Kann bei den Nachführungstabellen vorkommen.
        try:
            result = arcpy.CalculateDefaultGridIndex_management(fc)
            grid_size = float(result.getOutput(0))
            grid_size = int(round(grid_size))
        except:
            grid_size = 0
    return grid_size

def append(object, source_object, target_object, config):
    logger = config['LOGGING']['logger']

    needs_spatial_index = False
    if arcpy.Describe(target_object).datasetType == "FeatureClass":
        needs_spatial_index = True
        
    if arcpy.Exists(source_object):
        if arcpy.Exists(target_object):
                
            # Räumlichen Index entfernen
            if needs_spatial_index and arcpy.Describe(target_object).hasSpatialIndex:
                logger.info("Spatial Index wird entfernt.")
                if arcpy.TestSchemaLock(target_object):
                    arcpy.RemoveSpatialIndex_management(target_object)
                    logger.info("Spatial Index erfolgreich entfernt.")
                else:
                    logger.warn("Spatial Index konnte wegen eines Locks nicht entfernt werden.")
                
            logger.info("Truncating " + target_object)
            arcpy.TruncateTable_management(target_object)
                
            logger.info("Appending " + source_object)
            arcpy.Append_management(source_object, target_object, "TEST")
                
            # Räumlichen Index erstellen
            if needs_spatial_index:
                logger.info("Spatial Index wird erstellt.")
                if arcpy.TestSchemaLock(target_object):
                    logger.info("Grid Size wird berechnet.")
                    grid_size = calculate_grid_size(source_object)
                    logger.info("Grid Size ist: " + unicode(grid_size))
                    if grid_size > 0:
                        arcpy.AddSpatialIndex_management(target_object, grid_size)
                    else:
                        arcpy.AddSpatialIndex_management(target_object)
                    logger.info("Spatial Index erfolgreich erstellt.")
                else:
                    logger.warn("Spatial Index konnte wegen eines Locks nicht erstellt werden.")
                
            logger.info("Zähle Records in der Quelle und im Ziel.")
            source_count = int(arcpy.GetCount_management(source_object)[0])
            logger.info("Anzahl Records in der Quelle: " + unicode(source_count))
            target_count = int(arcpy.GetCount_management(target_object)[0])
            logger.info("Anzahl Records im Ziel: " + unicode(target_count))
                
            if source_count==target_count:
                logger.info("Anzahl Records identisch")
            else:
                logger.error("Anzahl Records nicht identisch. Ebene " + object)
                logger.error("Import wird abgebrochen.")
                avLader.helpers.helper.delete_connection_files(config, logger)
                sys.exit() 
        else:
            logger.error("Ziel-Objekt " + target_object + " existiert nicht.")
            logger.error("Import wird abgebrochen.")
            avLader.helpers.helper.delete_connection_files(config, logger)
            sys.exit()
    else:
        logger.error("Quell-Objekt " + source_object + " existiert nicht.")
        logger.error("Import wird abgebrochen.")
        avLader.helpers.helper.delete_connection_files(config, logger)
        sys.exit()

def delete_connection_files(config, logger):
    for connObj in config['OraConnectionObjects']:
        connObj.delete_all_sde_connections()

def get_config(subcommand):
    config = AGILib.configuration.Configuration(configfile_envvar="AVIMPORTHOMEPRO").config
    
    logfile_name = subcommand + ".log"
    config['LOGGING']['log_directory'] = os.path.join(config['LOGGING']['basedir'], subcommand)
    logger = AGILib.agilogger.initialize_agilogger(logfile_name=logfile_name, logfile_folder=config['LOGGING']['log_directory'], list_log_handler=['file','stream'], archive=True, logger_name='AGILogger')
    logger.info('Konfiguration wird eingelesen.')
    config['LOGGING']['logger'] = logger

    # Connections erstellen
    config['OraConnectionObjects'] = []
    for ora_connection_key in ["AV01_WORK","NORM_TEAM","GEODB_DD_TEAM","GEODB_VEK2","GEO_VEK1","AV01_WORKH","GPS1_WORKH"]:
        logger.info("Connection-Files werden erstellt.")
        connObj = AGILib.connection.Connection(db=config[ora_connection_key]['database'], username=config[ora_connection_key]['username'], password=config[ora_connection_key]['password'], db_type='oracle')
        config[ora_connection_key]['connection_file'] = connObj.create_sde_connection()
        config['OraConnectionObjects'].append(connObj)
        config[ora_connection_key]['connection'] = connObj

    for pg_connection_key in ["GEODB_VEK2_PG", "OEREB_VEK2_PG", "NORM_TEAM_PG"]:
        connObj = AGILib.connection.Connection(db=config[pg_connection_key]['database'], username=config[pg_connection_key]['username'], password=config[pg_connection_key]['password'], db_type='postgres', host=config[pg_connection_key]['host'], port=config[pg_connection_key]['port'])
        config[pg_connection_key]['connection'] = connObj

    return config 