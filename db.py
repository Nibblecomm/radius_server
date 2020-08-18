from sqlalchemy.orm import scoped_session,sessionmaker
from caches import online_cache,user_cache,cache_data,stat_cache
from models import engine
from sqlalchemy.exc import SQLAlchemyError
from logger import info,error,warning,debug,exception,is_debug
import arrow
import models

Session = sessionmaker(bind=engine,autocommit=False, autoflush=False)
def get_db_session():
    return Session()



@cache_data()
def get_site_from_key(sitekey):
    session = get_db_session()
    result = session.query(models.Wifisite).filter_by(sitekey = sitekey).first()
    session.close()
    return result

@cache_data()
def get_site_from_d(siteid):
    session = get_db_session()
    result = session.query(models.Wifisite).filter_by(id=siteid).first()
    session.close()
    return result

@cache_data()
def get_nas(identity):
    session = get_db_session()
    result = session.query(models.Radiusnas).filter_by(identity = identity).first()
    session.close()
    return result

@cache_data()
def get_nas_from_id(id):
    session = get_db_session()
    result = session.query(models.Radiusnas).filter_by(id = id).first()
    session.close()
    return result

@cache_data()
def get_radiususer(nasid,username):
    session = get_db_session()
    result = session.query(models.Radiususer).filter_by(nas_id=nasid,radiususer=username).first()
    session.close()
    return result

@cache_data()
def get_radiususer_from_name(username):
    session = get_db_session()
    result = session.query(models.Radiususer).filter_by(radiususer=username).first()
    session.close()
    return result

@cache_data()
def get_radiussession(radiusnas,radiususer,sessionid):
    session = get_db_session()
    result = session.query(models.Radiussessions).filter_by(nas_id=radiusnas.id,
                                                                    radiususer_id=radiususer.id,
                                                                    accnt_sessionid=sessionid
                                                                    ).first()

    session.close()
    return result

def update_radiussession(id,data_used=None,time_used=None,disassoc=None):
    session = get_db_session()
    radiussession = session.query(models.Radiussessions).get(id)
    radiussession.lastseen_time = arrow.utcnow().naive
    if data_used:
        radiussession.data_used = data_used
    if time_used:
        radiussession.duration = int(time_used)
    if disassoc:
        radiussession.disassoc_time = arrow.utcnow().naive
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        session.close()
        exception('Exception while trying to create session')
        return None
    else:
        session.close()
        return radiussession

def create_radius_session(radiusnas,radiususer,accnt_sessionid,framed_ip_address):
    radiussession = models.Radiussessions(
                                          nas_id=radiusnas.id,
                                          radiususer_id=radiususer.id,
                                          mac=radiususer.mac,
                                          accnt_sessionid=accnt_sessionid,
                                          framed_ip_address=framed_ip_address)
    session = get_db_session()
    try:
        session.add(radiussession)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        session.close()
        exception('Exception while trying to create session')
        return None
    else:
        session.close()
        return radiussession