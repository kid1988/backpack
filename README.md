##BACKPACK
####Bottle.py application structure for fast start
Backpack is a bottle.py boilerplate with all necessary utilites which can help you get started fast and develop your applications rapidly.
<br>

**On board:**

- Configuration<br>
Add your config options to 'config/config.ini',<br>
Add banned ip addresses to 'config/netban.dat'

- Registration / Login
<br>
See users.py

- User sessions
<br>
Access user session data trough `request.environ.get('beaker.session')`<br>
Access logged in user using `request.user`

- Access management
```python
from bottle import protected
@route('/')
def index():
	protected('admin') #only admin pass further
	return {}
```

- Flash messages
```python
from bottle import flash
@route('/')
def index():
	flash('Message', 'status')
	return {}
```

- Sendmail
```python
from bottle import mail
@route('/send')
def index():
	mail('template.html', subject='Notification', name='John Doe', email='johndoe@host.tld', **template_ctx)
	return {}
```

- Template globals<br>
Access current `request` {{request}}<br>
Pop flash messages using `flashes()`<br>
Add your own globals at wsgi.py<br>

###Getting started

####Installation
```sh
	cd backpack
	make install-py3
```

####Run dev. server
- Edit 'config/config.ini'
- Start a mongod instance
- Run dev server
```sh
	python3 wsgi.py
```

####Add functionality
- Add new python module with your web applications
- Add html templates to the views directory
- Import your module in 'imports.py'
