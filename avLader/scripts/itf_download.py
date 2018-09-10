# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.ftp_proxy
import ftplib
import os
import sys

ftp_files = []

def process_ftp_listing(ftp_line):
    ftp_files.append(ftp_line)

def download_files(config, logger):
    ftp_host = config['ZAV_FTP']['host']
    ftp_username = config['ZAV_FTP']['username']
    ftp_password = config['ZAV_FTP']['password']
    ftp_directory = config['ZAV_FTP']['itf_directory']
    download_dir = config['DIRECTORIES']['itfs']
    
    logger.info("Verbinde mit dem FTP-Server.")
    ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    logger.info("Wechsle ins Verzeichnis " + ftp_directory)
    ftp.cwd(ftp_directory)
    logger.info("Hole Liste aller Files.")
    ftp.retrlines('NLST', process_ftp_listing)
    
    if len(ftp_files) > 0:
        logger.info("Leere Download-Verzeichnis.")
        filelist = os.listdir(download_dir)
        for file_to_delete in filelist:
            file_to_delete_path = os.path.join(download_dir, file_to_delete) 
            if os.path.isfile(file_to_delete_path):
                logger.info("Lösche " + file_to_delete_path)
                os.remove(file_to_delete_path)
        
        logger.info("Lade Files herunter...")
        for itf_file in ftp_files:
            logger.info(itf_file)
            downloaded_file = os.path.join(download_dir, itf_file) 
            ftp.retrbinary('RETR ' + itf_file, open(downloaded_file,'wb').write)
        ftp.quit()
    else:
        ftp.quit()
        logger.error("Die Liste der herunterzuladenden ITF-Dateien konnte nicht erstellt werden.")
        sys.exit()
   
def download_files_avch(config, logger):
    ftp_host = config['ZAV_FTP']['host']
    ftp_username = config['ZAV_FTP']['username']
    ftp_password = config['ZAV_FTP']['password']
    ftp_directory = config['ZAV_FTP']['itf_ch_directory']
    download_dir = config['DIRECTORIES']['itfs_ch']
    
    logger.info("Verbinde mit dem FTP-Server.")
    ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    logger.info("Wechsle ins Verzeichnis " + ftp_directory)
    ftp.cwd(ftp_directory)
    logger.info("Hole Liste aller Files.")
    ftp.retrlines('NLST', process_ftp_listing)
    
    if len(ftp_files) > 0:
        logger.info("Leere Download-Verzeichnis.")
        filelist = os.listdir(download_dir)
        for file_to_delete in filelist:
            file_to_delete_path = os.path.join(download_dir, file_to_delete) 
            if os.path.isfile(file_to_delete_path):
                logger.info("Lösche " + file_to_delete_path)
                os.remove(file_to_delete_path)
        
        logger.info("Lade Files herunter...")
        for itf_file in ftp_files:
            logger.info(itf_file)
            downloaded_file = os.path.join(download_dir, itf_file) 
            ftp.retrbinary('RETR ' + itf_file, open(downloaded_file,'wb').write)
        ftp.quit()
    else:
        ftp.quit()
        logger.error("Die Liste der herunterzuladenden ITF-Dateien konnte nicht erstellt werden.")
        sys.exit() 

def run():
    config = avLader.helpers.config_helper.get_config('itf_download')
    
    logger = config['LOGGING']['logger']
    logger.info("ITF-Download (Original ITFs) wird ausgeführt.")

    # Download vom FTP-Server funktioniert nur via Proxy
    if config['ZAV_FTP']['use_proxy'] == "1":
        logger.info("FTP-Proxy wird gesetzt!")
        avLader.helpers.ftp_proxy.setup_http_proxy(config['PROXY']['host'], int(config['PROXY']['port']))
        
    download_files(config, logger)
    logger.info("ITF-Download (AVCH) wird ausgeführt.")
    global ftp_files
    ftp_files = []
    download_files_avch(config, logger)
    
    avLader.helpers.connection_helper.delete_connection_files(config, logger)