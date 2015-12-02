# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import datetime

def prepare_fme_log(fme_script, log_directory):
    prefix = os.path.splitext(os.path.basename(fme_script))[0]
    fme_logfilename = prefix + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log"
    fme_logfile = os.path.join(log_directory, fme_logfilename)
    
    return fme_logfile