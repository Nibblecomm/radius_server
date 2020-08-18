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
        reply = srv.SendPacket(req)
    except pyrad.client.Timeout:
        print("ERROR: RADIUS server does not reply")
        sys.exit(1)
    except socket.error as error:
        print("ERROR: Network error: " + error[1])
        sys.exit(1)
    else:
        if reply.code == pyrad.packet.AccessAccept:
            print("Access accepted")
        else:
            print("ERROR: Access denied")
            print(reply)

srv = Client(server="127.0.0.1", secret=b"56rmkuri92d8a0wvi9divyxvn1nku3", dict=Dictionary(path_to_dictionary))

req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name="VZJ9VTB662KI7F1ZHFF8YBW8PNV1ECEQD3FZAMSY")
req["User-Password"] = req.PwCrypt("GHRZ88B1QMWPV6GKI91DHZFTZBKC0NDZBMVKJ36R")


req["Calling-Station-Id"] = "f2:ff:11:22:33:44"

SendPacket(srv,req)


