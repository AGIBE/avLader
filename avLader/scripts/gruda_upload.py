# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper
import avLader.helpers.ftp_helper
import os
import glob
from shutil import copyfile

ftp_files = {}
    
def process_ftp_listing(ftp_line):
    splitted_line = ftp_line.split(';')
    modify = splitted_line[2].split('=')[1]
    filename = splitted_line[4].strip()
    ftp_files[modify] = filename

def run():
    config = avLader.helpers.config_helper.get_config('gruda_upload')
    
    logger = config['LOGGING']['logger']
    logger.info("GRUDA-Upload wird ausgeführt.")
    
    list_of_files = glob.glob(config['DIRECTORIES']['gruda_lieferung']) 
    latest_file = max(list_of_files, key=os.path.getctime)
    
    zip_file_ori = os.path.join(config['DIRECTORIES']['gruda_lieferung'], latest_file)
    zip_filename = config['DIRECTORIES']['gruda_filename']
    zip_file = os.path.join(config['DIRECTORIES']['gruda'], zip_filename)
    
    # copy and replace old zip-file
    copyfile(zip_file_ori, zip_file)
    logger.info("Datei wird kopiert von " + zip_file_ori + " nach " + zip_file)

    logger.info("Upload auf den infoGrips-Server beginnt.")
    try:    
        avLader.helpers.ftp_helper.upload_zip(zip_file, zip_filename, config, logger)
        logger.info("Upload auf den infoGrips-Server beendet.")
    except Exception as e:
        logger.error("Upload auf den infoGrips-Server nicht erfolgreich!")
        logger.error(e)

    avLader.helpers.connection_helper.delete_connection_files(config, logger)    