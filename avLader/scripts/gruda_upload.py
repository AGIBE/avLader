# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.ftp_helper
import os

ftp_files = {}
    
def process_ftp_listing(ftp_line):
    splitted_line = ftp_line.split(';')
    modify = splitted_line[2].split('=')[1]
    filename = splitted_line[4].strip()
    ftp_files[modify] = filename
    
def download_file(config, logger):
    ftp_host = config['GRUDA_FTP']['host']
    ftp_port = int(config['GRUDA_FTP']['port'])
    ftp_username = config['GRUDA_FTP']['username']
    ftp_password = config['GRUDA_FTP']['password']
    ftp_directory = config['GRUDA_FTP']['directory']
    download_dir = config['DIRECTORIES']['gruda']
    
    ftps = avLader.helpers.ftp_helper.tyFTP()
    logger.info("FTP-Verbindung mit Server " + ftp_host + ":" + unicode(ftp_port) + " wird geöffnet.")
    ftps.connect(host=ftp_host, port=ftp_port)
    ftps.login(ftp_username, ftp_password)
    ftps.prot_p()
    ftps.cwd(ftp_directory)
    # MLSD liefert die Dateiinfos maschinenlesbar d.h. mit Strichpunkt getrennt zurueck
    ftps.retrlines('MLSD', process_ftp_listing)
    
    # Sortieren nach der Modified-Information
    newest_key = sorted(ftp_files.keys(), reverse=True)[0]
    file_to_download = ftp_files[newest_key]
    logger.info("Folgende Datei wird heruntergeladen: " + file_to_download)
    
    # File herunterladen
    downloaded_file = os.path.join(download_dir, file_to_download)
    ftps.retrbinary('RETR ' + file_to_download, open(downloaded_file, 'wb').write)
    
    ftps.quit()
    
    return downloaded_file

def run():
    config = avLader.helpers.config_helper.get_config('gruda_upload')
    
    logger = config['LOGGING']['logger']
    logger.info("GRUDA-Upload wird ausgeführt.")
    
    logger.info("Alte Zip-Datei wird gelöscht.")
    zip_filename = config['GRUDA_FTP']['filename']    
    zip_file = os.path.join(config['DIRECTORIES']['gruda'], zip_filename)
    if os.path.exists(zip_file):
        logger.info("Lösche " + zip_file)
        os.remove(zip_file)
    
    downloaded_file = download_file(config, logger)
    
    logger.info("Datei wird umbenannt von " + os.path.basename(downloaded_file) + " in " + os.path.basename(zip_file))
    os.rename(downloaded_file, zip_file)

    logger.info("Upload auf den infoGrips-Server beginnt.")    
    avLader.helpers.ftp_helper.upload_zip(zip_file, zip_filename, config, logger)
    logger.info("Upload auf den infoGrips-Server beendet.")

    avLader.helpers.connection_helper.delete_connection_files(config, logger)    