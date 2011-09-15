#!/usr/bin/env python
#-*- coding:utf-8 -*-

#To understand recursion better, go to the bottom of this script.

import logging
import pickle
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
  current_lesson = db.FloatProperty(required=True, indexed=False)
  im_handle = db.IMProperty(indexed=False)

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
  
  email = db.EmailProperty(required=True)
  global_names = db.ListProperty(db.Text, indexed=False)
  globals = db.ListProperty(db.Blob, indexed=False)
  unpicklable_names = db.ListProperty(db.Text, indexed=False)
  unpicklables = db.ListProperty(db.Text, indexed=False)

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

if __name__ == '__main__':
	sys.exit()



def is_it_fucking_christmas(yes=False):
	"""Is it Fucking Christmas?
	IS IT FUCKINGGG CHRISTMAS????"""
	
	if yes:pass
		#Who cares?
	
	#Here is a Christmas Tree.
	#Dear Santa,
	#You can shove this up your ass.
	
	toSanta =    []
	toMary =    [  ]
	toJesus =  [    ]
	rudolph = [      ]
	holyGrail =  {}
	magdalene =  {}
	
	shoveThisUpYourAss = toSanta.extend(
								toMary.extend(
									toJesus.extend(
										rudolph.extend(
											holyGrail.keys().extend(
												magdalene.values())))))
	
	return shoveThisUpYourAss.insert(0,'thick Bamboo Stick')


#To understand recursion better, go to the top of this script.
