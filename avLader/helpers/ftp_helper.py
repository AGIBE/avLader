# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ftplib
import socket
import ssl
import os.path
import shutil
import sys
import zipfile
import datetime
import avLader.helpers.ftp_proxy

# Aus: http://stackoverflow.com/questions/12164470/python-ftp-tls-connection-issue
class tyFTP(ftplib.FTP_TLS):
    def __init__(self, host='', user='', passwd='', acct='', keyfile=None, certfile=None, timeout=60):
        ftplib.FTP_TLS.__init__(self, host, user, passwd, acct, keyfile, certfile, timeout)
        
    def connect(self, host='', port=0, timeout=-999):
        '''
        Connect to host.  Arguments are:
        :param host:
        :param port:
        :param timeout:
        '''
        if host != '':
            self.host = host
        if port > 0:
            self.port = port
        if timeout != -999:
            self.timeout = timeout
        try:
            self.sock = socket.create_connection((self.host, self.port), self.timeout)
            self.af = self.sock.family
            #add this line!!!
            self.sock = ssl.wrap_socket(self.sock, self.keyfile, self.certfile,ssl_version=ssl.PROTOCOL_TLSv1)
            #add end
            self.file = self.sock.makefile('rb')
            self.welcome = self.getresp()
        except Exception as e:
            print(e)
        return self.welcome

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
    ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    ftp.cwd(ftp_directory)
    ftp.retrbinary('RETR ' + ftp_file, open(downloaded_file,'wb').write)
    ftp.quit()
    
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
        
def upload_zip(zip_file, zip_filename, config, logger):
    ftp_host = config['INFOGRIPS_FTP']['host']
    ftp_username = config['INFOGRIPS_FTP']['username']
    ftp_password = config['INFOGRIPS_FTP']['password']
    
    avLader.helpers.ftp_proxy.setup_http_proxy("proxy.be.ch", 8080)

    logger.info("Verbinde mit " + ftp_host)
    ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    logger.info("Datei " + zip_file + " wird hochgeladen.")
    ftp.storbinary('STOR ' + zip_filename, open(zip_file, 'rb'), 1024)
    ftp.quit()