import os
import sys
import time

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

from programy.utils.logging.ylogger import YLogger

class SpotifySession():
  ########
  # INIT #
  ########
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


  ########
  # HELP #
  ########
  def help(self):
    print("Hello I am SpotBot.")
    print("I am able to have a conversation with you and control your Spotify.")
    print("Before you can use my full capabilities you first need to login.")

  def help_login(self):
    print("I you have not logged in yet, you can either type in  \"login\",")
    print("I will then ask for you Spotify username with which you can reply: \"my username is [username]\" or \"my spotify username is [username]\".")
    print("Or you spare yourself some typing and type: \"login [spotify username]\".")
    print("If the username provided is already registered with me I will take care of the rest.")
    print("If not, I will direct you to your browser in which you need to give me permission to control your Spotify.")
    print("When you have given the permission, you will be directed to a webpage that does not seem to work, however I only need the link of that page.")
    print("You will be prompted to give me an url, it is this url you need to give.")
    print("When this is done, all should be ok and I will be able to control your Spotify for you.")

  def help_functions(self):
    print("My main aim is to hold a conversation with you to assist you with Spotify.")
    print("If you are logged in I can control your Spotify. I can...")
    print("-Play/Resume your Spotify.")
    print("-Pause your Spotify.")
    print("-Skip to the next track.")
    print("-Go back to the previous track.")
    print("-Rewind to the start of the track.")
    print("-Turn shuffle on and off.")
    print("-Set repeat to track, context or off.")
    print("-Save the track you are currently listening to.")
    print("-Find a track, album, artist or playlist for you. \n    You can then choose which item you want to play from a list of results.")
    print("-Play a track, album, artist or playlist for you.")
    print("-Tell you to which song you are currently listening.")
  

  #########
  # LOGIN #
  #########
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

  def logout(self, uname, all=0):
    saved_uname = "_"
    try:
      with open('uname.txt', 'r') as file:
        saved_uname = file.read()
    except:
      pass

    if (uname == saved_uname):
      try:
        os.remove('uname.txt')
        print(os.getcwd())
        os.remove('.cache-' + uname.strip())
      except Exception as fail:
        print(fail)
        #pass
      
      if (all == 1):
        try:          
          import webbrowser
          webbrowser.open("https://www.spotify.com/nl/account/apps/")
          print("Login on the user you want to remove, and remove me from the authorized apps.")
          return "PYOK LOGOUT ALL"
        except Exception as fail:
          return "PYFAIL LOGOUT BROWSER https://www.spotify.com/nl/account/apps/"     
      return "PYOK LOGOUT"

    else:
      return "PYOK LOGOUT ALREADYLOGGEDOUT"


  #########################
  # BASIC SPOTIFY CONTROL #
  #########################
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

  def rewind(self):
    self._sp.seek_track(0)
    return "PYOK PLAYB"

  def shuffle(self, state):
    stb = state == "on"
    self._sp.shuffle(stb)
    return "PYOK SHUFFLE " + state.upper()

  def repeat(self, state):
    self._sp.repeat(state)
    return "PYOK REPEAT " + state.upper()

  def change_volume(self, increase=0, step=10):
    curr_playback = self._sp.current_playback()
    new_volume = curr_playback['device']['volume_percent']
    new_volume = new_volume - step if increase == 0 else new_volume + step 
    return(self.set_volume(new_volume))

  def set_volume(self, volume):
    volume = float(volume)
    if 0 < volume < 1:
      volume = volume * 100
    if volume > 100:
      volume = 100
    elif volume < 0:
      volume = 0
    volume = int(volume)
    self._sp.volume(volume)
    return "PYOK VOLUME " + str(volume)


  ###################################
  # CURRENT PLAYBACK & SAVED TRACKS #
  ###################################
  def current_playback(self):
    playing = self._sp.current_playback()
    name = playing['item']['name']
    artist = playing['item']['artists'][0]['name']
    return "PYOK CURRPLAYB " + name + " by " + artist

  def is_curr_on_saved(self):
    curr_track = self._sp.current_playback()
    is_on_saved = self._sp.current_user_saved_tracks_contains(curr_track['item']['uri'])
    if is_on_saved:
      return "PYOK ISONSAVED YES"
    else:
      return "PYOK ISONSAVED NO"

  def add_curr_to_saved(self):
    curr_track = self._sp.current_playback()
    self._sp.current_user_saved_tracks_add(curr_track['item']['uri'])
    return "PYOK ADDTOSAVED " + curr_track['item']['name'] + " by " + curr_track['item']['artists'][0]['name']

  def remove_curr_from_saved(self):
    curr_track = self._sp.current_playback()
    self._sp.current_user_saved_tracks_delete(curr_track['item']['uri'])
    return "PYOK REMOVEFROMSAVED " + curr_track['item']['name'] + " by " + curr_track['item']['artists'][0]['name']


  #####################
  # FIND & PLAY SONGS #
  #####################
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

  
  #####################
  # EMOTION FUNCTIONS #
  #####################
  def play_track_emotion(self, emotion):
    '''
      Takes as input a string from one of the emotions.
      Returns None if emotion is not known.
      Plays a song with that mood if emotion is known returns.
    '''
    
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
        exec(cmd)
        self.shuffle("on")
        self.next_track()
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
    if score < -0.1:
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

  ###################
  # RECOMMENDATIONS #
  ###################
  def recommendations(self, genre = None):
    if genre is None:
      dic = self._sp.recommendation_genre_seeds()
      for element in dic['genres']:
        print(element.strip("'"), end='')
        print(' - ', end='')
      print('/n')
      return
    else:
      dic = self._sp.recommendation_genre_seeds()
      print(genre)
      track = self._sp.recommendations(None, ['soul'])
      self._sp.start_playback(track)
      print(track)
      return 'hoi'

  ########
  # TEST #
  ########
  def test(self):
    self._test += 1
    return str(self._test)
