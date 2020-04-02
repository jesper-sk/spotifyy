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
          file = open("uname.txt", "r")
          uname = file.read()
          file.close()
        except FileNotFoundError:
          return "LOGINFAILNONAME"

      if self.is_logged_in and _username == uname:
        return "LOGINOK"

      token = util.prompt_for_user_token( username=uname
                                        , scope='ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing streaming app-remote-control playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private user-library-modify user-library-read user-top-read user-read-playback-position user-read-recently-played user-follow-read user-follow-modify'
                                        , client_id='b1559f5b27ff48a09d34e95c68c4a95d'
                                        , client_secret='5c17274ad83843259af8bd4e62b4a354'
                                        , redirect_uri='http://localhost/'
                                        )
      if token:
        self._sp = spotipy.Spotify(auth=token)
        file = open("uname.txt", "w")
        file.write(uname)
        file.close()
        return "LOGINOK"

      else:
        return "LOGINFAIL The authentication procedure was interrupted"

    except Exception as fail:
      return "LOGINFAIL"

  def play(self):
    self._sp.start_playback()
    return "PLAYBOK"

  def pause(self):
    self._sp.pause_playback()
    return "PAUSEOK"

  def next_track(self):
    self._sp.next_track()
    return "PLAYBOK"

  def prev_track(self):
    self._sp.previous_track()
    return "PLAYBOK"

  def shuffle(self, state):
    stb = state == "on"
    self._sp.shuffle(stb)
    return "SHUFFLEOK " + state

  def repeat(self, state):
    self._sp.repeat(state)
    return "REPEATOK " + state.upper()

  def add_curr_to_fav(self):
    d = self._sp.current_playback()
    self._sp.current_user_saved_tracks_add([d['item']['uri']])
    return "ADDOK " + d['item']['name'] + " by " + d['item']['artists'][0]['name']

  def current_playback(self):
    playing = self._sp.current_playback()
    name = playing['item']['name']
    artist = playing['item']['artists'][0]['name']
    return "CURRPLAYBOK " + name + " by " + artist

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
    return "PLAYOK " + name + " by " + artist

  def play_next_from_query(self):
    self.play_from_query(index=self._query_index+1)

  def find(self, query, kind, offset=0, limit=10, play=0):
    kind = kind.strip()
    if not (kind in ["track", "album", "artist", "playlist"]):
      return "FINDFAILTYPE"

    self._query_index = 0
    self._query_kind = kind
    self._query = query
    self._offset = offset
    self._query_page = 0

    q = self._sp.search(query, type=kind)
    self._query_results = q[kind+'s']['items']

    self._query_nresults = len(self._query_results)
    if (self._query_nresults) == 0:
      return "FINDFAILNORESULTS"

    if play:
      return self.play_from_query()
    else:
      return "FINDOK " + str(self._query_nresults)

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

    return "PRINTRESULTSOK"

  def print_next_query_page(self):
    self._query_page += 1
    self.print_query_result()

  def test(self):
    self._test += 1
    return str(self._test)

  def execute(self, context, data):
    params = [x.strip().lower() for x in data.split(',')]

    if (not self.is_logged_in) and params[0] != "login":
      try:
        file = open("uname.txt", "r")
        file.close()
      except FileNotFoundError:
        pass
        #return "LOGIN FIRST"

    if self.is_logged_in:
      pass
      #TODO: Check if token expired and refresh if so

    cmd = 'self.' + params[0] + '(' + ','.join(params[1:]) + ')'

    #TODO: tryexcept (ERR-FAIL)
    return eval(cmd)
  
  def play_track_emotion(self, emotion):
    # takes as input a string from one of the emotions
    # returns None if emotion is not known
    # plays a song with that mood if emotion is known returns
    emotion = str(emotion).upper()  
    emotion_list = ["HAPPY", "SAD", "RELAX", "ANGRY", "SLEEP", "ENERGETIC", "STUDY"]
    
    if emotion not in emotion_list:
        return "EMOTIONFAIL"

    else:
    
        options = {"HAPPY" : ("self._sp.start_playback(None, 'spotify:playlist:37i9dQZF1DWSf2RDTDayIx')", "What do you think of this song?")
                ,"SAD" : ("self._sp.start_playback(None, 'spotify:playlist:54ozEbxQMa0OeozoSoRvcL')", "What do you think of this song?")
                ,"RELAX" : ("self._sp.start_playback(None, 'spotify:playlist:0RD0iLzkUjrjFKNUHu2cle')", "What do you think of this song?")
                ,"ANGRY" : ("self._sp.start_playback(None, 'spotify:playlist:6ft4ijUITtTeVC0dUCDdvH')", "What do you think of this song?")
                ,"SLEEP" : ("self._sp.start_playback(None, 'spotify:playlist:37i9dQZF1DWStLt4f1zJ6I')", "What do you think of this song?")
                ,"ENERGETIC" : ("self._sp.start_playback(None, 'spotify:playlist:0gFLYrJoh1tLxJvlKcd5Lv')", "What do you think of this song?")
                ,"STUDY" : ("self._sp.start_playback(None, 'spotify:playlist:37i9dQZF1DX9sIqqvKsjG8')", "What do you think of this song?")
                }
        cmd, mess = options[emotion]
        self._sp.shuffle(True, device_id=None)
        exec(cmd)
        return "EMOTIONOK"
  
  def play_track_positiviy(self, score):
    score = float(score)

    if score < -0.9:
        mood = 'EXTREMELY NEGATIVE'
    if score > -0.9 and score <= -0.7:
        mood = 'VERY NEGATIVE'
    if score > -0.7 and score <= -0.5:
        mood = 'QUITE NEGATIVE'
    if score > -0.5 and score <= -0.3:
        mood =  'NEGATIVE'
    if score > -0.3 and score <= -0.1:
        mood = 'SOMEWHAT NEGATIVE'
    if score > -0.1 and score <= 0.1:
        mood = 'NEUTRAL'
    if score > 0.1 and score <= 0.3:
        mood = 'SOMEWHAT POSITIVE'
    if score > 0.3 and score <= 0.5:
        mood = 'POSITIVE'
    if score > 0.5 and score <= 0.7:
        mood = 'QUITE POSITIVE'
    if score > 0.7 and score <= 0.9:
        mood = 'VERY POSITIVE'
    if score > 0.9:
        mood = 'EXTREMELY POSITIVE'

    print('You seem {}'.format(mood))
    if score < 0:
        self._sp.shuffle(True, device_id=None)
        self._sp.start_playback(None, 'spotify:playlist:7HCXp5mTEkbwb9hYq2JTmO') # starts playing a song from a negative playlist
        print('This is a song from a Sad-playlist')
        return "POSITIVITYOK"
    elif score > 0.1:
        self._sp.shuffle(True, device_id=None)
        self._sp.start_playback(None, 'spotify:playlist:37i9dQZF1DWUAZoWydCivZ') # starts playing a song from a positive
        print('This is a song from a Positive-playlist')
        return "POSITIVITYOK"
    else:
        self._sp.shuffle(True, device_id=None)
        self._sp.start_playback(None, 'spotify:playlist:0RD0iLzkUjrjFKNUHu2cle') # starts playing a song from the Relax playlist
        print('This is a song from a Relax-playlist')
        return "POSITIVITYOK"
