#To understand recursion better, go to the bottom of this script.

import types

try:
  from google.appengine.api import users
  from google.appengine.ext import db
  from google.appengine.ext import webapp
  from google.appengine.ext.webapp import template
  INITIAL_UNPICKLABLES = [
    'from google.appengine.ext import db',
    'from google.appengine.api import users',
	]

except ImportError:
  from google3.apphosting.api import users
  from google3.apphosting.ext import db
  from google3.apphosting.ext import webapp
  from google3.apphosting.ext.webapp import template
  INITIAL_UNPICKLABLES = [
    'from google3.apphosting.ext import db',
    'from google3.apphosting.api import users',
    ]


_DEBUG = False

_SESSION_KIND = 'IHeartPy_Shell_Session'

UNPICKLABLE_TYPES = (
  types.ModuleType,
  types.TypeType,
  types.ClassType,
  types.FunctionType,
  )

INITIAL_UNPICKLABLES += [
  'import logging',
  'import os',
  'import sys',
  'class Foo(db.Expando):\n  pass',
  ]

notifications = [
  'Hola, &#223;-Tester! Rough Seas ahead...',
  'Give Feedback!',
  'Something broken?',
  'Oh dear...',
  'Glad to see you.',
  ]


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
