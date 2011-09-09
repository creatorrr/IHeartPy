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
import pickle
import new
import os
import sys
import traceback
import types
import wsgiref.handlers
import random

sys.path.append(os.path.abspath(''))

import lolpython
import aiml
import highlighter

try:
  from google.appengine.api import users
  from google.appengine.ext import db
  from google.appengine.ext import webapp
  from google.appengine.ext.webapp import template
  from google.appengine.ext.webapp.util import login_required
  INITIAL_UNPICKLABLES = [
    'from google.appengine.ext import db',
    'from google.appengine.api import users',
	]

except ImportError:
  from google3.apphosting.api import users
  from google3.apphosting.ext import db
  from google3.apphosting.ext import webapp
  from google3.apphosting.ext.webapp import template
  from google3.apphosting.ext.webapp.util import login_required
  INITIAL_UNPICKLABLES = [
    'from google3.apphosting.ext import db',
    'from google3.apphosting.api import users',
    ]


# Set to True if stack traces should be shown in the browser, etc.
_DEBUG = False

# The entity kind for shell sessions. Feel free to rename to suit your app.
_SESSION_KIND = 'IHeartPy_Shell_Session'
_GA_ID='UA-25004086-1'

# Types that can't be pickled.
UNPICKLABLE_TYPES = (
  types.ModuleType,
  types.TypeType,
  types.ClassType,
  types.FunctionType,
  )

# Unpicklable statements to seed new sessions with.
INITIAL_UNPICKLABLES += [
  'import logging',
  'import os',
  'import sys',
  'class Foo(db.Expando):\n  pass',
  ]

class Session(db.Model):
  """A shell session. Stores the session's globals.

  Each session globals is stored in one of two places:

  If the global is picklable, it's stored in the parallel globals and
  global_names list properties.
  
  If the global is not picklable (e.g. modules, classes, and functions), or if
  it was created by the same statement that created an unpicklable global,
  it's not stored directly. Instead, the statement is stored in the
  unpicklables list property. On each request, before executing the current
  statement, the unpicklable statements are evaluated to recreate the
  unpicklable globals.

  The unpicklable_names property stores all of the names of globals that were
  added by unpicklable statements. When we pickle and store the globals after
  executing a statement, we skip the ones in unpicklable_names.

  Using Text instead of string is an optimization. We don't query on any of
  these properties, so they don't need to be indexed.
  """
  
  global_names = db.ListProperty(db.Text)
  globals = db.ListProperty(db.Blob)
  unpicklable_names = db.ListProperty(db.Text)
  unpicklables = db.ListProperty(db.Text)

  def set_global(self, name, value):
    """Adds a global, or updates it if it already exists.

    Also removes the global from the list of unpicklable names.

    Args:
      name: the name of the global to remove
      value: any picklable value
    """
    blob = db.Blob(pickle.dumps(value))

    if name in self.global_names:
      index = self.global_names.index(name)
      self.globals[index] = blob
    else:
      self.global_names.append(db.Text(name))
      self.globals.append(blob)

    self.remove_unpicklable_name(name)

  def remove_global(self, name):
    """Removes a global, if it exists.

    Args:
      name: string, the name of the global to remove
    """
    if name in self.global_names:
      index = self.global_names.index(name)
      del self.global_names[index]
      del self.globals[index]

  def globals_dict(self):
    """Returns a dictionary view of the globals.
    """
    return dict((name, pickle.loads(val))
                for name, val in zip(self.global_names, self.globals))

  def add_unpicklable(self, statement, names):
    """Adds a statement and list of names to the unpicklables.

    Also removes the names from the globals.

    Args:
      statement: string, the statement that created new unpicklable global(s).
      names: list of strings; the names of the globals created by the statement.
    """
    self.unpicklables.append(db.Text(statement))

    for name in names:
      self.remove_global(name)
      if name not in self.unpicklable_names:
        self.unpicklable_names.append(db.Text(name))

  def remove_unpicklable_name(self, name):
    """Removes a name from the list of unpicklable names, if it exists.

    Args:
      name: string, the name of the unpicklable global to remove
    """
    if name in self.unpicklable_names:
      self.unpicklable_names.remove(name)


def getQuote():
  """Returns a randomized quotation"""
  libraryFile=open('../site/quotes.txt','r')
  library=libraryFile.readlines()
  return (random.choice(library)).split(';')

def responder(statement,chat):
  """Returns a randomized quotation"""
  kernel=aiml.Kernel()
  kernel.verbose(False)
  current_lesson = 1.1 #TODO: Lesson Initializr
  kernel.bootstrap(brainFile='rawAIML/lesson%d.brn'%(int(current_lesson)),commands=[])
  statement=statement.replace('=',' EQUALS ').replace('**',' POW ').replace('*',' MUL ').replace('(','').replace(')','').replace('"','')
  chat=chat.replace('=',' EQUALS ').replace('**',' POW ').replace('*',' MUL ').replace('(','').replace(')','').replace('"','')
  kernel.setPredicate('topic','lesson%d'%(int(current_lesson*10)%10))
  kernel.setBotPredicate('user',users.get_current_user().nickname())
  kernel.setPredicate('gender','male') #TODO: gert gender info
  reply=''
  if kernel.respond(statement).split('#')[0]:
      reply+='\n#'+(kernel.respond(statement).split('#')[0].replace('\n','\n#'))
  if kernel.respond(chat):
      reply+='\n#'+kernel.respond(chat).replace('\n','\n#')
  return reply+'\n'

