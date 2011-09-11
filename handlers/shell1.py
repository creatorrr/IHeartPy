#!/usr/bin/python
#
# Copyright 2007 Creatorrr! Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An interactive, Python instructor.

Uses AIML for interactive tutorial.

Latest build on GitHub http://creatorrr.github.com/IHeartPy

Interpreter state is stored as strings in the memcache so that variables, function
definitions, and other values in the global and local namespaces can be used
across commands.
"""

import logging
import new
import os
import sys
import traceback
import types
import wsgiref.handlers
import random
from re import escape
import urllib

sys.path.append(os.path.abspath(''))

import lolpython
import aiml
from models import *

try:
  from google.appengine.api import users
  from google.appengine.api import memcache
  from google.appengine.ext import db
  from google.appengine.ext import webapp
  from google.appengine.ext.webapp import template

except ImportError:
  from google3.apphosting.api import users
  from google3.apphosting.api import memcache
  from google3.apphosting.ext import db
  from google3.apphosting.ext import webapp
  from google3.apphosting.ext.webapp import template


# Set to True if stack traces should be shown in the browser, etc.
_DEBUG = True

# The entity kind for shell sessions. Feel free to rename to suit your app.
_SESSION_KIND = 'IHeartPy_Shell_Session'
_GA_ID='UA-25004086-1'

# Initializer statements to seed new sessions with.
INITIALIZERS = [
  'import logging',
  'import os',
  'import sys',
  'class Foo(db.Expando):\n  pass',
  ]

def getQuote():
  """Returns a randomized quotation"""
  libraryFile=open('../site/quotes.txt','r')
  library=libraryFile.readlines()
  return random.choice(library).split(';')

def get_memcached_values(session_key):
  """Retrieves all statements in history for given namespace"""
  
  counter=memcache.get(key='counter',namespace=session_key)
  
  if not counter:
    memcache.add(key='counter',time=7500,value=0,namespace=session_key)
    return []
  
  statement_list=[]
  key_list=[]

  flag=1
  while counter >flag:
    key_list.append('statement'+str(flag))
    flag+=1

  returned_list = memcache.get_multi(key_list,namespace=session_key).values()
  for value in returned_list:
      statement_list.append((urllib.unquote(value)).decode("string-escape"))
  return statement_list

def add_memcached_statement(statement, session_key):
  """Retrieves all statements in history for given namespace"""
  counter=memcache.get(key='counter',namespace=session_key)
  if not counter:
    memcache.add(key='counter',value=0,time=7500,namespace=session_key)
  
  memcache.incr(key='counter',namespace=session_key,initial_value=0)
  
  try:
    memcache.add(key='statement'+str(counter),time=7500,value=urllib.quote(statement),namespace=session_key)
  except:
    logging.error("Memcache miss")
    return False
  
  return True

class ShellPageHandler(webapp.RequestHandler):
  """Creates a new session and renders the shell.html template."""
  
  def generate_hash(self):
    from time import gmtime, strftime
    import sha
    seed=strftime("%A:%W, %B %d %Y", gmtime())+users.get_current_user().user_id()+users.get_current_user().email()
    return sha.new(str(seed)).hexdigest()

  def get(self):
    session_key = self.request.get('session')
    if not session_key:
      # create a new session
      session_key = self.generate_hash()

    template_file = os.path.abspath('../site/shell.html')
    if "mobile" in self.request.user_agent.lower():
		template_file = os.path.abspath('../site/mobile-shell.html')

    session_url = '/shell'
    quote=getQuote()

    notifications="Hola, %s!" % users.get_current_user().nickname()
    
    vars = { 'server_software': os.environ['SERVER_SOFTWARE'],
             'python_version': sys.version,
             'session': str(session_key),
             'user': users.get_current_user(),
             'login_url': users.create_login_url(session_url),
             'logout_url': users.create_logout_url('/'),
             'notifications': notifications,
             'quotation': quote[0],
             'quotation_author': quote[1],
             'quotation_link': quote[2],
             'title': 'Shell',
             'analytics_id':_GA_ID,
             }
    rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
    self.response.out.write(rendered)


class StatementHandler(webapp.RequestHandler):
  """Evaluates a python statement in a given session and returns the result."""

  def get(self):

    _DEFAULT_ROLE = "tester"
    user=users.get_current_user()
    query=ShellUser.all()
    query.filter("account = ", user)
    db_user = query.get()
    
    if not db_user:
       db_user = ShellUser(name=user.nickname(),
        									role=_DEFAULT_ROLE,
        									course_completed = False,
        									account = user,
        									email = user.email(),
      	  								current_lesson = 1)
       history = History(account = user,
       							number = 0)
       db_user.put()
       history.put()
  
    query=History.all()
    query.filter("account = ", user)
    history = query.get()

    self.response.headers['Content-Type'] = 'text/plain'

    # extract the statement to be run
    statement = self.request.get('statement')
    if not statement:
      return

    # the python compiler doesn't like network line endings
    statement = statement.replace('\r\n', '\n')

    # add a couple newlines at the end of the statement. this makes
    # single-line expressions such as 'class Foo: pass' evaluate happily.
    statement += '\n\n'

    lol = self.request.get('lol')
    if lol == '1':
      statement = lolpython.to_python(statement)
      import sys as _lol_sys
	
    self.response.out.write(statement)

    # log and compile the statement up front
    try:
      logging.info('Compiling and evaluating:\n%s' % statement)
      compiled = compile(statement, '<string>', 'single')
    except:
      self.response.out.write(traceback.format_exc())
      return

    # create a dedicated module to be used as this statement's __main__
    statement_module = new.module('__main__')

    # use this request's __builtin__, since it changes on each request.
    # this is needed for import statements, among other things.
    import __builtin__
    statement_module.__builtins__ = __builtin__

    # load the session
    session_key = self.request.get('session')

    # swap in our custom module for __main__.
    old_main = sys.modules.get('__main__')
    try:
      sys.modules['__main__'] = statement_module
      statement_module.__name__ = '__main__'

      # re-evaluate the statements history
      for code in get_memcached_values(session_key):
        try:
          compiled_code = compile(code, '<string>', 'single')
          exec compiled_code in statement_module.__dict__
          logging.info("Executing statements from history:"+code)
        except:
          logging.warning("Error in executing history:"+code)

      # run!
      old_globals = dict(statement_module.__dict__)
      try:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
          sys.stdout = self.response.out
          sys.stderr = self.response.out
          exec compiled in statement_module.__dict__
        finally:
          sys.stdout = old_stdout
          sys.stderr = old_stderr
      except:
        self.response.out.write(traceback.format_exc())
        return

      # statement added
      add_memcached_statement(statement, session_key)
      logging.debug('Storing this statement in memcache.')

    finally:
      sys.modules['__main__'] = old_main

def main():
  application = webapp.WSGIApplication(
    [('/shell', ShellPageHandler),
     ('/shell.do', StatementHandler)], debug=_DEBUG)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
