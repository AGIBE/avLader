# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.ftp_helper
import avLader.helpers.index_helper
import os
import arcpy
import sys

def run():
    config = avLader.helpers.config_helper.get_config('fds_import')
    logger = config['LOGGING']['logger']
    logger.info("FDS-Import wird ausgeführt.")
    
    fds_objects = [
    'BB_BBNachfuehrung',
    'BB_BoFlaeche',
    'BB_BoFlaecheSymbol',
    'BB_BoFlaecheSymbolUP2',
    'BB_BoFlaecheSymbolUP5',
    'BB_Einzelpunkt',
    'BB_EinzelpunktPos',
    'BB_Gebaeudenummer',
    'BB_GebaeudenummerPos',
    'BB_Objektname',
    'BB_ObjektnamePos',
    'BB_ObjektnamePosUP2',
    'BB_ObjektnamePosUP5',
    'BB_ProjBoFlaeche',
    'BB_ProjBoFlaecheSymbol',
    'BB_ProjGebaeudenummer',
    'BB_ProjGebaeudenummerPos',
    'BB_ProjObjektname',
    'BB_ProjObjektnamePos',
    'BB_ProjObjektnamePosUP2',
    'BB_ProjObjektnamePosUP5',
    'BG_Bezirksgrenzabschnitt',
    'EO_EONachfuehrung',
    'EO_Einzelobjekt',
    'EO_Einzelpunkt',
    'EO_EinzelpunktPos',
    'EO_Flaechenelement',
    'EO_FlaechenelementSymbol',
    'EO_FlaechenelementSymbolUP2',
    'EO_FlaechenelementSymbolUP5',
    'EO_Linienelement',
    'EO_LinienelementSymbol',
    'EO_LinienelementSymbolUP2',
    'EO_LinienelementSymbolUP5',
    'EO_Objektname',
    'EO_ObjektnamePos',
    'EO_ObjektnamePosUP2',
    'EO_ObjektnamePosUP5',
    'EO_Objektnummer',
    'EO_ObjektnummerPos',
    'EO_Punktelement',
    'FP1_HFP1',
    'FP1_HFP1Nachfuehrung',
    'FP1_HFP1Pos',
    'FP1_LFP1',
    'FP1_LFP1Nachfuehrung',
    'FP1_LFP1Pos',
    'FP1_LFP1Symbol',
    'FP2_HFP2',
    'FP2_HFP2Nachfuehrung',
    'FP2_HFP2Pos',
    'FP2_LFP2',
    'FP2_LFP2Nachfuehrung',
    'FP2_LFP2Pos',
    'FP2_LFP2Symbol',
    'FP3_HFP3',
    'FP3_HFP3Nachfuehrung',
    'FP3_HFP3Pos',
    'FP3_Hilfsfixpunkt',
    'FP3_HilfsfixpunktPos',
    'FP3_HilfsfixpunktSymbol',
    'FP3_LFP3',
    'FP3_LFP3Nachfuehrung',
    'FP3_LFP3Pos',
    'FP3_LFP3Symbol',
    'GA_BenanntesGebiet',
    'GA_GEBNachfuehrung',
    'GA_GebaeudeBeschreibung',
    'GA_GebaeudeName',
    'GA_GebaeudeNamePos',
    'GA_GebaeudeNamePosUP2',
    'GA_GebaeudeNamePosUP5',
    'GA_Gebaeudeeingang',
    'GA_HausnummerPos',
    'GA_HausnummerPosUP2',
    'GA_HausnummerPosUP5',
    'GA_Lokalisation',
    'GA_LokalisationsName',
    'GA_LokalisationsNamePos',
    'GA_LokalisationsNamePosUP2',
    'GA_LokalisationsNamePosUP5',
    'GA_Strassenstueck',
    'GG_GEMNachfuehrung',
    'GG_Gemeinde',
    'GG_Gemeindegrenze',
    'GG_Hoheitsgrenzpunkt',
    'GG_HoheitsgrenzpunktPos',
    'GG_HoheitsgrenzpunktSymbol',
    'GG_ProjGemeindegrenze',
    'HK_HKNachfuehrung',
    'HK_Hoehenkurve',
    'HK_HoehenkurvePos',
    'HK_HoehenkurvePosUP2',
    'HK_HoehenkurvePosUP5',
    'HO_Aussparung',
    'HO_Gelaendekante',
    'HO_HONachfuehrung',
    'HO_Hoehenpunkt',
    'HO_HoehenpunktPos',
    'HO_HoehenpunktPosUP2',
    'HO_HoehenpunktPosUP5',
    'KG_Kantonsgrenzabschnitt',
    'LG_Landesgrenzabschnitt',
    'LI_Bergwerk',
    'LI_Grenzpunkt',
    'LI_GrenzpunktPos',
    'LI_GrenzpunktSymbol',
    'LI_Grundstueck',
    'LI_GrundstueckPos',
    'LI_GrundstueckPosUP2',
    'LI_GrundstueckPosUP5',
    'LI_LSNachfuehrung',
    'LI_Liegenschaft',
    'LI_ProjBergwerk',
    'LI_ProjGrundstueck',
    'LI_ProjGrundstueckPos',
    'LI_ProjGrundstueckPosUP2',
    'LI_ProjGrundstueckPosUP5',
    'LI_ProjLiegenschaft',
    'LI_ProjSelbstRecht',
    'LI_SelbstRecht',
    'LI_TeilLSPos',
    'LI_TeilLSPosUP2',
    'LI_TeilLSPosUP5',
    'LI_TeilProjLSPos',
    'LI_TeilProjLSPosUP2',
    'LI_TeilProjLSPosUP5',
    'LI_TeilProjSRPos',
    'LI_TeilProjSRPosUP2',
    'LI_TeilProjSRPosUP5',
    'LI_TeilSRPos',
    'LI_TeilSRPosUP2',
    'LI_TeilSRPosUP5',
    'NB_NBGeometrie',
    'NB_Nummerierungsbereich',
    'NB_NummerierungsbereichPos',
    'NO_Flurname',
    'NO_FlurnamePos',
    'NO_FlurnamePosUP2',
    'NO_FlurnamePosUP5',
    'NO_Gelaendename',
    'NO_GelaendenamePos',
    'NO_GelaendenamePosUP2',
    'NO_GelaendenamePosUP5',
    'NO_NKNachfuehrung',
    'NO_Ortsname',
    'NO_OrtsnamePos',
    'NO_OrtsnamePosUP2',
    'NO_OrtsnamePosUP5',
    'OR_OSNachfuehrung',
    'OR_Ortschaft',
    'OR_OrtschaftsName',
    'OR_OrtschaftsName_Pos',
    'OR_OrtschaftsName_PosUP2',
    'OR_OrtschaftsName_PosUP5',
    'OR_OrtschaftsVerbund',
    'OR_OrtschaftsVerbundText',
    'OR_PLZ6',
    'OR_PLZ6Nachfuehrung',
    'PE_Plan',
    'PE_PlanPos',
    'PE_Plangeometrie',
    'PR_Darstellungsflaeche',
    'PR_Darstellungsflaeche_Geometr',
    'PR_KoordinatenLinie',
    'PR_Koordinatenanschrift',
    'PR_KoordinatenanschriftPos',
    'PR_Linienobjekt',
    'PR_Netzkreuz',
    'PR_PlanLayout',
    'PR_PlanLayoutSymbol',
    'PR_Planbeschriftung',
    'PR_PlanbeschriftungPos',
    'RL_Einzelpunkt',
    'RL_EinzelpunktPos',
    'RL_Flaechenelement',
    'RL_Leitungsobjekt',
    'RL_LeitungsobjektPos',
    'RL_LeitungsobjektPosUP2',
    'RL_LeitungsobjektPosUP5',
    'RL_Linienelement',
    'RL_Punktelement',
    'RL_RLNachfuehrung',
    'RL_Signalpunkt',
    'RL_SignalpunktPos',
    'Ru_Rutschung',
    'Ru_RutschungPos',
    'TS_Toleranzstufe',
    'TS_ToleranzstufePos'
    ]
    
    # Download vom FTP-Server funktioniert nur via Proxy
    if config['ZAV_FTP']['use_proxy'] == "1":
        logger.info("FTP-Proxy wird gesetzt!")
        avLader.helpers.ftp_proxy.setup_http_proxy(config['PROXY']['host'], int(config['PROXY']['port']))
    
    source_fgdb = avLader.helpers.ftp_helper.download_fgdb(config['ZAV_FTP']['fds_filename'], config, logger)
    target_sde = config['AV01_WORK']['connection_file']
    
    for fds_object in fds_objects:
        logger.info("Importiere " + fds_object)
        source_object = os.path.join(source_fgdb, fds_object)
        target_object = os.path.join(target_sde, config['AV01_WORK']['username'] + "." + fds_object)
 
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
                        grid_size = avLader.helpers.index_helper.calculate_grid_size(source_object)
                        logger.info("Grid Size ist: " + str(grid_size))
                        if grid_size > 0:
                            arcpy.AddSpatialIndex_management(target_object, grid_size)
                        else:
                            arcpy.AddSpatialIndex_management(target_object)
                        logger.info("Spatial Index erfolgreich erstellt.")
                    else:
                        logger.warn("Spatial Index konnte wegen eines Locks nicht erstellt werden.")
                 
                logger.info("Zähle Records in der Quelle und im Ziel.")
                source_count = int(arcpy.GetCount_management(source_object)[0])
                logger.info("Anzahl Records in der Quelle: " + str(source_count))
                target_count = int(arcpy.GetCount_management(target_object)[0])
                logger.info("Anzahl Records im Ziel: " + str(target_count))
                  
                if source_count==target_count:
                    logger.info("Anzahl Records identisch")
                else:
                    logger.error("Anzahl Records nicht identisch. Ebene " + fds_object)
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