
import db
import arrow
from pyrad import packet

from logger import info,error,debug,is_debug,log_ctx
from signals import (send_accounting_start_signal,
                    send_accounting_stop_signal)

STATUS_TYPE_START   = 1
STATUS_TYPE_STOP    = 2
STATUS_TYPE_UPDATE  = 3
STATUS_TYPE_NAS_ON  = 7
STATUS_TYPE_NAS_OFF = 8


class _AccountingRequestHandler():
    def process(self,req):
        attr_keys = list(req.keys())
        if is_debug():
            log_ctx.base_info(ip=req.source[0],msgtype='ACCOUNTING PKT')
            #for attr in attr_keys:
            debug_info = '\t\t'.join("%s: %s" %(attr, req[attr]) for attr in attr_keys)
            debug("Accounting packet from :%s [%s]" %(req.source[0],debug_info))


        username = req.get_username()
        if not username:
            debug('ERROR no username provided')
            return self.send_response(req)

        radiususer = db.get_radiususer_from_name(username)
        if not radiususer :
            debug('ERROR radius user not found in DB')
            return self.send_response(req)
        if not radiususer.active:
            debug('ERROR radius user is not active')
            return self.send_response(req)

        radiusnas_id = radiususer.nas_id
        radiusnas = db.get_nas_from_id(radiusnas_id)

        if not radiusnas:
            debug('ERROR no radiusnas')
            return self.send_response(req)

        log_ctx.add_nas_info(nasid=radiusnas_id, siteid=radiusnas.siteid)

        req.secret = radiusnas.secret

        reply = req.CreateReply()
        reply.source = req.source

        acct_status_type  = req.get_acctstatustype()

        if acct_status_type == STATUS_TYPE_START:
            log_ctx.update_packet_type('Accounting Start')
            return self.start_accounting(req,radiusnas)
        elif acct_status_type == STATUS_TYPE_STOP:
            log_ctx.update_packet_type('Accounting Stop')
            return self.stop_accounting(req,radiusnas)
        elif acct_status_type == STATUS_TYPE_UPDATE:
            log_ctx.update_packet_type('Accounting Status')
            return self.update_accounting(req,radiusnas)
        elif acct_status_type == STATUS_TYPE_NAS_ON or \
             acct_status_type == STATUS_TYPE_NAS_OFF  :
            log_ctx.update_packet_type('Accounting NAS On/Off')
            return self.nasonoff_accounting(req,radiusnas,acct_status_type)
        else:
            return self.send_response(req)

    def send_response(self,req):
        reply = req.CreateReply()
        reply.source = req.source
        reply.code=packet.AccountingResponse
        req.sock.sendto(reply.ReplyPacket(), reply.source)

    def start_accounting(self,req,radiusnas):
        username = req.get_username()

        if not username:
            if is_debug():
                debug('Got empty username')
            return self.send_response(req)

        sessionid = req.get_accnt_sessionid()
        if not sessionid:
            if is_debug():
                debug('Got empty sessionid')
            return self.send_response(req)

        radiususer = db.get_radiususer(radiusnas.id,username)
        if not radiususer:
            if is_debug():
                debug('Got unknown username :%s'%username)
            return self.send_response(req)

        framed_ip_address = req.get_framed_ip()
        if not framed_ip_address:
            if is_debug():
                debug('ERROR no Framed-IP provided')
            return self.send_response(req)

        send_accounting_start_signal(username)

        radiussession = db.create_radius_session(radiusnas,radiususer,sessionid,framed_ip_address)
        if not radiussession:
            if is_debug():
                debug('Something went wrong while accounting session creation ')
            return self.send_response(req)

        if is_debug():
            debug('[Acct] User[%s],Nas[%s] billing starting'%(radiususer.radiususer,radiusnas.id))

        return self.send_response(req)


    def stop_accounting(self,req,radiusnas):
        username = req.get_username()

        if not username:
            if is_debug():
                debug('Got empty username')
            return self.send_response(req)

        sessionid = req.get_accnt_sessionid()
        if not sessionid:
            if is_debug():
                debug('Got empty sessionid')
            return self.send_response(req)

        radiususer = db.get_radiususer(radiusnas.id,username)
        if not radiususer:
            if is_debug():
                debug('Got unknown username :%s'%username)
            return self.send_response(req)


        radiussession = db.get_radiussession(radiusnas,radiususer,sessionid)

        if not radiussession:
            if is_debug():
                debug('No session found ')
            return self.send_response(req)

        data_used = req.get_totaldatausage()
        time_used = round(req.get_acctsessiontime()/60,0)
        db.update_radiussession(radiussession.id,
                                data_used=data_used,
                                time_used=time_used,
                                disassoc=True)
        send_accounting_stop_signal(username)
        if is_debug():
            debug('[Acct] User[%s] Session-ID[%s] Used[%s Mb] in [%s mins] STOP'%(radiususer.radiususer,
                            radiussession.accnt_sessionid,data_used,time_used))
        return self.send_response(req)

    def update_accounting(self,req,radiusnas):
        username = req.get_username()

        if not username:
            if is_debug():
                debug('Got empty username')
            return self.send_response(req)

        sessionid = req.get_accnt_sessionid()
        if not sessionid:
            if is_debug():
                debug('Got empty sessionid')
            return self.send_response(req)

        radiususer = db.get_radiususer(radiusnas.id,username)
        if not radiususer:
            if is_debug():
                debug('Got unknown username :%s'%username)
            return self.send_response(req)


        radiussession = db.get_radiussession(radiusnas,radiususer,sessionid)

        if not radiussession:
            if is_debug():
                debug('No session found ')
            return self.send_response(req)

        data_used = req.get_totaldatausage()
        time_used = round(req.get_acctsessiontime()/60,0)
        db.update_radiussession(radiussession.id,
                                data_used=data_used,
                                time_used=time_used)
        if is_debug():
            debug('[Acct] User[%s] Session-ID[%s] Used[%s Mb] in [%s mins]'%(radiususer.radiususer,
                            radiussession.accnt_sessionid,data_used,time_used))
        return self.send_response(req)

    def nasonoff_accounting(self,req,radiusnas,status_type):
        if status_type == STATUS_TYPE_NAS_ON :
            info("[Acct] nas [%s] on : success"%radiusnas.identity)
        elif status_type == STATUS_TYPE_NAS_OFF:
            info("[Acct] nas [%s] off : success"%radiusnas.identity)
        return self.send_response(req)



_handler = _AccountingRequestHandler()

def accountingHandler(req):
    _handler.process(req)