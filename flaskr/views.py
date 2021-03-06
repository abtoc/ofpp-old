from datetime      import date
from dateutil.relativedelta import relativedelta
from flask         import request, redirect, url_for, render_template, flash
from flaskr        import app,db
from flaskr.models import Person, WorkRec

@app.route('/')
def index():
    today = date.today()
    yymm = today.strftime('%Y%m')
    yesterday =  today - relativedelta(days=1)
    if yesterday.weekday() == 6:
        yesterday =  today - relativedelta(days=1)
    prevm = today - relativedelta(months=1)
    yymm_1 = prevm.strftime('%Y%m')
    persons = Person.query.filter_by(enabled=True).order_by(Person.staff.asc(),Person.name.desc()).all()
    items = []
    for person in persons:
        item = {}
        item['id'] = person.id
        item['name'] = person.display
        workrec = WorkRec.get_date(person.id, today)
        item['work_in'] = ''
        item['work_out'] = ''
        if workrec is not None:
            if workrec.work_in is not None:
                item['work_in'] = workrec.work_in
            elif workrec.situation is not None:
                item['work_in'] = workrec.situation
            if workrec.work_out is not None:
                item['work_out'] = workrec.work_out
            elif workrec.reason is not None:
                item['work_out'] = workrec.reason
        workrec = WorkRec.get_date(person.id, yesterday)
        item['work_in_1'] = ''
        item['work_out_1'] = ''
        if workrec is not None:
            if workrec.work_in is not None:
                item['work_in_1'] = workrec.work_in
            elif workrec.situation is not None:
                item['work_in_1'] = workrec.situation
            if workrec.work_out is not None:
                item['work_out_1'] = workrec.work_out
            elif workrec.reason is not None:
                item['work_out_1'] = workrec.reason
        items.append(item)
    return render_template('index.pug', items=items, yymm=yymm, yymm_1=yymm_1)
    #return redirect(url_for('persons.index'))

@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"]        = "DENY"
    response.headers["X-XSS-Protection"]       = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

from flaskr  import views_persons
app.register_blueprint(views_persons.bp)
from flaskr  import views_workrecs
app.register_blueprint(views_workrecs.bp)
from flaskr  import api_idm
app.register_blueprint(api_idm.bp)
from flaskr  import views_pdf
app.register_blueprint(views_pdf.bp)
from flaskr  import views_auth
app.register_blueprint(views_auth.bp)
from flaskr  import views_users
app.register_blueprint(views_users.bp)
from flaskr  import views_options
app.register_blueprint(views_options.bp)
