import os
import sys
import time
import random
import datetime

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
    self._token_time = None
    self._test = 0

    self._query_results = None
    self._query_index = None
    self._query_kind = None
    self._query_buffer = str()
    self._query_nresults = None
    self._query_page = None

    self.is_logged_in = False
    self._username = None

    self._device = None
    self._device_id = None
    self._available_devices = None
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
    print("- Play/Resume your Spotify.")
    print("- Pause your Spotify.")
    print("- Skip to the next track.")
    print("- Go back to the previous track.")
    print("- Rewind to the start of the track.")
    print("- Turn shuffle on and off.")
    print("- Set repeat to track, context or off.")
    print("- Save the track you are currently listening to.")
    print("- Find a track, album, artist or playlist for you. \n    You can then choose which item you want to play from a list of results.")
    print("- Play a track, album, artist or playlist for you.")
    print("- Tell you to which song you are currently listening.")

  def help_play_find(self):
    print("You can use the [play [query]] function to immediately play the top result found with your provided [query].")
    print("You can use the [find [query]] function to let me find you some results for the given query.")
    print("You will then able to pick the item you want using [item [item_number]]")
    print("I default to finding tracks unless you specify this earlier.")
    print("You can specify this using [play [item_type] [query]], [find [item_type] [query]], or [set type [item_type]]")
    print("The possible item types are:")
    print("- track")
    print("- album")
    print("- artist")
    print("- playlist")


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
        self._token_time = datetime.datetime.now()
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

  def is_token_expired(self):
    res = (datetime.datetime.now() - self._token_time).seconds >= 3600
    if res:
      self.is_logged_in = False
    return res

  ##############################
  # DEVICE CONTROL & SELECTION #
  ##############################
  def current_device(self):
    if not self._device:
      return "PYOK CURRDEVICE NONE"
    return f"PYOK CURRDEVICE {self._device['name']}"

  def refresh_print_devices(self):
    self._available_devices = self._sp.devices()['devices']
    n = len(self._available_devices)
    if n > 1:
      print('\n'.join([f"{index+1}: {x['name']} ({x['type']})" for (index, x) in enumerate(self._available_devices)]))
    return f"PYOK DEVICESREFRESH {n}"

  def set_device(self, index=-1):
    if index < 0:
      self._device = None
      self._device_id = None
      return "PYOK SETDEVICE NONE"

    index-=1 #Humans are 1-based

    self._available_devices = self._sp.devices()['devices']
    if index >= len(self._available_devices):
      return f"PYFAIL SETDEVICE OUTOFRANGE {len(self._available_devices)}"     
    else:
      self._device = self._available_devices[index]
      self._device_id = self._device['id']
      return f"PYOK SETDEVICE {self._device['name']}"
  
  def reset_device(self):
    return self.set_device()


  #########################
  # BASIC SPOTIFY CONTROL #
  #########################
  def play(self):
    self._sp.start_playback(self._device_id)
    return "PYOK PLAYB"

  def pause(self):
    self._sp.pause_playback(self._device_id)
    return "PYOK PAUSE"

  def next_track(self):
    self._sp.next_track(self._device_id)
    return "PYOK PLAYB"

  def prev_track(self):
    self._sp.previous_track(self._device_id)
    return "PYOK PLAYB"

  def rewind(self):
    self._sp.seek_track(0)
    return "PYOK PLAYB"

  def shuffle(self, state):
    stb = state == "on"
    self._sp.shuffle(stb, self._device_id)
    return "PYOK SHUFFLE " + state.upper()

  def repeat(self, state):
    self._sp.repeat(state, self._device_id)
    return "PYOK REPEAT " + state.upper()

  def change_volume(self, increase=0, step=10):
    step = int(str(step).strip())
    if 0 < step < 1:
      step = step * 100
    if step > 100:
      step = 100
    elif step < 0:
      step = 0
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
    is_on_saved = self._sp.current_user_saved_tracks_contains([curr_track['item']['uri']])
    if is_on_saved:
      return "PYOK ISONSAVED YES"
    else:
      return "PYOK ISONSAVED NO"

  def add_curr_to_saved(self):
    curr_track = self._sp.current_playback()
    self._sp.current_user_saved_tracks_add([curr_track['item']['uri']])
    return "PYOK ADDTOSAVED " + curr_track['item']['name'] + " by " + curr_track['item']['artists'][0]['name']

  def remove_curr_from_saved(self):
    curr_track = self._sp.current_playback()
    self._sp.current_user_saved_tracks_delete([curr_track['item']['uri']])
    return "PYOK REMOVEFROMSAVED " + curr_track['item']['name'] + " by " + curr_track['item']['artists'][0]['name']


  #####################
  # FIND & PLAY SONGS #
  #####################
  def play_from_query(self, index=-1):
    if index >= 0:
      self._query_index = int(index) - 1

    if self._query_kind == "track":
      #self._sp.start_playback(device_id=self._device_id, uris=[self._query_results[self._query_index]['uri']])
      self._sp.add_to_queue(device_id=self._device_id, uri=self._query_results[self._query_index]['uri'])
      self.next_track()
    else:
      self._sp.start_playback(device_id=self._device_id, context_uri=self._query_results[self._query_index]['uri'])


    name = self._query_results[self._query_index]['name']
    if self._query_kind == "artist":
      by = " "
    elif self._query_kind == "playlist":
      by = f", owned by {self._query_results[self._query_index]['owner']['id']}"
    else:
      by = f" by {self._query_results[self._query_index]['artists'][0]['name']}"

    return "PYOK PLAY " + name + by

  def enqueue_from_query(self, index=-1, play=0):
    if index >= 0:
      self._query_index = int(index) - 1

    track = self._query_results[self._query_index]
    self._sp.add_to_queue(device_id=self._device_id, uri=track['uri'])

    name = track['name']
    artist = track['artists'][0]['name']

    if play:      
      self.next_track()
      return "PYOK PLAY " + name + " by " + artist
    return "PYOK ENQUEUE " + name + " by " + artist

  def play_next_from_query(self):
    self.play_from_query(index=self._query_index+1)

  def find(self, query, kind, offset=0, limit=10, play=0, enqueue=0):
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
    if self._query_nresults == 0:
      return "PYFAIL FIND NORESULTS"

    if play and kind == "track":
      return self.enqueue_from_query(play=1)
    elif play:
      return self.play_from_query()
    elif enqueue:
      return self.enqueue_from_query()
    else:
      return "PYOK FIND " + str(self._query_nresults)

  def print_query_result(self, page=-1):
    if page == -1:
      page = self._query_page
      
    start = page*5

    end = start + 5
    if end > self._query_nresults:
      end = self._query_nresults
      if start == end:
        return "PYOK NOMORERESULTS"

    if self._query_kind == "playlist":
      print('\n'.join([str((index+1)+(page*5)) + ': ' + x['name'] + ", owned by " + x['owner']['id'] 
        for (index, x) in enumerate(self._query_results[start:end])]))

    elif self._query_kind == "artist":
      print('\n'.join([str((index+1)+(page*5)) + ': ' + x['name']
        for (index, x) in enumerate(self._query_results[start:end])]))

    else:
      print('\n'.join([str((index+1)+(page*5)) + ': ' + x['name'] + " by " + x['artists'][0]['name'] 
        for (index, x) in enumerate(self._query_results[start:end])]))

    return "PYOK PRINTRESULTS"

  def print_next_query_page(self):
    self._query_page += 1
    return self.print_query_result()

  def print_prev_query_page(self):
    self._query_page -= 1
    if self._query_page < 0:
      self._query_page = 0
      return "PYFAIL NEGATIVEPAGE"
    return self.print_query_result()

  
  #####################
  # EMOTION FUNCTIONS #
  #####################
  def calm_down(self):
    self._sp.start_playback(context_uri='spotify:playlist:37i9dQZF1DWSf2RDTDayIx')
    self.shuffle("on")
    self.next_track()
    return "PYOK COOLDOWN"

  def play_track_emotion(self, emotion):
    '''
      Takes as input a string from one of the emotions.
      Returns None if emotion is not known.
      Plays a song with that mood if emotion is known returns.
    '''
    
    emotion = str(emotion).upper()  
    emotion_list = ["HAPPY", "SAD", "RELAX", "ANGRY", "SLEEP", "ENERGETIC", "STUDY", "PARTY", "CHILL", "LOVESICK", "HOLIDAY", "ROADTRIP" ]
    
    if emotion not in emotion_list:
        return "EMOTIONFAIL"

    else:
        options = {"HAPPY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DWSf2RDTDayIx')", "What do you think of this song?")
                  ,"SAD" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:54ozEbxQMa0OeozoSoRvcL')", "What do you think of this song?")
                  ,"RELAX" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:0RD0iLzkUjrjFKNUHu2cle')", "What do you think of this song?")
                  ,"ANGRY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:6ft4ijUITtTeVC0dUCDdvH')", "What do you think of this song?")
                  ,"SLEEP" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DWStLt4f1zJ6I')", "What do you think of this song?")
                  ,"ENERGETIC" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:0gFLYrJoh1tLxJvlKcd5Lv')", "What do you think of this song?")
                  ,"STUDY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DX9sIqqvKsjG8')", "What do you think of this song?")
                  ,"PARTY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DX0IlCGIUGBsA')", "What do you think of this song?")
                  ,"CHILL" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DX4WYpdgoIcn6')", "What do you think of this song?")
                  ,"LOVESICK" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:6dm9jZ2p8iGGTLre7nY4hf')", "What do you think of this song?")
                  ,"HOLIDAY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:1KFOvnwqjeCpYTSC91wM4U')", "What do you think of this song?")
                  , "ROADTRIP": ("self._sp.start_playback(self._device_id, 'spotify:playlist:27LXgC5xD1s1vpB7E0pA3W')", "What do you think of this song?")
                  }
        cmd, mess = options[emotion]
        exec(cmd)
        self.shuffle("on")
        self.next_track()
        return "EMOTIONOK"
  
  def play_track_positivity(self, score):
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
        self._sp.start_playback(self._device_id, 'spotify:playlist:7HCXp5mTEkbwb9hYq2JTmO') # starts playing a song from a negative playlist
        print('This is a song from a Sad-playlist')
        return "POSITIVITYOK"
    elif score > 0.1:
        self._sp.shuffle(True, device_id=None)
        self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DWUAZoWydCivZ') # starts playing a song from a positive
        print('This is a song from a Positive-playlist')
        return "POSITIVITYOK"
    else:
        self._sp.shuffle(True, device_id=None)
        self._sp.start_playback(self._device_id, 'spotify:playlist:0RD0iLzkUjrjFKNUHu2cle') # starts playing a song from the Relax playlist
        print('This is a song from a Relax-playlist')
        return "POSITIVITYOK"


  ###################
  # RECOMMENDATIONS #
  ###################
  def get_artists_seed(self, artists):
    if artists == None or str(artists).strip() == "":
      return None
    else:
      artist_seed = []
      for artist in str(artists).split(';'):
        #print(artist)
        res = self._sp.search(artist.strip(), limit=1, type="artist")
        #print(res)
        if len(res['artists']['items']) > 0:
          artist_seed.append(res['artists']['items'][0]['id'])
        #artist_seed = artist_seed.append(res['artists']['items'][0]['id']) if len(res['artists']['items']) > 0 else artist_seed
      
      if len(artist_seed) == 0:
        return None
      else:
        return artist_seed

  def get_genres_seed(self, genres):
    if genres == None or str(genres).strip() == "":
      return None
    else:
      genre_seed = [genre.strip() for genre in str(genres).split(';')]
      if len(genre_seed) == 0:
        return None
      else:
        return genre_seed

  def get_tracks_seed(self, tracks):
    if tracks == None or str(tracks).strip() == "":
      return None
    else:
      track_seed = []
      for track in str(tracks).split(';'):
        res = self._sp.search(track.strip(), limit=1, type="track")
        if len(res['tracks']['items']) > 0:
          track_seed.append(res['tracks']['items'][0]['id'])
        #track_seed = track_seed.append(res['tracks']['items']['id']) if len(res['items']) > 0 else track_seed
      
      if len(track_seed) == 0:
        return None
      else:
        return track_seed


  def recommend(self, artists=None, genres=None, tracks=None, limit=20, play=0):
    artists_seed = self.get_artists_seed(artists)    
    genres_seed = self.get_genres_seed(genres)
    tracks_seed = self.get_tracks_seed(tracks)

    self._query_index = 0
    self._query_kind = "track"
    self._query = ""
    self._offset = 0
    self._query_page = 0

    tracks = self._sp.recommendations(seed_artists=artists_seed, seed_genres=genres_seed, seed_tracks=tracks_seed, limit=limit)
    self._query_results = tracks['tracks']

    self._query_nresults = len(self._query_results)
    if self._query_nresults == 0:
      return "PYFAIL RECOMMEND NORESULTS"
    elif play:
      self._sp.start_playback(self._device_id, uris=[x['uri'] for x in self._query_results])
      name = self._query_results[0]['name']
      artist = self._query_results[0]['artists'][0]['name']
      return "PYOK PLAY " +  name + " by " + artist
    else:
      return "PYOK FIND " + str(self._query_nresults)

  def get_recommended_artists(self, ref_artist, play=0):
    ref_artist = str(ref_artist).strip()
    found_artist = self._sp.search(ref_artist, limit=1, type="artist")

    if len(found_artist['artists']) == 0:
      return "PYFAIL RECOMMENDARTIST ARTISTNOTFOUND " + ref_artist

    self._query_index = 0
    self._query_kind = "artist"
    self._query = ""
    self._offset = 0
    self._query_page = 0

    found_artist = found_artist['artists']['items'][0]
    related_artists = self._sp.artist_related_artists(found_artist['id'])

    if len(related_artists['artists']) == 0:
      return "PYFAIL RECOMMENDARTIST NORELATEDFOUND " + ref_artist

    random.shuffle(related_artists)
    self._query_results = related_artists['artists']
    self._query_nresults = len(self._query_results)

    if play:
      return self.play_from_query()
    else:
      return "PYOK FIND " + str(self._query_nresults)


  ########
  # TEST #
  ########
  def test(self):
    self._test += 1
    return str(self._test)
