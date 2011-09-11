#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging
import os
import sys
import types
import random

sys.path.append(os.path.abspath(''))


try:
  from google.appengine.api import users
  from google.appengine.ext import db

except ImportError:
  from google3.apphosting.api import users
  from google3.apphosting.ext import db

class ShellUser(db.Model):
  """Holds user properties."""
  
  name = db.StringProperty(required=True)
  role = db.StringProperty(required=True, choices=set(["admin", "tester", "student"]), indexed=False)
  first_access_date = db.DateProperty(auto_now_add=True, indexed=False)
  last_access_date = db.DateProperty(auto_now=True, indexed=False)
  course_completed = db.BooleanProperty(required=True, indexed=False)
  account = db.UserProperty(required=True)
  email = db.EmailProperty(required=True)
  current_lesson = db.RatingProperty(required=True, indexed=False)
  im_handle = db.IMProperty(indexed=False)

class History(db.Model):
  """History holds statements history for a kiddo.
  
  Using Text instead of string is an optimization. We don't query on any of
  these properties, so they don't need to be indexed.
  """
  account = db.UserProperty(required=True)
  statements = db.ListProperty(db.Text, indexed=False)
  access_time = db.DateTimeProperty(auto_now=True, indexed=False)

if __name__ == '__main__':
	sys.exit()
