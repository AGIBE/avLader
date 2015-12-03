# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import ftplib
import socket
import ssl

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
