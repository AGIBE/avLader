# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.qacheck_helper
import os
import sys
import ftplib
import zipfile
import fmeobjects

def download_files(source_dir, target_dir, config, logger, file_to_download):
    
    logger.info("Download-Verzeichnis: "+ target_dir)

    ftp_host = config['LK_FTP']['host']
    ftp_username = config['LK_FTP']['username']
    ftp_password = config['LK_FTP']['password']

    logger.info("Verbinde mit dem FTP-Server.")
    ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    logger.info("Wechsle ins FTP-Verzeichnis " + source_dir)
    ftp.cwd(source_dir)
    logger.info("Hole Liste aller Files.")
    ftp_files = ftp.nlst()
    
    if len(ftp_files) > 0:
        if os.path.exists(target_dir):
            logger.info("Leere Download-Verzeichnis.")
            clean_download_dir(target_dir, logger)
        else:
            logger.info("Download-Verzeichnis existiert nicht. Es wird erstellt.")
            os.makedirs(target_dir)
        
        logger.info("Lade Files herunter." + file_to_download)

        if file_to_download in ftp_files:
            downloaded_file = os.path.join(target_dir, file_to_download) 
            ftp.retrbinary('RETR ' + file_to_download, open(downloaded_file,'wb').write)
        else:
            logger.warning("Datei nicht gefunden. Download nicht möglich.")

    else:
        ftp.quit()
        logger.error("Die Liste der herunterzuladenden Dateien konnte nicht erstellt werden.")
        sys.exit()

def clean_download_dir(download_dir, logger):
    filelist = os.listdir(download_dir)
    for file_to_delete in filelist:
        file_to_delete_path = os.path.join(download_dir, file_to_delete) 
        if os.path.isfile(file_to_delete_path):
            logger.info("Lösche " + file_to_delete_path)
            os.remove(file_to_delete_path)

def unzip_zip(zip_file, config, logger):
    logger.info("Entpacke Zip-File.")
    with zipfile.ZipFile(zip_file) as avzip:
        avzip.extractall(config['LK_PARAMETER']['lk_gpkg'])

def run():
    config = avLader.helpers.config_helper.get_config('lk_import')
    logger = config['LOGGING']['logger']
    logger.info("LK-Import wird ausgeführt.")
    
    # Download vom FTP-Server funktioniert nur via Proxy
    if config['LK_FTP']['use_proxy'] == "1":
        logger.info("FTP-Proxy wird gesetzt!")
        avLader.helpers.ftp_proxy.setup_http_proxy(config['PROXY']['host'], int(config['PROXY']['port']))
    
    # Download des GPKG
    logger.info("GPKG-Download für LK wird ausgeführt.")
    download_files(config['LK_FTP']['directory'], config['LK_PARAMETER']['lk_gpkg'], config, logger, config['LK_FTP']['lk_filename'])
    unzip_zip(os.path.join(config['LK_PARAMETER']['lk_gpkg'], config['LK_FTP']['lk_filename']), config, logger)
    
    # FME-Skripte
    # FME 1: LKMETA_gpkg2Norm: Schreibt die LKMETA-Daten vom Geopackage aufs NORM
    fme_script = os.path.splitext(__file__)[0] + "_1.fmw"
    fme_logfile = avLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory'])
    
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'SourceDataset_XLSXR_5': str(config['LK_PARAMETER']['lk_meta_wt']), 
        'DestDataset_ESRISHAPE': str(config['LK_PARAMETER']['lk_stand']), 
        'SourceDataset_XLSXR_4': str(config['LK_PARAMETER']['lk_etapp']),
        'POSTGIS_DB': str(config['NORM_TEAM_PG']['database']),
        'POSTGIS_HOST': str(config['NORM_TEAM_PG']['host']),
        'POSTGIS_PORT': str(config['NORM_TEAM_PG']['port']),
        'POSTGIS_USER': str(config['NORM_TEAM_PG']['username']),
        'POSTGIS_PASSWORD': str(config['NORM_TEAM_PG']['password']),
        'LKBE_gpkg': str(os.path.join(config['LK_PARAMETER']['lk_gpkg'], config['LK_PARAMETER']['lk_gpkg_file'])),
        'NORM_CONNECTIONFILE': str(config['NORM_TEAM']['connection_file']),
        'VEK1_CONNECTIONFILE': str(config['GEO_VEK1']['connection_file']),
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

    # FME 2: LKMAP_geopackage_view2fNorm: Schreibt die LKMAP-Daten vom Geopackage aufs NORM
    fme_script = os.path.splitext(__file__)[0] + "_2.fmw"
    fme_logfile = avLader.helpers.fme_helper.prepare_fme_log(fme_script, config['LOGGING']['log_directory'])
    
    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_logfile)
    
    runner = fmeobjects.FMEWorkspaceRunner()
    # Der FMEWorkspaceRunner akzeptiert keine Unicode-Strings!
    # Daher müssen workspace und parameters umgewandelt werden!
    parameters = {
        'SourceDataset_XLSXR': str(config['LK_PARAMETER']['lk_map_wt']),
        'LKBE_gpkg': str(os.path.join(config['LK_PARAMETER']['lk_gpkg'], config['LK_PARAMETER']['lk_gpkg_file'])),
        'LOGFILE': str(fme_logfile),
        'POSTGIS_DB': str(config['NORM_TEAM_PG']['database']),
        'POSTGIS_HOST': str(config['NORM_TEAM_PG']['host']),
        'POSTGIS_PORT': str(config['NORM_TEAM_PG']['port']),
        'POSTGIS_USER': str(config['NORM_TEAM_PG']['username']),
        'POSTGIS_PASSWORD': str(config['NORM_TEAM_PG']['password']),
        'NORM_CONNECTIONFILE': str(config['NORM_TEAM']['connection_file'])
    }
    try:
        runner.runWithParameters(str(fme_script), parameters)
        pass
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        logger.error("Import wird abgebrochen!")
        sys.exit()
    
    
    # Check ausführen
    gp = 'LKMETA'
    avLader.helpers.qacheck_helper.check_count_features(config, logger, gp, quelle_pg = False,  gemeinde = True)
    gp = 'LKMAP'
    avLader.helpers.qacheck_helper.check_count_features(config, logger, gp, quelle_pg = True, gemeinde = True)
    
    avLader.helpers.connection_helper.delete_connection_files(config, logger)