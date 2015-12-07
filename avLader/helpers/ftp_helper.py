# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ftplib
import socket
import ssl
import os.path
import shutil
import sys
import zipfile

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

def download_fgdb(ftp_filename, config, logger):
    ftp_host = config['ZAV_FTP']['host']
    ftp_username = config['ZAV_FTP']['username']
    ftp_password = config['ZAV_FTP']['password']
    ftp_directory = config['ZAV_FTP']['directory']
    ftp_file = ftp_filename
    download_dir = config['DIRECTORIES']['local_data_dir']
    
    downloaded_file = os.path.join(download_dir, ftp_file)
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

    logger.info("Verbinde mit " + ftp_host)
    ftp = ftplib.FTP(ftp_host, ftp_username, ftp_password)
    logger.info("Datei " + zip_file + " wird hochgeladen.")
    ftp.storbinary('STOR ' + zip_filename, open(zip_file, 'rb'), 1024)
    ftp.quit()