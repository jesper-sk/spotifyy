import os
import sys
import time

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

from programy.utils.logging.ylogger import YLogger

class SpotifySession():
  def __init__(self):
    self._sp = None
    self._test = 0

    self._query_results = None
    self._query_index = None
    self._query_kind = None
    self._query_buffer = str()
    self._query_nresults = None
    self._query_page = None

    self.is_logged_in = False
    self._username = None
    #print("SpotifySession initialized.")

  #Login to a Spotify account, and initiate authenitcated Spotify object
  def login(self, uname=""):

    try:
      if len(uname) == 0:
        try:
          with open('uname.txt', 'r') as file:
            uname=file.read()
        except FileNotFoundError:
          return "PYFAIL LOGIN NONAME"

      if self.is_logged_in and _username == uname:
        return "PYOK LOGIN"

      token = util.prompt_for_user_token( username=uname
                                        , scope='ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing streaming app-remote-control playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private user-library-modify user-library-read user-top-read user-read-playback-position user-read-recently-played user-follow-read user-follow-modify'
                                        , client_id='b1559f5b27ff48a09d34e95c68c4a95d'
                                        , client_secret='5c17274ad83843259af8bd4e62b4a354'
                                        , redirect_uri='http://localhost/'
                                        )
      if token:
        self._sp = spotipy.Spotify(auth=token)
        with open("uname.txt", "w") as file:
          file.write(uname)
        return "PYOK LOGIN"

      else:
        return "PYFAIL LOGIN The authentication procedure was interrupted"

    except Exception as fail:
      return "PYFAIL LOGIN"

  def play(self):
    self._sp.start_playback()
    return "PYOK PLAYB"

  def pause(self):
    self._sp.pause_playback()
    return "PYOK PAUSE"

  def next_track(self):
    self._sp.next_track()
    return "PYOK PLAYB"

  def prev_track(self):
    self._sp.previous_track()
    return "PYOK PLAYB"

  def shuffle(self, state):
    stb = state == "on"
    self._sp.shuffle(stb)
    return "PYOK SHUFFLE " + state.upper()

  def repeat(self, state):
    self._sp.repeat(state)
    return "PYOK REPEAT " + state.upper()

  def add_curr_to_fav(self):
    d = self._sp.current_playback()
    self._sp.current_user_saved_tracks_add([d['item']['uri']])
    return "PYOK ADD " + d['item']['name'] + " by " + d['item']['artists'][0]['name']

  def current_playback(self):
    playing = self._sp.current_playback()
    name = playing['item']['name']
    artist = playing['item']['artists'][0]['name']
    return "PYOK CURRPLAYB " + name + " by " + artist

  def play_from_query(self, index=-1):
    if index >= 0:
      self._query_index = int(index) - 1

    if self._query_kind == "track":
      self._sp.start_playback(uris=[self._query_results[self._query_index]['uri']])
    else:
      self._sp.start_playback(context_uri=self._query_results[self._query_index]['uri'])

    time.sleep(0.4)

    playing = self._sp.current_playback()
    name = playing['item']['name']
    artist = playing['item']['artists'][0]['name']
    return "PYOK PLAY " + name + " by " + artist

  def play_next_from_query(self):
    self.play_from_query(index=self._query_index+1)

  def find(self, query, kind, offset=0, limit=10, play=0):
    kind = kind.strip()
    if not (kind in ["track", "album", "artist", "playlist"]):
      return "PYFAIL FIND INVALIDTYPE"

    self._query_index = 0
    self._query_kind = kind
    self._query = query
    self._offset = offset
    self._query_page = 0

    q = self._sp.search(query, type=kind)
    self._query_results = q[kind+'s']['items']

    self._query_nresults = len(self._query_results)
    if (self._query_nresults) == 0:
      return "PYFAIL FIND NORESULTS"

    if play:
      return self.play_from_query()
    else:
      return "PYOK FIND " + str(self._query_nresults)

  def print_query_result(self, page=-1):
    if page == -1:
      page = self._query_page
      
    start = page*5

    end = start + 5
    if end > self._query_nresults:
      end = self._query_nresults

    if self._query_kind == "playlist":
      print('\n'.join([str(index+1) + ': ' + x['name'] + ", owned by " + x['owner']['id'] 
        for (index, x) in enumerate(self._query_results[start:end])]))

    elif self._query_kind == "artist":
      print('\n'.join([str(index+1) + ': ' + x['name']
        for (index, x) in enumerate(self._query_results[start:end])]))

    else:
      print('\n'.join([str(index+1) + ': ' + x['name'] + " by " + x['artists'][0]['name'] 
        for (index, x) in enumerate(self._query_results[start:end])]))

    return "PYOK PRINTRESULTS"

  def print_next_query_page(self):
    self._query_page += 1
    return self.print_query_result()
