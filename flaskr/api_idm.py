from flask         import Blueprint
from flask         import request, jsonify
from flaskr        import db, cache, auth
from flaskr.models import Person, WorkRec, User
from flaskr.workrule import *
from flaskr.worker import enabled_workrec
from datetime      import datetime
import json

bp = Blueprint('api_idm', __name__, url_prefix="/api/idm")

@auth.verify_password
def verify_pw(username,password):
    user, checked = User.auth(username,password)
    return checked

def get_work_in(hhmm, staff):
    if staff:
        work_rules = work_rules_staff
    else:
        work_rules = work_rules_staff_no
    for i in work_rules:
        if (i['work_in']) and (i['start_time'] <= hhmm) and (hhmm < i['end_time']):
            return i
    return None

def get_work_out(hhmm, staff):
    if staff:
        work_rules = work_rules_staff
    else:
        work_rules = work_rules_staff_no
    for i in work_rules:
        if (i['work_out']) and (i['start_time'] <= hhmm) and (hhmm < i['end_time']):
            return i
    return None

@bp.route('/<idm>',methods=['GET'])
@auth.login_required
def get_idm(idm):
    cache.set('idm', idm, 30*60)
    person = Person.query.filter_by(idm=idm).first()
    if person is None:
        return jsonify({"name": "該当者無し"}), 404
    result = dict(
        name=person.display
    )
    return jsonify(result), 200

@bp.route('/<idm>',methods=['DELETE'])
@auth.login_required
def delete_idm(idm):
    cache.set('idm', None, 30*60)
    return jsonify({}), 200

@bp.route('/<idm>',methods=['POST'])
@auth.login_required
def post_idm(idm):
    cache.set('idm', None, 5*60)
    person = Person.query.filter_by(idm=idm).first()
    if person is None:
        return jsonify({"message": "Not Found!"}), 404
    now=datetime.now()
    yymm=now.strftime('%Y%m')
    dd=now.day
    hhmm=now.strftime('%H:%M')
    workrec=WorkRec.get(person.id, yymm, dd)
    creation=False
    if workrec is None:
        creation = True
        work_in = get_work_in(hhmm, person.staff)
        workrec = WorkRec(person_id=person.id, yymm=yymm,dd=dd, work_in=hhmm)
    else:
        work_in  = get_work_in(workrec.work_in, person.staff)
        work_out = get_work_out(hhmm, person.staff)
        break_t  = 0.0
        if (work_in['value'] < 12.0) and (work_out['value'] > 13.0):
            break_t = 1.0
        value    = work_out['value'] - work_in['value'] - break_t
        if value < 0:
            value = 0
            break_t = 0
        over_t   = 0.0
        if value > 8.0:
            over_t = value - 8.0
        workrec.work_out = hhmm
        workrec.value    = value
        workrec.break_t  = break_t
        workrec.over_t   = over_t
    db.session.add(workrec)
    try:
        db.session.commit()
        enabled_workrec.delay(person.id, yymm)
    except:
        db.session.rollback()
        return jsonify({}), 500
    if creation:
        result = dict(
            work_in  = workrec.work_in,
            work_out = '--:--'
        )
        return jsonify(result), 201
    result = dict(
        work_in  = workrec.work_in,
        work_out = workrec.work_out
    )
    return jsonify(result), 200