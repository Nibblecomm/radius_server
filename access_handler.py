import db
import arrow
from pyrad import packet
from logger import error,debug,is_debug,log_ctx

class _AccessRequestHandler():

    def process(self,req):
        attr_keys = list(req.keys())
        if is_debug():
            # for attr in attr_keys:
            log_ctx.base_info(ip=req.source[0],msgtype='AUTH PKT')
            debug_info = '\t\t'.join("%s: %s" % (attr, req[attr]) for attr in attr_keys)
            debug("Received [%s]" % (debug_info))

        username = req.get_username()
        if not username:
            debug('ERROR no username provided')
            return self.send_reject(req,'ERROR no username provided')

        radiususer = db.get_radiususer_from_name(username)
        if not radiususer:
            debug('ERROR radius user not found in DB')
            return self.send_reject(req,'ERROR no radiususer found with given username or radiususer not active')

        if not radiususer.active:
            debug('ERROR radius user is inactive')
            return self.send_reject(req,'ERROR no radiususer found with given username or radiususer not active')

        radiusnas_id = radiususer.nas_id
        radiusnas = db.get_nas_from_id(radiusnas_id)

        if not radiusnas:
            return self.send_reject(req,'ERROR unknown NAS ID')
        log_ctx.add_nas_info(nasid=radiusnas_id,siteid=radiusnas.siteid)

        #set secret
        req.secret = radiusnas.secret.encode('utf-8')

        if not req.is_valid_pwd(radiususer.radiuspass):
            if is_debug():
                debug('Got unknown password ')
            return self.send_reject(req,'ERROR Incorrect password')



        session_expiry = arrow.get(radiususer.stoptime)
        time_available = session_expiry.timestamp  -arrow.utcnow().timestamp
        if not time_available > 0:
            if is_debug():
                debug('Guestsession:%s expired at :%s '%(radiususer.stoptime,session_expiry.humanize()))
            return self.send_reject(req,'ERROR expired user credentials')

        rcvd_mac = req.get_macaddr()
        if not rcvd_mac:
            return self.send_reject(req,'ERROR no Calling-Station-Id provided')

        if not rcvd_mac.lower() == radiususer.mac.lower():
            if is_debug():
                debug('Expected MAC :%s got ;%s '%(radiususer.mac,rcvd_mac))
            return self.send_reject(req,'ERROR Invalid credentials for this device')


        return self.send_accept(req,radiusnas,
                        time_available=time_available,
                        speed_ul=int(radiususer.speed_ul) , #convert to bps
                        speed_dl=int(radiususer.speed_dl) ,
                        data_limit = radiususer.data_limit ) #convert to bytes



    def send_reject(self,req,err):
        reply = req.CreateReply(msg=err)
        reply.source = req.source
        reply.code=packet.AccessReject
        req.sock.sendto(reply.ReplyPacket(), reply.source)

        debug("[Auth]  send an authentication reject,err:%s"%err)

    def send_accept(self,req,radiusnas,time_available,speed_ul,speed_dl,data_limit):
        reply = req.CreateReply()
        reply.source = req.source
        reply.code=packet.AccessAccept

        reply.set_session_timeout(time_available)
        reply.set_idle_timeout(time_available)
        reply.set_intrim_update()
        if speed_dl:
            reply.set_special_int(radiusnas.vendor_id,"speed_dl",int(speed_dl))
        if speed_ul:
            reply.set_special_int(radiusnas.vendor_id,"speed_ul",int(speed_ul))
        #setting data limits is a bit tricky, some routers accept single value for total data.
        #some accept different for dl/ul
        reply.set_special_int(radiusnas.vendor_id,"data_limit",int(data_limit))
        reply.set_special_int(radiusnas.vendor_id,"dl_data_limit",int(data_limit))
        reply.set_special_int(radiusnas.vendor_id,"ul_data_limit",int(data_limit))
        req.sock.sendto(reply.ReplyPacket(), reply.source)

        if is_debug():
            debug("[Auth] send an authentication accept,user[%s]"\
                %(req.get_username()))

_handler = _AccessRequestHandler()

def accessHandler(auth_pkt):
    _handler.process(req=auth_pkt)