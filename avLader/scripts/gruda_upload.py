# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import avLader.helpers.config_helper
import avLader.helpers.connection_helper

def run():
    config = avLader.helpers.config_helper.get_config('gruda_upload')
    logger = config['LOGGING']['logger']
    logger.info("GRUDA-Upload wird ausgeführt.")
    avLader.helpers.connection_helper.delete_connection_files(config, logger)