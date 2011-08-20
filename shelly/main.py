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
I Heart Py!
FrontPageHandler

"""


import logging
import new
import os
import sys
import traceback
import types
import wsgiref.handlers


try:
  from google.appengine.api import users
  from google.appengine.ext import webapp
  from google.appengine.ext.webapp import template

except ImportError:
  from google3.apphosting.api import users
  from google3.apphosting.ext import webapp
  from google3.apphosting.ext.webapp import template

# Set to True if stack traces should be shown in the browser, etc.
_DEBUG = False



def getQuote():
  """Gets a randomized quotation"""
#fetch quotes from BrainyQuote API
  return ("There is no charge for awesomeness... or attractiveness.","Kung Fu Panda","http://www.google.co.in/search?ie=UTF-8&q=kung+fu+panda+awesomeness")

class FrontPageHandler(webapp.RequestHandler):
  """Creates a new session and renders the Front Page."""

  def get(self):
    # set up the session. TODO: garbage collect old shell sessions

    template_file = os.path.join(os.path.dirname(__file__), 'site','main.html')
    session_url = '/shell'

    vars = { 'user': users.get_current_user(),
             'login_url': users.create_login_url('/shell'),
             'logout_url': users.create_logout_url('/'),
             'quotation': getQuote()[0],
             'quotation_author': getQuote()[1],
             'quotation_link': getQuote()[2],
             'title': 'Home',
             }
    rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
    self.response.out.write(rendered)

class ResourcePageHandler(webapp.RequestHandler):
  """Renders the Resources Page."""

  def get(self):
    # set up the session. TODO: garbage collect old shell sessions

    template_file = os.path.join(os.path.dirname(__file__), 'site','resources.html')
    session_url = '/shell'

    vars = { 'user': users.get_current_user(),
             'login_url': users.create_login_url('/shell'),
             'logout_url': users.create_logout_url('/'),
             'quotation': getQuote()[0],
             'quotation_author': getQuote()[1],
             'quotation_link': getQuote()[2],
             'title': 'Resources',
             }
    rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
    self.response.out.write(rendered)


class InstructionsPageHandler(webapp.RequestHandler):
  """Renders the Instructions Page."""

  def get(self):
    # set up the session. TODO: garbage collect old shell sessions

    template_file = os.path.join(os.path.dirname(__file__), 'site','instructions.html')
    session_url = '/shell'

    vars = { 'user': users.get_current_user(),
             'login_url': users.create_login_url('/shell'),
             'logout_url': users.create_logout_url('/'),
             'quotation': getQuote()[0],
             'quotation_author': getQuote()[1],
             'quotation_link': getQuote()[2],
             'title': 'Instructions',
             }
    rendered = webapp.template.render(template_file, vars, debug=_DEBUG)
    self.response.out.write(rendered)


def main():
  application = webapp.WSGIApplication(
    [('/', FrontPageHandler),('/resources', ResourcePageHandler),('/instructions', InstructionsPageHandler)], debug=_DEBUG)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
