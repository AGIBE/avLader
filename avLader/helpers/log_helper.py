# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import chromalog
import os
import datetime

def init_logging(config, subcommand):
    log_directory = os.path.join(config['LOGGING']['basedir'], subcommand)
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logfile = os.path.join(log_directory, subcommand + "_" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log")
        
    logger = logging.getLogger("avLaderLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(create_loghandler_file(logfile))
    logger.addHandler(create_loghandler_stream())
    logger.propagate = False
    
    return logger

def create_loghandler_stream():
    '''
    Konfiguriert einen Stream-Loghandler. Der Output
    wird in sys.stdout ausgegeben. In der Regel ist das
    die Kommandozeile. Falls sys.stdout dies unterst�tzt,
    werden Warnungen und Fehler farbig ausgegeben (dank
    des chromalog-Moduls).
    '''
    
    file_formatter = chromalog.ColorizingFormatter('%(levelname)s|%(message)s')
    
    h = chromalog.ColorizingStreamHandler()
    h.setLevel(logging.DEBUG)
    h.setFormatter(file_formatter)
    
    return h
    
def create_loghandler_file(filename):
    '''
    Konfiguriert einen File-Loghandler
    :param filename: Name (inkl. Pfad) des Logfiles 
    '''
    
    file_formatter = logging.Formatter('%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', '%Y-%m-%d %H:%M:%S')
    
    h = logging.FileHandler(filename, encoding="UTF-8")
    h.setLevel(logging.DEBUG)
    h.setFormatter(file_formatter)
    
    return h