# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.helper
import AGILib.folder_files
import AGILib.downloader
import os
import sys
import datetime
import codecs

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

    logger.info("Download-Ordner werden geleert:")
    logger.info(config['DIRECTORIES']['itfs_ch'])
    AGILib.folder_files.clean_folder_recursive(config['DIRECTORIES']['itfs_ch'])
    logger.info(config['DIRECTORIES']['itfs'])
    AGILib.folder_files.clean_folder_recursive(config['DIRECTORIES']['itfs'])

    logger.info("Statistik-Download (für AI) wird ausgeführt.")
    statistik_files = config['ZAV_FTP']['statistics_files']
    statistik_dir_ai = os.path.join(config['DIRECTORIES']['itfs_ch'], config['DIRECTORIES']['itfs_ch_subdir_statistik'])
    if not os.path.exists(statistik_dir_ai):
        os.makedirs(statistik_dir_ai)
    ftp = AGILib.downloader.FTPDownloader(dest_dir=statistik_dir_ai, ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['statistics_directory'], ftp_filenames=statistik_files)
    ftp.download()

    logger.info("Statistik-Download (für DAT) wird ausgeführt.")
    statistik_dir_dat = os.path.join(config['DIRECTORIES']['archiv'], datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    if os.path.exists(statistik_dir_dat):
        AGILib.folder_files.clean_folder_recursive(statistik_dir_dat)
    else:
        os.makedirs(statistik_dir_dat)
    AGILib.folder_files.clean_folder(statistik_dir_dat)
    ftp = AGILib.downloader.FTPDownloader(dest_dir=statistik_dir_dat, ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['statistics_directory'], ftp_filenames=statistik_files)
    ftp.download()

    logger.info("ITF-Download (Modell Bern) wird ausgeführt.")
    ftp = AGILib.downloader.FTPDownloader(dest_dir=config['DIRECTORIES']['itfs'], ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['itf_directory'])
    ftp.download()

    increment_mode_file = os.path.join(statistik_dir_ai, "zav_integration.csv")
    logger.info("Ermittle Inkrement-Modus aus " + increment_mode_file)
    checker_logs_dir = os.path.join(config['DIRECTORIES']['itfs_ch'], config['DIRECTORIES']['itfs_ch_subdir_logs'])
    if not os.path.exists(checker_logs_dir):
        os.makedirs(checker_logs_dir)
    increment_mode = get_mode_from_csv(increment_mode_file)
    if increment_mode == "full":
        logger.info("Inkrement-Modus ist " + increment_mode)
        logger.info("Es werden sämtliche Files heruntergeladen.")
        logger.info("ITF-Download (AVCH) wird ausgeführt.")
        ftp = AGILib.downloader.FTPDownloader(dest_dir=config['DIRECTORIES']['itfs_ch'], ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['itf_ch_directory'])
        ftp.download()
        logger.info("Checker-Log-Download wird ausgeführt.")
        ftp = AGILib.downloader.FTPDownloader(dest_dir=checker_logs_dir, ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['itf_ch_logs'])
        ftp.download()
    elif increment_mode == "increment":
        logger.info("Inkrement-Modus ist " + increment_mode)
        logger.info("Liste der herunterzuladenden Files wird ausgelesen:")
        increment_file = os.path.join(statistik_dir_ai, "zav_inkrement.csv")
        (itf_files_to_download, log_files_to_download) = get_itf_files_from_csv(increment_file)
        logger.info("ITF-Download (AVCH) wird ausgeführt.")
        ftp = AGILib.downloader.FTPDownloader(dest_dir=config['DIRECTORIES']['itfs_ch'], ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['itf_ch_directory'], ftp_filenames=itf_files_to_download)
        ftp.download()
        logger.info("Checker-Log-Download wird ausgeführt.")
        ftp = AGILib.downloader.FTPDownloader(dest_dir=checker_logs_dir, ftp_host=config['ZAV_FTP']['host'], ftp_username=config['ZAV_FTP']['username'], ftp_password=config['ZAV_FTP']['password'], ftp_directory=config['ZAV_FTP']['itf_ch_logs'], ftp_filenames=log_files_to_download)
        ftp.download()
    else:
        logger.error("Ungültiger Wert zum Inkrement-Modus in " + increment_mode_file)
        logger.error("Es werden keine AVCH-Files heruntergeladen.")
        sys.exit()

    avLader.helpers.helper.delete_connection_files(config, logger)