import os
import os.path
import sys

import pickle

from .sessions import SpotifySession

from programy.extensions.base import Extension
from programy.utils.logging.ylogger import YLogger

from spotipy.client import SpotifyException

class SpotifyExtension(Extension):
  spotify_exception_handlers = {
    "Player command failed: No active devices found" : "NODEVICE",
    "Player command failed: Restriction violated" : "RESTRICTIONVIOLATED",
    "invalid request" : "INVALIDREQUEST",
    "The access token expired" : "TOKENEXPIRED"
  }

  def __init__(self):
    if os.path.isfile('session.pickle'):
      with open('session.pickle', 'rb') as file:
        self.session = pickle.load(file)
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

    try:
      result = eval(cmd)

    except SpotifyException as ex:
      YLogger.exception_nostack(context, "Spotify exception raised", ex)
      message = str(ex).splitlines()[1].strip()
      code = self.spotify_exception_handlers.get(message, "GENERIC")
      return f"PYFAIL SPOTIFYY {code} {params[0].replace('_', '').upper()}"
    except (NameError, AttributeError, SyntaxError) as ex:
      YLogger.exception_nostack(context, f"Couldn't evaluate command {cmd()}", ex)
      return f"PYFAIL INVALIDCOMMAND {params[0].replace('_', '').upper()}"
    except Exception as ex:
      YLogger.exception_nostack(context, f"Spotify extension fail with {cmd()}", ex)
      return "PYFAIL ERROR"
    

    with open('session.pickle', 'wb') as file:
      pickle.dump(self.session, file, pickle.HIGHEST_PROTOCOL)

    return result