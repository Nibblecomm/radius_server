from pyrad.packet import AuthPacket
from pyrad.packet import AcctPacket
from pyrad.packet import AccessRequest
from pyrad.packet import AccessAccept
from pyrad.packet import AccountingRequest
from pyrad import tools
import binascii
import datetime
import hashlib
import six
import os
from math import pow
from logger import error,warning,exception,is_debug,debug
from settings import vendor_cfg

class AuthPacket2(AuthPacket):

    def __init__(self, code=AccessRequest, id=None, secret=six.b(''),
            authenticator=None, **attributes):
        AuthPacket.__init__(self, code, id, secret, authenticator, **attributes)

    def CreateReply(self, msg=None,**attributes):
        reply = AuthPacket2(AccessAccept, self.id,
                                self.secret, self.authenticator,
                                dict=self.dict,**attributes)
        if msg:
            reply.set_reply_msg(tools.EncodeString(msg))
        return reply


    def set_reply_msg(self,msg):
        if msg:
            self.AddAttribute(18,msg)

    def set_framed_ip_addr(self,ipaddr):
        if ipaddr:
            self.AddAttribute(8,tools.EncodeAddress(ipaddr))

    def set_session_timeout(self,timeout):
        if timeout:
            self.AddAttribute(27,tools.EncodeInteger(timeout))

    def set_idle_timeout(self,timeout):
        if timeout:
            self.AddAttribute(28,tools.EncodeInteger(timeout))

    def set_intrim_update(self,update_intreval=300):
        """
            Set the value of Acct-Interim-Interval  in Access Accept
        :param update_intreval:
        :return:
        """
        if update_intreval:
            self.AddAttribute(85,tools.EncodeInteger(update_intreval))
    def set_special_str(self,vendor,name,value):
        if not value or not vendor or not name:
            return
        try:
            if int(vendor) not in vendor_cfg:
                return
            key = vendor_cfg[int(vendor)][name]
            if key:
                self.AddAttribute(key,value)
        except Exception as e:
            exception("set_special error,vendor=%s,name=%s,value=%s;err=%s"\
                %(vendor,name,value,str(e)))

    def set_special_int(self,vendor,name,value):
        if not value or not vendor or not name:
            return
        try:
            cfg = vendor_cfg.get(int(vendor))
            if not cfg:
                return None

            attr_cfg = cfg.get(name)

            if not attr_cfg:
                return None

            attr_name = attr_cfg.get('attr')

            if attr_cfg.get('convertor'):
                value = attr_cfg['convertor'](value)

            if int(value) >= 4294967295:
                value = 4294967294

            self.AddAttribute(attr_name,value)
            print(("set_special error,vendor=%s,name=%s,value=%s" \
                      % (vendor, name, value,)))
        except Exception as e:
            exception("set_special error,vendor=%s,name=%s,value=%s;err=%s"\
                %(vendor,name,value,str(e)))

    def get_nasaddr(self):
        try:
            return tools.DecodeAddress(self.get(4)[0])
        except:
            return None

    def get_macaddr(self):
        try:
            macstr =  tools.DecodeString(self.get(31)[0]).replace("-",":")
        except:
            return None
        else:
            #check if the mac format is deadbeefcafe
            if len(macstr) == 12 and isinstance(macstr, str):
                mac = ':'.join([ "%s%s"%(macstr[2*i],macstr[2*i+1]) for i in range(0,6)])
            else:
                mac = macstr
            return mac

    def get_framed_ip(self):
        try:
            return tools.DecodeAddress(self.get(8)[0])
        except:
            return None

    def get_username(self):
        try:
            return tools.DecodeString(self.get(1)[0])
        except:
            return None


    def get_passwd(self):
        try:
            return self.PwDecrypt(self.get(2)[0])
        except:
            if is_debug():
                debug('Exception while trying to get password')
            return None

    def get_chappwd(self):
        try:
            return tools.DecodeOctets(self.get(3)[0])
        except:
            return None


    def get_nasid(self):
        try:
            return self.get(32)[0]
        except:
            if is_debug():
                exception('Exception while trying to get nas id')
            return None

    def get_accnt_sessionid(self):
        try:
            return self.get(44)[0]
        except:
            if is_debug():
                exception('Exception while trying to get accounting session id')
            return None


    def is_valid_pwd(self,userpwd):
        if not self.get_chappwd():
            return userpwd == self.get_passwd()
        else:
            return self.VerifyChapPasswd(userpwd)


class AcctPacket2(AcctPacket):
    def __init__(self, code=AccountingRequest, id=None, secret=six.b(''),
            authenticator=None, **attributes):
        AcctPacket.__init__(self, code, id, secret, authenticator, **attributes)

    def get_nasid(self):
        try:
            return self.get(32)[0]
        except:
            if is_debug():
                exception('Exception while trying to get nas id')
            return None

    def get_acctstatustype(self):
        try:
            return tools.DecodeInteger(self.get(40)[0])
        except:
            if is_debug():
                exception('Exception while trying to get nas accounting status')
            return None

    def get_accnt_sessionid(self):
        try:
            return self.get(44)[0]
        except:
            if is_debug():
                exception('Exception while trying to get accounting session id')
            return None

    def get_macaddr(self):
        try:
            return tools.DecodeString(self.get(31)[0]).replace("-",":")
        except:
            return None
        else:
            #check if the mac format is deadbeefcafe
            if len(macstr) == 12 and isinstance(macstr, str):
                mac = ':'.join([ "%s%s"%(macstr[2*i],macstr[2*i+1]) for i in range(0,6)])
            else:
                mac = macstr
            return mac

    def get_username(self):
        try:
            return tools.DecodeString(self.get(1)[0])
        except:
            if is_debug():
                exception('Exception while trying to get username')
            return None

    def get_framed_ip(self):
        try:
            return tools.DecodeAddress(self.get(8)[0])
        except:
            return None

    def get_acctinputoctets(self):
        try:
            return tools.DecodeInteger(self.get(42)[0])
        except:
            return None

    def get_acctoutputoctets(self):
        try:
            return tools.DecodeInteger(self.get(43)[0])
        except:
            return None

    def get_acctsessiontime(self):
        try:
            return tools.DecodeInteger(self.get(46)[0])
        except:
            return None

    def get_acctinputpackets(self):
        try:
            return tools.DecodeInteger(self.get(47)[0])
        except:
            return None

    def get_acctoutputpackets(self):
        try:
            return tools.DecodeInteger(self.get(48)[0])
        except:
            return None

    def get_acctterminatecause(self):
        try:
            return tools.DecodeInteger(self.get(49)[0])
        except:
            return None

    def get_acctinputgigawords(self):
        try:
            return tools.DecodeInteger(self.get(52)[0])
        except:
            return None

    def get_acctoutputgigawords(self):
        try:
            return tools.DecodeInteger(self.get(53)[0])
        except:
            return None

    def get_totaldatausage(self):
        input_bytes = self.get_acctinputoctets() or 0
        output_bytes = self.get_acctoutputoctets() or 0
        input_gigbytes = self.get_acctinputgigawords() or 0
        output_gigbytes = self.get_acctoutputgigawords() or 0

        total_data = (pow(2,32) * input_gigbytes) + (pow(2,32) * output_gigbytes)  + \
                                input_bytes + output_bytes

        return round(total_data/(1024*1024),0)