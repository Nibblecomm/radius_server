#!/usr/bin/env python
#coding:utf-8
import sys
import logging
import os
import inspect
import google.cloud.logging # Don't conflict with standard logging
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

__loglevel = logging.DEBUG
try:
    from instance.cloud_config import GRAYLOG_SERVER
except:
    GRAYLOG_SERVER = None

def is_debug():
  return __loglevel == logging.DEBUG




class ContextFilter(logging.Filter):
    def __init__(self, filter_name):
        super(ContextFilter, self).__init__(filter_name)
        self.nasip = ''
        self.nasid = ''
        self.siteid = ''
        self.msgtype = ''

    def filter(self, record):
        record.nasip = self.nasip
        record.nasid = self.nasid
        record.siteid = self.siteid
        record.msgtype = self.msgtype
        return True

    def base_info(self,ip,msgtype):
        self.nasip = ip
        self.nasid = ''
        self.siteid = ''
        self.msgtype = msgtype

    def add_nas_info(self,nasid,siteid):
        self.nasid = nasid
        self.siteid = siteid

    def update_packet_type(self,msgtype):
        self.msgtype = msgtype


log_ctx = ContextFilter(filter_name='radlog')

def getLogger(name, level=__loglevel):
    formatter = logging.Formatter('%(nasip)s %(nasid)s %(siteid)s %(msgtype)s %(message)s', '%a, %d %b %Y %H:%M:%S', )
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.addFilter(log_ctx)

    if GRAYLOG_SERVER:
        client = google.cloud.logging.Client()
        cloud_handler = CloudLoggingHandler(client, name="radiusd")
        logger.addHandler(cloud_handler)
        setup_logging(cloud_handler)
        cloud_handler.addFilter(log_ctx)
        cloud_handler.setFormatter(formatter)
    else:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

radiuslog = getLogger("radiusd",level=__loglevel)

info        = radiuslog.info
debug       = radiuslog.debug
error       = radiuslog.error
exception   = radiuslog.exception
warning     = radiuslog.warning