class ShellPageHandler(webapp.RequestHandler):
  """Creates a new session and renders the shell.html template."""

  def get(self):
    # set up the session. TODO: garbage collect old shell sessions
    session_key = self.request.get('session')
    if session_key:
      session = Session.get(session_key)
    else:
      # create a new session
      session = Session()
      session.unpicklables = [db.Text(line) for line in INITIAL_UNPICKLABLES]
      session_key = session.put()

    template_file = os.path.abspath('../site/shell.html')
    if "mobile" in self.request.user_agent.lower():
		template_file = os.path.abspath('../site/mobile-shell.html')

    session_url = '/shell'
    quote=getQuote()

    notifications="Hola, %s!" % users.get_current_user().nickname()
    
    greetings = """Welcome to IHeartPy console.\nStart coding right away.\nType python commands below and hit Enter.\nFor new lines hit: Shift+Enter\n\nTo get started, type #Hello and hit enter.\nHappy coding.\n"""
    
    vars = { 'server_software': os.environ['SERVER_SOFTWARE'],
             'python_version': sys.version,
             'session': str(session_key),
             'user': users.get_current_user(),
             'login_url': users.create_login_url(session_url),
             'greetings': greetings,
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

  @login_required
  def get(self):
    # extract the statement to be run
    statement = self.request.get('statement')
    if not statement:
      return

    # the python compiler doesn't like network line endings
    statement = statement.replace('\r\n', '\n')

    reply=''
    chat=(''.join([statement,'#']).split('#')[1])

    # add a couple newlines at the end of the statement. this makes
    # single-line expressions such as 'class Foo: pass' evaluate happily.
    statement += '\n'

    lol = self.request.get('lol')
    if lol == '1':
      statement = lolpython.to_python(statement)
      import sys as _lol_sys

    self.response.clear()

    if "mobile" in self.request.user_agent.lower():
        self.response.headers['Content-Type'] = 'text/html'
        highlighter.Parser(statement,self.response.out).format()
    else:
        self.response.headers['Content-Type'] = 'text/text'
        self.response.out.write(statement)
        statement = statement.split('#')[0]
        reply=responder(statement,chat)

    # log and compile the statement up front
    try:
      logging.info('Compiling and evaluating:\n%s' % statement)
      if statement.strip():
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

    # load the session from the datastore
    session = Session.get(self.request.get('session'))

    # swap in our custom module for __main__. then unpickle the session
    # globals, run the statement, and re-pickle the session globals, all
    # inside it.
    old_main = sys.modules.get('__main__')
    try:
      sys.modules['__main__'] = statement_module
      statement_module.__name__ = '__main__'

      # re-evaluate the unpicklables
      for code in session.unpicklables:
        exec code in statement_module.__dict__

      # re-initialize the globals
      for name, val in session.globals_dict().items():
        try:
          statement_module.__dict__[name] = val
        except:
          msg = 'Dropping %s since it could not be unpickled.\n' % name
          self.response.out.write(msg)
          logging.warning(msg + traceback.format_exc())
          session.remove_global(name)

      # run!
      old_globals = dict(statement_module.__dict__)
      try:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
          sys.stdout = self.response.out
          sys.stderr = self.response.out
          if statement.strip():
                exec compiled in statement_module.__dict__
        finally:
          sys.stdout = old_stdout
          sys.stderr = old_stderr
      except:
        self.response.out.write(traceback.format_exc())
        self.response.out.write(responder('some stupid error',''))
        return

      # extract the new globals that this statement added
      new_globals = {}
      for name, val in statement_module.__dict__.items():
        if name not in old_globals or val != old_globals[name]:
          new_globals[name] = val

      if True in [isinstance(val, UNPICKLABLE_TYPES)
                  for val in new_globals.values()]:
        # this statement added an unpicklable global. store the statement and
        # the names of all of the globals it added in the unpicklables.
        session.add_unpicklable(statement, new_globals.keys())
        logging.debug('Storing this statement as an unpicklable.')

      else:
        # this statement didn't add any unpicklables. pickle and store the
        # new globals back into the datastore.
        session.set_global('help', 'Use the instructions link at the bottom for more info.')
        session.set_global('author', 'Diwank Singh')
        session.set_global('about', 'The friendly Python Instructor')
        session.set_global('inspiration', 'Ila Nitin Gokarn')
        for name, val in new_globals.items():
          if not name.startswith('__'):
            session.set_global(name, val)

    finally:
      sys.modules['__main__'] = old_main

    self.response.out.write(reply)
    session.put()


def main():
  application = webapp.WSGIApplication(
    [('/shell', ShellPageHandler),
     ('/shell.do', StatementHandler)], debug=_DEBUG)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
