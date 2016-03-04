import os,sys,functools
PATH = os.path.dirname(__name__)
sys.path.append(os.path.join(PATH,'packages'))

import bottle, json
from bottle import request,abort, hook, error
from beaker.middleware import SessionMiddleware
from bottle.ext.mongo import MongoPlugin
app = bottle.default_app()
app.config.load_config(os.path.join(PATH, "config/config.ini"))

APACHE = app.config.get('site.apache') == 'true'
DEV = DEBUG = app.config.get('site.debug') == 'true'

if not DEBUG and not APACHE:
    import gevent.monkey; gevent.monkey.patch_all()

app.config['session'] = {
    'session.type': 'file',
    'session.cookie_expires': 3600*24*10,
    'session.data_dir': '/tmp/websessiondata',
    'session.auto': True
}

mongo = MongoPlugin(uri=app.config['mongodb.uri'], db=app.config['mongodb.dbname'], json_mongo=True)
app.install(mongo)
app = SessionMiddleware(app, app.config['session'])




with open(os.path.join(PATH,'views/error.html'), 'r') as f:
    bottle.ERROR_PAGE_TEMPLATE = f.read();

#template globals
def svgicon(name, width=64):
    return '<img src="/icons/%s.svg" style="width:%dpx;"/>'%(name,width)

def flashes(json=False):
    session = request.environ.get('beaker.session')
    msgStack = session.get('messages')
    if not msgStack: return []
    session['messages'] = None;
    session.save()
    if json:
        return json.dumps(msgStack)
    else:
        return msgStack

#extend bottle view
bottle.view = functools.partial(bottle.view,
    icon = svgicon,
    flashes = flashes,
    request = request
)

def flash(msg,ctype='default'):
    session = request.environ.get('beaker.session')
    msgStack = session.get('messages') or []
    msgStack.append(dict(message=msg,status=ctype))
    session['messages'] = msgStack
    session.save()
bottle.flash = flash

from sendmail_wrapper import sendmail
def mail(template, subject="No Reply", **kv):
    body = bottle.template('email/%s'%template, root=request.app.config.get('site.root'),**kv)
    sender_name = request.app.config.get('sendmail.sender', 'Notification Bot')
    sender_email = request.app.config.get('sendmail.email', 'email@local.tld')
    sendmail.send(
        To = "%s <%s>"%(kv.get('name'), kv.get('email')),
        From = "%s <%s>"%(sender_name, sender_email),
        Subject = subject,
        body = str(body)
    )
bottle.mail = mail

def protected(who=None):
    if not request.user:
        abort(403)
    if who and who in (request.user.get('group') or []):
        abort(403)
bottle.protected = protected

import re
@hook('before_request')
def before_request():
    if DEBUG: bottle.TEMPLATES.clear()
    #ip ban
    ip = request.environ.get('REMOTE_ADDR')
    with open(os.path.join(PATH, "config/netban.dat"),"r") as f:
        for pattern in f.read().split('\n'):
            if not pattern: continue
            reg = re.compile(pattern)
            if reg.match(ip):
                return abort(403, "Forbidden")

    #session
    sessionData = request.environ.get('beaker.session')
    request.user = None
    if sessionData:
        request.user = sessionData.get('user')
        if request.user:
            with open(os.path.join(PATH, "config/userban.dat"), "r") as f:
                for pattern in f.read().split('\n'):
                    if not pattern: continue
                    reg = re.compile(pattern)
                    if reg.match(request.user.get('email')):
                        return abort(403, "Forbidden")

from imports import *

if DEBUG:
    @bottle.route('/<path:path>')
    def public(path):
        return bottle.static_file(path, os.path.join(os.path.dirname(__name__), 'public'))

    class SleepMiddleware(object):
        """Emulate delays"""
        def __init__(self, app):
            self.app = app
        def __call__(self, e, h):
            import time; time.sleep(.2)
            return self.app(e,h)
    app = SleepMiddleware(app)

    from werkzeug.debug import DebuggedApplication
    app = DebuggedApplication(app, evalex=True)



if __name__=="__main__":
    if DEBUG:
        bottle.run(app,
            host="localhost",
            port=9999,
            debug=DEBUG,
            reloader=DEBUG,
        )
    else:
        from geventwebsocket.handler import WebSocketHandler
        bottle.run(app,
            host = 'localhost',
            port = 9999,
            server = 'gevent',
            handler_class = WebSocketHandler
        )
