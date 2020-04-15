# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.folder_files
import ftplib
import os
import sys
import datetime
import codecs

def download_files(source_dir, target_dir, config, logger, files_to_download=None):
    
    logger.info("Download-Verzeichnis: "+ target_dir)

    ftp_host = config['ZAV_FTP']['host']
    ftp_username = config['ZAV_FTP']['username']
    ftp_password = config['ZAV_FTP']['password']

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
        
        if files_to_download is not None:
            logger.info("Lade nur bestimmte Files herunter.")
            for file_to_download in files_to_download:
                logger.info(file_to_download)
                if file_to_download in ftp_files:
                    downloaded_file = os.path.join(target_dir, file_to_download) 
                    ftp.retrbinary('RETR ' + file_to_download, open(downloaded_file,'wb').write)
                else:
                    logger.warning("Datei nicht gefunden. Download nicht möglich.")
        else:
            logger.info("Keine Liste mit herunterzuladenden Files vorhanden. Lade sämtliche Files im Verzeichnis herunter.")
            for download_file in ftp_files:
                logger.info(download_file)
                downloaded_file = os.path.join(target_dir, download_file) 
                ftp.retrbinary('RETR ' + download_file, open(downloaded_file,'wb').write)
        ftp.quit()
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

def get_mode_from_csv(csv_file):
    file_content = ""
    with codecs.open(csv_file, "r", "utf-8") as inc_file:
        file_content = inc_file.read().strip()
    
    return file_content

def get_itf_files_from_csv(csv_file):
    download_itf_files = []
    download_log_files = []
    with codecs.open(csv_file, "r", "utf-8") as inc_file:
        for line in inc_file.readlines():
            if len(line) > 0:
                itf_file = line.split(";")[0]
                log_file = itf_file.replace(".itf", ".log")
                download_itf_files.append(itf_file)
                download_log_files.append(log_file)

    return (download_itf_files, download_log_files)

def run():
    subcommand = 'itf_download'
    config = avLader.helpers.helper.get_config(subcommand)
    logger = config['LOGGING']['logger']
    logger.info("%s wird ausgeführt." % (subcommand))

    logger.info("Statistik-Download (für AI) wird ausgeführt.")
    statistik_files = config['ZAV_FTP']['statistics_files']
    statistik_dir_ai = os.path.join(config['DIRECTORIES']['itfs_ch'], config['DIRECTORIES']['itfs_ch_subdir_statistik'])
    download_files(config['ZAV_FTP']['statistics_directory'], statistik_dir_ai, config, logger, statistik_files)

    logger.info("Statistik-Download (für DAT) wird ausgeführt.")
    statistik_files = config['ZAV_FTP']['statistics_files']
    statistik_dir_dat = os.path.join(config['DIRECTORIES']['archiv'], datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    download_files(config['ZAV_FTP']['statistics_directory'], statistik_dir_dat, config, logger, statistik_files)

    logger.info("ITF-Download (Modell Bern) wird ausgeführt.")
    download_files(config['ZAV_FTP']['itf_directory'], config['DIRECTORIES']['itfs'], config, logger)

    increment_mode_file = os.path.join(statistik_dir_ai, "zav_integration.csv")
    logger.info("Ermittle Inkrement-Modus aus " + increment_mode_file)
    increment_mode = get_mode_from_csv(increment_mode_file)
    if increment_mode == "full":
        logger.info("Inkrement-Modus ist " + increment_mode)
        logger.info("Es werden sämtliche Files heruntergeladen.")
        logger.info("ITF-Download (AVCH) wird ausgeführt.")
        download_files(config['ZAV_FTP']['itf_ch_directory'], config['DIRECTORIES']['itfs_ch'], config, logger)
        logger.info("Checker-Log-Download wird ausgeführt.")
        checker_logs_dir = os.path.join(config['DIRECTORIES']['itfs_ch'], config['DIRECTORIES']['itfs_ch_subdir_logs'])
        download_files(config['ZAV_FTP']['itf_ch_logs'], checker_logs_dir, config, logger)
    elif increment_mode == "increment":
        logger.info("Inkrement-Modus ist " + increment_mode)
        logger.info("Liste der herunterzuladenden Files wird ausgelesen:")
        increment_file = os.path.join(statistik_dir_ai, "zav_inkrement.csv")
        (itf_files_to_download, log_files_to_download) = get_itf_files_from_csv(increment_file)
        logger.info("ITF-Download (AVCH) wird ausgeführt.")
        download_files(config['ZAV_FTP']['itf_ch_directory'], config['DIRECTORIES']['itfs_ch'], config, logger, itf_files_to_download)
        logger.info("Checker-Log-Download wird ausgeführt.")
        checker_logs_dir = os.path.join(config['DIRECTORIES']['itfs_ch'], config['DIRECTORIES']['itfs_ch_subdir_logs'])
        download_files(config['ZAV_FTP']['itf_ch_logs'], checker_logs_dir, config, logger, log_files_to_download)

    else:
        logger.error("Ungültiger Wert zum Inkrement-Modus in " + increment_mode_file)
        logger.error("Es werden keine AVCH-Files heruntergeladen.")
        sys.exit()

    avLader.helpers.helper.delete_connection_files(config, logger)