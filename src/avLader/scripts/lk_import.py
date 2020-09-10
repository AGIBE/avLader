# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import avLader.scripts.lk_import_qa
import AGILib.fme
import AGILib.downloader
import os
import sys
import zipfile 

def unzip_zip(zip_file, config, logger):
    logger.info("Entpacke Zip-File.")
    with zipfile.ZipFile(zip_file) as avzip:
        avzip.extractall(config['LK_PARAMETER']['lk_gpkg'])

def run():
    subcommand = 'lk_import'
    config = avLader.helpers.helper.get_config(subcommand)
    logger = config['LOGGING']['logger']
    logger.info("%s wird ausgeführt." % (subcommand))
    
    # Download des GPKG
    logger.info("GPKG-Download für LK wird ausgeführt.")
    ftp = AGILib.downloader.FTPDownloader(dest_dir=config['LK_PARAMETER']['lk_gpkg'], ftp_host=config['LK_FTP']['host'], ftp_username=config['LK_FTP']['username'], ftp_password=config['LK_FTP']['password'], ftp_directory=config['LK_FTP']['directory'], ftp_filenames=config['LK_FTP']['lk_filename'])
    ftp.download()
    unzip_zip(os.path.join(config['LK_PARAMETER']['lk_gpkg'], config['LK_FTP']['lk_filename']), config, logger)
    
    # FME-Skripte
    # FME 1: LKMETA_gpkg2Norm: Schreibt die LKMETA-Daten vom Geopackage aufs NORM
    fme_script = os.path.splitext(__file__)[0] + "_1.fmw"
    fme_script_logfile = os.path.join(config['LOGGING']['log_directory'], subcommand + "_1_fme.log")

    parameters = {
        'SourceDataset_XLSXR_5': config['LK_PARAMETER']['lk_meta_wt'],
        'SourceDataset_XLSXR_4': config['LK_PARAMETER']['lk_etapp'],
        'LKBE_gpkg': os.path.join(config['LK_PARAMETER']['lk_gpkg'], config['LK_PARAMETER']['lk_gpkg_file']),
        'DestDataset_GEODATABASE_FILE': config['LK_PARAMETER']['lk_gdb_stand'],
        'DestDataset_XLSXW': config['LK_PARAMETER']['lk_xlsx_stand'],
        'SourceDataset_XLSXR': config['LK_PARAMETER']['lk_xlsx_stand'],
        'VEK1_CONNECTIONFILE': config['GEO_VEK1']['connection_file'],
        'POSTGIS_DB': config['NORM_TEAM_PG']['database'],
        'POSTGIS_HOST': config['NORM_TEAM_PG']['host'],
        'POSTGIS_PASSWORD': config['NORM_TEAM_PG']['password'],
        'POSTGIS_PORT': unicode(config['NORM_TEAM_PG']['port']),
        'POSTGIS_USER': config['NORM_TEAM_PG']['username'],
        'NORM_CONNECTIONFILE': config['NORM_TEAM']['connection_file']
    }

    logger.info("Script " +  fme_script + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile)
    
    fme_runner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()    

    # FME 2: LKMAP_geopackage_view2fNorm: Schreibt die LKMAP-Daten vom Geopackage aufs NORM
    fme_script2 = os.path.splitext(__file__)[0] + "_2.fmw"
    fme_script_logfile2 = os.path.join(config['LOGGING']['log_directory'], subcommand + "_2_fme.log")

    parameters2 = {
        'SourceDataset_XLSXR': config['LK_PARAMETER']['lk_map_wt'],
        'LKBE_gpkg': os.path.join(config['LK_PARAMETER']['lk_gpkg'], config['LK_PARAMETER']['lk_gpkg_file']),
        'POSTGIS_DB': config['NORM_TEAM_PG']['database'],
        'POSTGIS_HOST': config['NORM_TEAM_PG']['host'],
        'POSTGIS_PORT': unicode(config['NORM_TEAM_PG']['port']),
        'POSTGIS_USER': config['NORM_TEAM_PG']['username'],
        'POSTGIS_PASSWORD': config['NORM_TEAM_PG']['password'],
        'NORM_CONNECTIONFILE': config['NORM_TEAM']['connection_file']
    }

    logger.info("Script " +  fme_script2 + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile2)
    
    fme_runner = AGILib.FMERunner(fme_workbench=fme_script2, fme_workbench_parameters=parameters2, fme_logfile=fme_script_logfile2, fme_logfile_archive=True)
    fme_runner.run()    

    # Check ausführen
    gp = 'LKMETA'
    avLader.scripts.lk_import_qa.check_count_features(config, logger, gp, quelle_pg = False,  gemeinde = False)
    gp = 'LKMAP'
    avLader.scripts.lk_import_qa.check_count_features(config, logger, gp, quelle_pg = True, gemeinde = True)
    
    avLader.helpers.helper.delete_connection_files(config, logger)