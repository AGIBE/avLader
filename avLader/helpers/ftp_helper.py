# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ftplib
import os.path
import shutil
import sys
import zipfile
import datetime
import avLader.helpers.ftp_proxy

def download_statsfile(ftp_filename, config, logger):
    ftp_host = config['ZAV_FTP']['host']
    ftp_username = config['ZAV_FTP']['username']
    ftp_password = config['ZAV_FTP']['password']
    ftp_directory = config['ZAV_FTP']['statistics_directory']
    ftp_file = ftp_filename
    
    downloaded_file = os.path.join(config['DIRECTORIES']['archiv'], os.path.splitext(ftp_filename)[0] + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + os.path.splitext(ftp_filename)[1])
    
    ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    ftp.cwd(ftp_directory)
    try:
        ftp_stat_file = open(downloaded_file,'wb')
        ftp.retrbinary('RETR ' + ftp_file, ftp_stat_file.write)
    except:
        logger.warn("Statistik-File " + str(ftp_file) + " nicht auf FTP-Server vorhanden.")
        ftp_stat_file.close()
        os.remove(downloaded_file)
    ftp.quit()

def download_fgdb(ftp_filename, config, logger):
    ftp_host = config['ZAV_FTP']['host']
    ftp_username = config['ZAV_FTP']['username']
    ftp_password = config['ZAV_FTP']['password']
    ftp_directory = config['ZAV_FTP']['directory']
    ftp_file = ftp_filename
    download_dir = config['DIRECTORIES']['local_data_dir']
    archiv_dir = config['DIRECTORIES']['archiv']
    archiv_filename = os.path.splitext(ftp_file)[0] + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + os.path.splitext(ftp_file)[1] 
    
    downloaded_file = os.path.join(download_dir, ftp_file)
    archived_file = os.path.join(archiv_dir, archiv_filename)
    fgdb = os.path.splitext(downloaded_file)[0]
    
    if os.path.exists(downloaded_file):
        logger.info("Datei " + downloaded_file + " wird gelöscht.")
        os.remove(downloaded_file)
        
    if os.path.exists(fgdb):
        logger.info("Verzeichnis " + fgdb + " wird gelöscht.")
        shutil.rmtree(fgdb)

    logger.info("Folgende Datei wird heruntergeladen: " + ftp_file)
    logger.info("Ziel-Verzeichnis: " + download_dir)
    
    try:
        ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
        ftp.cwd(ftp_directory)
        ftp.retrbinary('RETR ' + ftp_file, open(downloaded_file,'wb').write)
        ftp.quit()
    except ftplib.all_errors as e:
        logger.error(ftp_file + " konnte nicht von FTP-Server heruntergeladen werden: " + str(e))
    
    logger.info(downloaded_file + " wird ins Archiv kopiert.")
    
    shutil.copy2(downloaded_file, archived_file)
    
    unzip_fgdb(downloaded_file, config, logger)
    if os.path.exists(fgdb):
        logger.info("Filegeodatabase: " + fgdb)
    else:
        logger.error("Filegeodatabase " + fgdb + " existiert nicht.")
        logger.error("Export wird abgebrochen.")
        sys.exit()
    
    return fgdb

def unzip_fgdb(zip_file, config, logger):
    logger.info("Entpacke Zip-File.")
    with zipfile.ZipFile(zip_file) as avzip:
        avzip.extractall(config['DIRECTORIES']['local_data_dir'])
