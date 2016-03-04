import os; os.chdir(os.path.dirname(__file__));
from wsgi import app
application = app
