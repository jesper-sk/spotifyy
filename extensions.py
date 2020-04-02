import os
import os.path
import sys

import pickle

from .sessions import SpotifySession

from programy.extensions.base import Extension

class SpotifyExtension(Extension):
  def __init__(self):
    if os.path.isfile('session.pickle'):
      file = open('session.pickle', 'rb')
      self.session = pickle.load(file)
      file.close()
    else:
      self.session = SpotifySession()

  def execute(self, context, data):   
    params = [x.strip().lower() for x in data.split(',')]

    if params[0] == "close":
      os.remove('session.pickle')
      return "EXIT"

    if (not self.session.is_logged_in) and params[0] != "login":
      if os.path.isfile('uname.txt'):
        self.session.login()
      else:
        return "LOGINFIRST"

    if self.session.is_logged_in:
      pass
      #TODO: Check if token expired and refresh if so

    cmd = 'self.session.' + params[0] + '(' + ','.join(params[1:]) + ')'

    #TODO: tryexcept (ERR-FAIL)
    result = eval(cmd)

    file = open('session.pickle', 'wb')
    pickle.dump(self.session, file)
    file.close()

    return result