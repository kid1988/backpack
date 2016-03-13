import bottle
import os, sys

from controllers import users

@bottle.get('/',template="index.html")
def index():
    return {}
