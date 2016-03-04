##BACKPACK
####Bottle.py application structure for fast start
Backpack is a bottle.py boilerplate with all necessary utilities which can help you get started fast and develop your applications rapidly.
<br>

**On board:**


- Registration / Login
<br>
Ready to use register and login controllers and templates

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
	flash('Message', 'error')
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

- User sessions
<br>
Access user session data trough `request.environ.get('beaker.session')`<br>
Access logged in user using `request.user`

- Configuration<br>
Add your config options to `config/config.ini`,<br>
Add banned ip addresses to `config/netban.dat`


###Getting started

####Installation
```sh
	cd backpack
	make install-py3
```

####Run dev. server
. Edit 'config/config.ini' <br>
. Start a mongod instance <br>
. Run dev server <br>
```sh
	python3 wsgi.py
```

####Add functionality
. Add new python module with your web applications <br>
. Add html templates to the views directory <br>
. Import your module in 'imports.py' <br>

####License
BSD
