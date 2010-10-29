#!/usr/bin/python2.4
#
# Copyright (c) Michael Still 2006, released under the terms of the GNU GPL v2

"""system.py -- a simple system statistics package

This plugin implements a simple query interface to system statistics. It's
careful to not use input from the user as something it executes, because that
is bad, mmmkay?
"""

import commands

def Verbs():
  """Verbs -- return the verbs which this module supports

  Takes no arguments, and returns an array of strings.
  """

  return ['uptime', 'df', 'hostname', 'sensors', 'mdstat', 'gmane', 'backuplog']

def Status():
  """Status -- suggest a message to display as the status string for the bot
  
  Takes no arguments, and returns a string. In this case we return the current
  location in the MythTV user interface.
  """

  return commands.getoutput('hostname')

def Help(verb):
  """Help -- display help for a verb

  Takes the name of a verb, and returns a string which is the help message for
  that verb.
  """

  if verb == 'uptime':
    return 'uptime - returns the uptime of the system'
  if verb == 'df':
    return 'df - return the output of the df command'
  if verb == 'hostname':
    return 'hostname - return the hostname of the system'
  if verb == 'sensors':
    return 'sensors - return lm-sensors information if available'
  if verb == 'mdstat':
    return 'mdstat - show the contents of /proc/mdstat'
  if verb == 'gmane':
    return 'gmane - return status of gmane archive process'
  if verb == 'backuplog':
    return 'backuplog - return the last few lines of the backup logs'

def Command(verb, line):
  """Command -- execute a given verb with these arguments

  Takes the verb which the user entered, and the remainder of the line.
  Returns a string which is sent to the user.
  """

  if verb == 'uptime':
    return commands.getoutput('uptime')
  if verb == 'df':
    return commands.getoutput('df -h')
  if verb == 'hostname':
    return commands.getoutput('hostname')
  if verb == 'sensors':
    return commands.getoutput('sensors')
  if verb == 'mdstat':
    return commands.getoutput('cat /proc/mdstat')
  if verb == 'gmane':
    return commands.getoutput('ls -lrth /data/gmane | tail -5')
  if verb == 'backuplog':
    return commands.getoutput('tail -5 /data/backups/push-to-dreamhost.log')
  return 'Huh?'
    
def Cleanup():
  """Cleanup -- you're about to be unloaded.

  We don't need to do anthing in this case.
  """
  return

# Do initialization here
print u'system is loading'
