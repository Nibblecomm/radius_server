#!/usr/bin/env python
#coding:utf-8
from gevent.server import DatagramServer
from gevent import socket
from access_handler import accessHandler
from accounting_handler import accountingHandler
from pyrad import dictionary
#from settings import radiuslog 
from pyrad.packet import Packet
from pyrad.tools import DecodeString
from logger import error,exception
from packets import AuthPacket2,AcctPacket2
import six
import gevent
import argparse
import os

MaxPacketSize = 8192

try:
    from instance.cloud_config import RADIUS_SENTRY_DSN
except:
    RADIUS_SENTRY_DSN = None
else:
    import sentry_sdk
    sentry_sdk.init(RADIUS_SENTRY_DSN)



class RudiusAuthServer(DatagramServer):

    def __init__(self, address,nases={},dict=None):
        DatagramServer.__init__(self,address)
        self.address = address
        self.dict = dict
        self.start()
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,3000000)

    def handle(self,data, address):
        try:
            auth_pkt = AuthPacket2(packet=data,dict=self.dict)
            auth_pkt.source,auth_pkt.sock = address,self.socket
            gevent.spawn(accessHandler,auth_pkt)
        except Exception as err:
            exception('process packet error:' + str(err))              




class RudiusAcctServer(DatagramServer):

    def __init__(self, address,nases={},dict=None):
        DatagramServer.__init__(self,address)
        self.address = address
        self.dict = dict
        self.start()
        self.socket.setsockopt(socket.SOL_SOCKET,
            socket.SO_RCVBUF,3000000)

    def handle(self,data, address):
        try:
            pkt = AcctPacket2(packet=data,dict=self.dict)
            pkt.source,pkt.sock = address,self.socket
            gevent.spawn(accountingHandler,pkt)    
        except Exception as err:
            exception('process packet error:' + str(err))     


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", help="directory which have dictionary")
    args = parser.parse_args()

    if args.workdir:
        workdir = args.workdir
    else:
        workdir = os.path.join(os.path.abspath(os.path.dirname(__file__)))

    dict_file = os.path.join(workdir,'dictionary')

    authsrv = RudiusAuthServer(address=('0.0.0.0',1812),dict=dictionary.Dictionary(dict_file))
    acctsrv = RudiusAcctServer(address=('0.0.0.0',1813),dict=dictionary.Dictionary(dict_file))
    authsrv.serve_forever()
    acctsrv.serve_forever()
    
