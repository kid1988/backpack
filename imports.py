import bottle
import os, sys

from resources import users

@bottle.get('/',template="index.html")
def index():
    return {}
