import bottle
from bottle import view, request, redirect, flash, mail
from werkzeug.security import generate_password_hash, check_password_hash
import uuid, datetime, time
from pymongo import ReturnDocument
"""
    user:
        - name : string
        - email : string
        - password : string
        - token : string
        - verified : boolean
        - group : list
"""
@bottle.get('/register', template="account/register.html")
def register():
    if request.user:
        return redirect('/')
    session = request.environ.get('beaker.session')
    data = session.get('register-input') or {}
    session['register-input'] = None
    session.save()
    return dict(**data)

@bottle.post('/register')
def register_post(mongodb):
    name = request.forms.get('name')
    email = request.forms.get('email')
    password = request.forms.get('password')
    password2 = request.forms.get('repeat_password')

    session = request.environ.get('beaker.session')
    session['register-input'] = dict(
        name = name,
        email = email
    )
    session.save()

    if name and email and '@' in email and password and (password==password2):
        exists = mongodb['users'].find_one(dict(
            email = email
        ))
        if exists:
            flash('User with such email already exists.', 'danger')
            return redirect('/register')

        token = str(uuid.uuid4())
        mongodb['users'].insert_one(dict(
                name = name,
                email = email,
                password = generate_password_hash(password),
                token = token,
                verified = False,
                group = ['user']
        ))
        mail('registration.html', "Registration Confirmation",
                name = name,
                email = email,
                token = token,
        )
        flash('Registration successful, check your email to confirm your registration', 'success')
        return redirect('/login')

    flash('Incomplete Credentials', 'warning')
    return redirect('/register')

@bottle.get('/register/verify/<token>')
def verify_registration(token, mongodb):
    user = mongodb['users'].find_one(dict(token=token))
    if not user: return redirect('/')
    mongodb['users'].find_one_and_update({"_id":user['_id']},{
        "$set":{
            'token':None,
            'verified':True
        }
    })
    flash('Thank you. Account Verified.', 'success')
    return redirect('/login')

@bottle.get('/login',template = 'account/login.html')
def login():
    if request.user:
        return redirect('/')
    return dict()

@bottle.post('/login')
def login_post(mongodb):

    email = request.forms.get('email')
    password = request.forms.get('password')

    if not email or not password:
        flash('Wrong Credentials', 'danger')
        return redirect('/login')

    user = mongodb['users'].find_one(dict(email=email))
    if not user:
        flash('User doesn\'t exists.', 'warning')
        return redirect('/')

    if not check_password_hash(user['password'], password):
        flash('Wrong Credentials.', 'danger')
        return redirect('/login')

    user = mongodb['users'].find_one_and_update(dict(_id=user['_id']),{
        "$set":{
            "last_login":str(datetime.datetime.now())
        }},
        return_document=ReturnDocument.AFTER
    )
    session = request.environ.get('beaker.session')
    session['user'] = user
    session.save()
    #flash('Hello %s'%user['name'], 'success')
    return redirect("/")

@bottle.get('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session.delete()
    flash('Goodbay', 'success')
    return redirect('/')
