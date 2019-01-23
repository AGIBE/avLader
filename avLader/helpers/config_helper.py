# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.crypto_helper
import avLader.helpers.log_helper
import avLader.helpers.connection_helper
import configobj
import os

def decrypt_passwords(section, key):
    '''
    Entschlüsselt sämtliche Passworte in der zentralen
    Konfigurationsdatei. Wird aus der ConfigObj.walk-Funktion
    aus aufgerufen. Deshalb sind section und key als
    Parameter obligatorisch.
    :param section: ConfigObj.Section-Objekt
    :param key: aktueller Schlüssel im ConfigObj-Objekt
    '''
    # Hilfsklasse für die Entschlüsselung
    
    # Annahme: alle Keys, die "password" heissen, enthalten zu entschlüsselnde Passwörter
    crypter = avLader.helpers.crypto_helper.Crypter()
    if key == "password":
        encrypted_password = section[key]
        decrypted_password = crypter.decrypt(encrypted_password)
        # Wert in der Config ersetzen
        section[key] = decrypted_password


def get_general_configfile_from_envvar():
    '''
    Holt den Pfad zur Konfigurationsdatei aus der Umgebungsvariable
    OEREBIMPORTHOME und gibt dann den vollständigen Pfad (inkl. Dateiname)
    der Konfigurationsdatei zurück.
    '''
    config_directory = os.environ['AVIMPORTHOME']
    config_filename = "config.ini"
    
    config_file = os.path.join(config_directory, config_filename)
    
    return config_file

def init_generalconfig():
    '''
    liest die zentrale Konfigurationsdatei in ein ConfigObj-Objet ein.
    Dieser kann wie ein Dictionary gelesen werden.
    '''
    config_filename = get_general_configfile_from_envvar()
    config_file = configobj.ConfigObj(config_filename, encoding="UTF-8")
    
    # Die Walk-Funktion geht rekursiv durch alle
    # Sections und Untersections der Config und 
    # ruft für jeden Key die angegebene Funktion
    # auf
    config_file.walk(decrypt_passwords)
    
    return config_file.dict()

def create_connection_string(config, key):
    username = config[key]['username']
    password = config[key]['password']
    database = config[key]['database']
    
    connection_string = username + "/" + password + "@" + database
    config[key]['connection_string'] = connection_string
    
def get_config(subcommand):
    config = init_generalconfig()
    
    logger = avLader.helpers.log_helper.init_logging(config, subcommand)
    logger.info('Konfiguration wird eingelesen.')
    config['LOGGING']['logger'] = logger

    # Connection-Strings zusammensetzen
    create_connection_string(config, 'AV01_WORK')
    create_connection_string(config, 'GEODB_DD_TEAM')
    create_connection_string(config, 'NORM_TEAM')
    
    # Connection-Files erstellen
    config['AV01_WORK']['connection_file'] = avLader.helpers.connection_helper.create_connection_files(config, 'AV01_WORK', logger)
    config['GEODB_DD_TEAM']['connection_file'] = avLader.helpers.connection_helper.create_connection_files(config, 'GEODB_DD_TEAM', logger)
    config['NORM_TEAM']['connection_file'] = avLader.helpers.connection_helper.create_connection_files(config, 'NORM_TEAM', logger)
    config['GPS1_WORKH']['connection_file'] = avLader.helpers.connection_helper.create_connection_files(config, 'GPS1_WORKH', logger)

    return config