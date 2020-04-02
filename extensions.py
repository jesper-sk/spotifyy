import os
import os.path
import sys
import time

import pickle

from .sessions import SpotifySession

from programy.extensions.base import Extension
from programy.utils.logging.ylogger import YLogger

from spotipy.client import SpotifyException

class SpotifyExtension(Extension):
  spotify_exception_handlers = {
    "Player command failed: No active device found" : "NODEVICE",
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


    retry = False
    if params[0] == "retry":
      retry = True
      params = params[1:]

    if ((not self.session.is_logged_in) or self.session.is_token_expired()) and params[0] != "login":
      if os.path.isfile('uname.txt'):
        self.session.login()
      else:
        return "LOGINFIRST"

    cmd = 'self.session.' + params[0] + '(' + ','.join(params[1:]) + ')'

    succeeded = False
    try:
      result = eval(cmd)
      succeeded = True

    except SpotifyException as ex:
      YLogger.exception_nostack(context, "Spotify exception raised", ex)
      message = str(ex).splitlines()[1].strip()
      #YLogger.exception_nostack(context, "Spotify exception raised", message)

      if message == "Device not found":
        self.session.reset_device()
        return self.execute(context, data)

      code = self.spotify_exception_handlers.get(message, "GENERIC")
      fail = f"PYFAIL SPOTIFYY {code} {params[0].replace('_', '').upper()}"

    except (NameError, AttributeError, SyntaxError) as ex:
      YLogger.exception_nostack(context, f"Couldn't evaluate command {cmd}", ex)
      fail = f"PYFAIL INVALIDCOMMAND {params[0].replace('_', '').upper()}"

    except Exception as ex:
      YLogger.exception_nostack(context, f"Spotify extension fail with {cmd}", ex)
      fail = "PYFAIL ERROR"

    with open('session.pickle', 'wb') as file:
      pickle.dump(self.session, file, pickle.HIGHEST_PROTOCOL)

    if retry:
      if os.path.isfile('latestfail.txt'):
        with open('latestfail.txt', 'r') as file:
          cmd = file.read()
        os.remove('latestfail.txt')
        try:
          return eval(cmd)
        except:
          pass


    if succeeded:
      return result
    else:
      with open("latestfail.txt", 'w') as file:
        file.write(cmd)
      return fail