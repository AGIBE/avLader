# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from cryptography.fernet import Fernet
import os

class Crypter(object):
    '''
    Hilfsklasse für die Ent- und Verschlüsselung der Passwörter sowie
    für die Erstellung von Schlüsseln
    Basiert auf der cryptography-Library: https://cryptography.io/en/latest/fernet/
    Der zu verwendende Schlüssel wird über eine Umgebungsvariable übergeben.
    '''
    
    @staticmethod
    def generate_key():
        return Fernet.generate_key().decode("utf-8")

    def __init__(self, key_envvar='AGILIBSECRET'):
        '''
        @summary: Konstruktor
        :param key_envvar (string): Name der Umgebungsvariable, in der der Schlüssel für die Verschlüsselung abgelegt ist. (default: AGILIBSECRET)
        """
        '''
        self.key_envvar = key_envvar
        if os.getenv(self.key_envvar, None) is not None:
            self.key = os.environ[key_envvar].encode("utf-8")
            self.fernet = Fernet(self.key)
        else:
            raise OSError(
                "Die Umgebungsvariable %s wurde nicht gefunden." %
                (self.key_envvar)
            )
        
    def encrypt(self, data):
        '''
        verschlüsselt den übergebenen String
        
        :param data: zu verschlüsselnder String
        '''
        # encode/decode ist notwendig, weil Fernet mit bytes arbeitet und nicht mit unicode
        encrypted_bytes = self.fernet.encrypt(data.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    
    def decrypt(self, data):
        '''
        entschlüsselt den übergebenen String
        
        :param data: zu entschlüsselnder String
        '''
        # encode/decode ist notwendig, weil Fernet mit bytes arbeitet und nicht mit unicode
        decrypted_bytes = self.fernet.decrypt(data.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")