#__author__ = 'Vosteen'
#   serviceNowConfig.py = sets logging for the integration process found in /opt/arcsight/snow/ServiceNowInterface.log

import logging
import logging.config
import logging.handlers

class ClientConfig():
    def __init__(self, vlogfilename):
        loglevel = logging.INFO
        logmaxbytes = 20000000
        logmaxfiles = 3

        logger = logging.getLogger('serviceNowInterface')
        logger.setLevel(loglevel)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        handler = logging.handlers.RotatingFileHandler('serviceNowLog' + vlogfilename + '.log', maxBytes=logmaxbytes, backupCount=3)
        handler.setLevel(loglevel)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

