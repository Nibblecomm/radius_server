#!/usr/bin/python

from pyrad.client import Client
from pyrad.dictionary import Dictionary
import random
import socket
import sys
import pyrad.packet
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
path_to_dictionary = os.path.join(currentdir,'..',"dictionary")


def SendPacket(srv, req):
    try:
        srv.SendPacket(req)
    except pyrad.client.Timeout:
        print("RADIUS server does not reply")
        sys.exit(1)
    except socket.error as error:
        print("Network error: " + error[1])
        sys.exit(1)
    else:
        print("Account Request has been processed by server successfully!")

srv = Client(server="127.0.0.1", secret=b"56rmkuri92d8a0wvi9divyxvn1nku3", dict=Dictionary(path_to_dictionary))

req = srv.CreateAcctPacket(User_Name="VZJ9VTB662KI7F1ZHFF8YBW8PNV1ECEQD3FZAMSY2")

req["NAS-IP-Address"] = "192.168.1.10"
req["NAS-Port"] = 0
req["NAS-Identifier"] = "azae0j07sbjzcyc2hg66_ac86745dbe40"
req["Called-Station-Id"] = "00-04-5F-00-0F-D1"
req["Calling-Station-Id"] = "00-01-24-80-B3-9C"
req["Framed-IP-Address"] = "10.0.0.100"
req["Acct-Session-Id"] = '80200028'

req["Acct-Status-Type"] = "Start"
SendPacket(srv,req)

