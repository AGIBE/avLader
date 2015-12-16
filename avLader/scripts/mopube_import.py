# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.ftp_helper
import os
import arcpy
import sys

def run():
    config = avLader.helpers.config_helper.get_config('mopube_import')
    logger = config['LOGGING']['logger']
    logger.info("MOPUBE-Import wird ausgeführt.")
    
    mopube_objects = [
        'MOPUBE_BBARTT',
        'MOPUBE_BBF',
        'MOPUBE_BBPRJF',
        'MOPUBE_BBPRJTXT',
        'MOPUBE_BBTXT',
        'MOPUBE_EOARTT',
        'MOPUBE_EOF',
        'MOPUBE_EOFTXT',
        'MOPUBE_EOL',
        'MOPUBE_EOLTXT',
        'MOPUBE_EOP',
        'MOPUBE_EOPTXT',
        'MOPUBE_FIXP',
        'MOPUBE_FPKATT',
        'MOPUBE_GAEINP',
        'MOPUBE_GAEINTXT',
        'MOPUBE_GASTRNA',
        'MOPUBE_GASTRNAT',
        'MOPUBE_GUELTIGT',
        'MOPUBE_HGABSCHL',
        'MOPUBE_HGARTT',
        'MOPUBE_HGF',
        'MOPUBE_HGL',
        'MOPUBE_HGP',
        'MOPUBE_HGPRJF',
        'MOPUBE_HGTYPT',
        'MOPUBE_HOAUSPAT',
        'MOPUBE_HOAUSSPA',
        'MOPUBE_HOEHEP',
        'MOPUBE_HOGELKAN',
        'MOPUBE_HOGELKAT',
        'MOPUBE_HOHK',
        'MOPUBE_LAGEZUVT',
        'MOPUBE_LIARTT',
        'MOPUBE_LIF',
        'MOPUBE_LIGP',
        'MOPUBE_LIL',
        'MOPUBE_LILARTT',
        'MOPUBE_LIPRJF',
        'MOPUBE_LIPRJTXT',
        'MOPUBE_LISRF',
        'MOPUBE_LISRL',
        'MOPUBE_LISRPRJF',
        'MOPUBE_LISRPRJT',
        'MOPUBE_LISRTXT',
        'MOPUBE_LITXT',
        'MOPUBE_LIVOLLT',
        'MOPUBE_NOKATT',
        'MOPUBE_NONAMF',
        'MOPUBE_NONAMTXT',
        'MOPUBE_NUMNAMET',
        'MOPUBE_OFFBEZT',
        'MOPUBE_PKTZT',
        'MOPUBE_QUALIT',
        'MOPUBE_RLF',
        'MOPUBE_RLFTXT',
        'MOPUBE_RLL',
        'MOPUBE_RLLTXT',
        'MOPUBE_RLMEDIT',
        'MOPUBE_RLP',
    ]
    
    source_fgdb = avLader.helpers.ftp_helper.download_fgdb(config['ZAV_FTP']['mopube_filename'], config, logger)
    target_sde = config['NORM_TEAM']['connection_file']
    
    for mopube_object in mopube_objects:
        logger.info("Importiere " + mopube_object)
        source_object = os.path.join(source_fgdb, mopube_object)
        target_object = os.path.join(target_sde, config['NORM_TEAM']['username'] + "." + mopube_object)
        
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
                    logger.error("Anzahl Records nicht identisch. Ebene " + mopube_object)
                    logger.error("Import wird abgebrochen.")
                    avLader.helpers.connection_helper.delete_connection_files(config, logger)
                    sys.exit() 
            else:
                logger.error("Ziel-Objekt " + target_object + " existiert nicht.")
                logger.error("Import wird abgebrochen.")
                avLader.helpers.connection_helper.delete_connection_files(config, logger)
                sys.exit()
        else:
            logger.error("Quell-Objekt " + source_object + " existiert nicht.")
            logger.error("Import wird abgebrochen.")
            avLader.helpers.connection_helper.delete_connection_files(config, logger)
            sys.exit()
    
    avLader.helpers.connection_helper.delete_connection_files(config, logger)