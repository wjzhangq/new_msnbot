#!/usr/bin/python2.4
#
# Copyright (c) Michael Still 2007, released under the terms of the GNU GPL v2

"""echo.py -- a very simple echo bot

This bot just repeats what you say...
"""

def Verbs():
  """Verbs -- return the verbs which this module supports

  Takes no arguments, and returns an array of strings.
  """

  return ['echo']

def Status():
  """Status -- suggest a message to display as the status string for the bot
  
  Takes no arguments, and returns a string.
  """

  return 'Want me to echo something?'

def Help(verb):
  """Help -- display help for a verb

  Takes the name of a verb, and returns a string which is the help message for
  that verb.
  """

  if verb == 'echo':
    return 'Use this to have me repeat something you say'
  return ''

def Command(verb, line):
  """Command -- execute a given verb with these arguments

  Takes the verb which the user entered, and the remainder of the line.
  Returns a string which is sent to the user.
  """

  if verb == 'echo':
    return line

  return ""
    
def Cleanup():
  """Cleanup -- you're about to be unloaded.

  We don't need to do anthing in this case.
  """
  return

# Do initialization here
print u'echo_bot is loading'
