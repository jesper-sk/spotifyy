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

    self._query_limit = 20

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


  ########
  # HELP #
  ########
  def help(self):
    print("Hello I am SpotBot.")
    print("I am able to have a conversation with you and control your Spotify.")
    print("In all the help functions I will refer to commands you can give to me between brackets, like [pause].")
    print("")
    print("For me to work optimally I want you to be a friendly person and always speak in multiple words, except when I ask very specific questions like yes/no-questions.")
    print("If I still don't understand you, you may need to be more specific in your answer, e.g.:")
    print("me: Do you have a specific genre in mind?")
    print("you: [The genre is [name of the genre]]")
    print("")
    print("You can use [what can I do with [name of topic]] for certain topics to get more information about that topic. I can help you with the following topics:")
    print("-[functions]: This shows you information about most of my commands.")
    print("-[playback]:  This shows you information about my playback functions.")
    print("-[volume]:    This shows you information about my volume functions.")
    print("-[shuffle]:   This shows my shuffle options.")
    print("-[repeat]:    This shows my repeat options.")
    print("-[current]:   This shows my functions regarding your current playback.")
    print("-[find]:      This shows information about how to use my find function.")
    print("-[play]:      This shows information about how to use my play function.")
    print("-[enqueue]:   This shows information about how to enqueue items to your queue.")
    print("-[device]     This shows information about how to select your playback device. This however does not work always as good as I want but I blame Spotify for this.")
    print("")
    print("I can understand many versions of everything you tell me, but bear with me if I do not understand you right away.")
    print("")
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
    print("- [play] / [resume] / [pause] your Spotify.")
    print("- [skip] to the [next track].")
    print("- Go back to the [previous track].")
    print("- [rewind] to the start of the track.")
    print("- Turn [shuffle on] and [shuffle off].")
    print("- Set [repeat] to track, context or off.")
    print("- Ask for the [currently playing] track and ask [is current track saved].")
    print("- You can then [add current to saved] or [remove current from saved]")
    print("- I can [find track [name of track]], find you an album, artist or playlist in the same way.")
    print("- I can also [play track [name of track]], or play an album, artist or playlist in the same way too.")
    print("- You can also [enqueue [name of track]], however this only works with tracks.")
    print("- Setting your playback device is also possible, but Spotify does not quite like that sometime.")
    print("     This can be done by asking your [current device] or [select device]")
    print("")
    print("Each time I show you a list of items you can type [item [item number]] to select an item.")
    print("You can often ask for [more items].")
    print("You can also [query nextpage] or [query prevpage] to navigate the pages.")
    print("")
    print("Since I am a very sentimental bot, you can also talk about your feelings with me.")
    print("I can also make you recomendations, this can be done in several ways.")
    print("[can you make me a recommendation] is my preferred way of giving you recommendations.")
    print("Or you can ask [play me a recommendation] if you want to listen to a recommendation right away.")


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
    print("You can also enqueue items by typing [enqueue item [name of the item]], however this only works with tracks.")


  #########
  # LOGIN #
  #########
  def login(self, uname=""):
    '''
    Used to login a user into the Spotify API.
    
    Parameters:
      - uname - User name to log in, if not specified this function tries to login an already saved username.

    Returns:
      - "PYFAIL LOGIN NONAME" - No username was provided and no username was saved.
      - "PYFAIL LOGIN" - Something went wrong trying to log the user in.
      - "PYOK LOGIN" - User is logged in succesfully.
    '''
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
    '''
      Used to logout a user from the Spotify API.

      Parameters:
        - uname - The username to logout.
        - all - 0 to just remove the user locally, 1 to open Spotify to all the user to remove Spotbot as authorized app.

      Returns:
        - "PYFAIL" - Something went wrong.
        - "PYOK LOGOUT" - User was logged out succesfully.
    '''
    saved_uname = "_"
    try:
      with open('uname.txt', 'r') as file:
        saved_uname = file.read()
    except:
      pass

    if (uname == saved_uname):
      try:
        os.remove('uname.txt')
        os.remove('.cache-' + uname.strip())
      except Exception as fail:
        return "PYFAIL " + fail
      
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
    '''
      Checks if the current token used to interact with the Spotify is still useful.
      (A token expires after 3600 seconds)

      Returns:
        - True - Token is expired.
        - False - Token is still valid.
    '''
    res = (datetime.datetime.now() - self._token_time).seconds >= 3600
    if res:
      self.is_logged_in = False
    return res

  ##############################
  # DEVICE CONTROL & SELECTION #
  ##############################
  def current_device(self):
    '''
      Returns: 
        - "PYOK CURRDEVICE NONE" - No current device detected.
        - "PYOK CURRDEVICE [device_name]" - Current device detected and the name of it.
    '''
    if not self._device:
      return "PYOK CURRDEVICE NONE"
    return f"PYOK CURRDEVICE {self._device['name']}"


  def refresh_print_devices(self):
    '''
      Refreshes the available playback devices and prints them.

      Returns:
        - "PYOK DEVICESREFRESH [number of availble devices]" - Devices refreshed succesfully and the number of currently available devices.
    '''
    self._available_devices = self._sp.devices()['devices']
    n = len(self._available_devices)
    if n > 1:
      print('\n'.join([f"{index+1}: {x['name']} ({x['type']})" for (index, x) in enumerate(self._available_devices)]))
    return f"PYOK DEVICESREFRESH {n}"


  def set_device(self, index=-1):
    '''
      Used to set the playback device for Spotify.

      Parameters:
        - index - The index of the avaible playback devices to set as active.

      Returns:
        - "PYOK SETDEVICE NONE" - Current active device set to no device.
        - "PYFAIL SETDEVICE OUTOFRANGE [number of available devices]" - The item to select is not in the rang of the amount of available devices.
        - "PYOK SETDEVICE [device name]" - The currently active playback device is succesfully set and its name.
    '''
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
    '''
      Sets the playback device to the default.

      Returns:
        - The return value of set_device() -
    '''
    return self.set_device()


  #########################
  # BASIC SPOTIFY CONTROL #
  #########################  
  def play(self):
    '''
      Resumes the Spotify playback.

      Returns:
        - "PYOK PLAYB" - Playback succesfully changed.
    '''
    self._sp.start_playback(self._device_id)
    return "PYOK PLAYB"


  def pause(self):
    '''
      Pauses the Spotify playback.

      Returns:
        - "PYOK PAUSE" - Playback succesfully paused.
    '''
    self._sp.pause_playback(self._device_id)
    return "PYOK PAUSE"


  def next_track(self):
    '''
      Sets the Spotify playback to the next track.

      Returns:
        - "PYOK PLAYB" - Playback succesfully changed.
    '''
    self._sp.next_track(self._device_id)
    return "PYOK PLAYB"


  def prev_track(self):
    '''
      Sets the Spotify playback to the previous track.

      Returns:
        - "PYOK PLAYB" - Playback succesfully changed.
    '''
    self._sp.previous_track(self._device_id)
    return "PYOK PLAYB"


  def rewind(self):
    '''
      Sets the Spotify playback to the start of the current playing track.

      Returns:
        - "PYOK PLAYB" - Playback succesfully changed.
    '''
    self._sp.seek_track(0)
    return "PYOK PLAYB"


  def shuffle(self, state):
    '''
      Sets the shuffle state of Spoitfy to a new state.
      Parameters:
        - state - "on" or "off"

      Returns:
      - "PYOK SHUFFLE [new state]" - Shuffle state succesfully changed to new state and the new state name.
    '''
    stb = state == "on"
    self._sp.shuffle(stb, self._device_id)
    return "PYOK SHUFFLE " + state.upper()


  def repeat(self, state):
    '''
      Sets the repeat state of Spotify to a new state.
      
      Parameters:
        - state - "track", "context" or "off"

      Returns:
      - "PYOK PLAYB" - Playback succesfully changed.
    '''
    self._sp.repeat(state, self._device_id)
    return "PYOK REPEAT " + state.upper()


  def change_volume(self, increase=0, step=10):
    '''
      Used to change the Spotify playback volume with a certain value.

      Parameters:  
        - increase - 0 to decrease the volume, 1 to increase the volume.  
        - step - percentage (in full percent or as floating point value between 0-1) to de- or increase the volume with.

      Returns:
      - "PYOK VOLUME [new volume value]" - Volume succesfully changed and the new volume percentage.
    '''
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
    if new_volume > 100:
      new_volume = 100
    elif new_volume < 0:
      new_volume = 0
    return(self.set_volume(new_volume))


  def set_volume(self, volume):
    '''
      Used to set the Spotify playback volume to a certain value.

      Parameters:  
        - volume - The new volume percentage (in full percent or as floating point value between 0-1).

      Returns:
      - "PYOK VOLUME [new volume value]" - Volume succesfully set and the new volume percentage.
    '''
    volume = float(volume)
    if 0 < volume < 1:
      volume = volume * 100
    if volume > 100:
      volume = 100
    elif volume < 0:
      volume = 0
    volume = int(volume)
    self._sp.volume(volume, self._device_id)
    return "PYOK VOLUME " + str(volume)


  ###################################
  # CURRENT PLAYBACK & SAVED TRACKS #
  ###################################
  def current_playback(self):
    '''
      Gets the currently playing track on Spotify.

      Returns:
        - "PYOK CURRPLAYB [name of track] by [name of artist]" -
	  '''
    playing = self._sp.current_playback()
    name = playing['item']['name']
    artist = playing['item']['artists'][0]['name']
    return "PYOK CURRPLAYB " + name + " by " + artist


  def is_curr_on_saved(self):
    '''
      Gets if the currently playing track is saved in the users Spotify Music Library.

      Returns:
        - "PYOK ISONSAVED YES" - The currently playing track is saved in the users Spotify Music Library,
        - "PYOK ISONSAVED NO" - The currently playing track is not saved in the users Spotify Music Libary.
	  '''
    curr_track = self._sp.current_playback()
    is_on_saved = self._sp.current_user_saved_tracks_contains([curr_track['item']['uri']])
    if is_on_saved:
      return "PYOK ISONSAVED YES"
    else:
      return "PYOK ISONSAVED NO"


  def add_curr_to_saved(self):
    '''
      Adds the currently playing track to the users Spotify Music Library.

      Returns:
        - "PYOK ADDTOSAVED [name of track] by [name of artist]" - The currently playing track is succesfully added to the users Spotify Music Library.
	  '''
    curr_track = self._sp.current_playback()
    self._sp.current_user_saved_tracks_add([curr_track['item']['uri']])
    return "PYOK ADDTOSAVED " + curr_track['item']['name'] + " by " + curr_track['item']['artists'][0]['name']


  def remove_curr_from_saved(self):
    '''
      Removes the currently playing track from the users Spotify Music Library.

      Returns:
        - "PYOK REMOVEFROMSAVED [name of track] by [name of artist]" - The currently playing track is succesfully removed from the users Spotify Music Library.
	  '''
    curr_track = self._sp.current_playback()
    self._sp.current_user_saved_tracks_delete([curr_track['item']['uri']])
    return "PYOK REMOVEFROMSAVED " + curr_track['item']['name'] + " by " + curr_track['item']['artists'][0]['name']


  ######################
  # FIND & PLAY TRACKS #
  ######################
  def play_from_query(self, index=-1):
    '''
      Plays an item from the currently saved query results.  
      To prevent the Spotify of stopping playback after playing one track,  
      this function enqueues a track to the users queue and immediately skips to it.  
      If the index is greater than the amount of available items, the playback is just set to the next track.

      Parameters:
        - index - The index of the item to play.

      Returns:
        - "PYOK PLAY [name of item] by [name of owner of item]" - Succesfully started playback of the requested item.
	  '''
    if index > 0:
      self._query_index = int(index) - 1 # Humans are 1-based.
    
    if self._query_index >= self._query_nresults:
      return self.next_track()

    if self._query_kind == "track":
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
    '''
      Adds an item to the playback queue of the user.         

      Parameters:
        - index - The index of the track to enqueue.
        - play - 0 to just enqueue the track, 1 to immediately start playing this track.

      Returns:
        - "PYOK ENQUEUE [name of track] by [name of artist]" - Succesfully enqueued the track.
        - "PYOK PLAY [name of track] by [name of artist]" - Succesfully started playback of the track.

        !!! This function can only enqueue tracks due to the Spotify API !!!
	  '''
    if self._query_kind != "track":
      return "PYFAIL ENQUEUE INVALIDTYPE"

    if index > 0:
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
    '''
      Plays the next item from the currently saved query results.

      Returns:
        - The return value of play_from_query() - 
	  '''
    return self.play_from_query(index=self._query_index+2)


  def find(self, query, kind, offset=0, limit=10, play=0, enqueue=0):
    '''
      Uses Spotify's search function to find items from a query.  
      A kind is needed for the search function to specify the kind of items to search for.  

      Find can either return a list of the results, enqueue the result (if it is a track), or immediately start playing the results.    

      Parameters:
        - query - The search query.
        - kind - The type of item to search for. "track", "album", "artist" or "playlist".
        - offset - The index of the first item to return.
        - limit - The amount of items to search for.
        - play - 0 to do nothing, 1 to immediately start playing the first result.
        - enqueue - 0 to do nothing, 1 to enqueue the stop result (if it is a track).

      Returns:
        - "PYFAIL FIND INVALIDTYPE [provided type]" - Provided type is not a valid item type.
        - "PYFAIL FIND NORESULTS" - No results were found.
        - "PYOK FIND [number of results found]" - 
        - A return value of play_from_query() - If play == 1
        - A return value of enqueue_from_query() - If enqueue == 1- 
	  '''
    kind = kind.strip()
    if not (kind in ["track", "album", "artist", "playlist"]):
      return "PYFAIL FIND INVALIDTYPE " + kind

    self._query_limit = limit
    self._query_index = 0
    self._query_kind = kind
    self._query = query
    self._offset = offset
    self._query_page = 0

    q = self._sp.search(query, type=kind, limit=self._query_limit)
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
    '''
      Prints 5 query results, the indices of these results are [page*5:(page+1)*5]

      Parameters:
        - page - Which 'page' of results to show. If not provided the last printed page will be printed again.

      Returns:
        - "PYOK NOMORERESULTS" - No more results to show on the provided page.
        - "PYOK PRINTRESULTS" - All results from provided page are printed.
    '''
    if page == -1:
      page = self._query_page
      
    start = page*5

    end = start + 5
    if end > self._query_nresults:
      end = self._query_nresults
      if start == end:
        return "PYOK NOMORERESULTS"

    if self._query_kind == "playlist":
      print('\n'.join([str((index+1)+(page*5)) + ': ' + x['name'] + ", owned by " + x['owner']['display_name'] 
        for (index, x) in enumerate(self._query_results[start:end])]))

    elif self._query_kind == "artist":
      print('\n'.join([str((index+1)+(page*5)) + ': ' + x['name']
        for (index, x) in enumerate(self._query_results[start:end])]))

    else:
      print('\n'.join([str((index+1)+(page*5)) + ': ' + x['name'] + " by " + x['artists'][0]['name'] 
        for (index, x) in enumerate(self._query_results[start:end])]))

    return "PYOK PRINTRESULTS"


  def print_next_query_page(self):
    '''
      Prints the next page of results.

      Returns:
        - A return value of print_query_result() -
    '''
    self._query_page += 1
    return self.print_query_result()


  def print_prev_query_page(self):
    '''
      Prints the previous page of results.

      Returns:
        - A return value of print_query_result() -
    '''
    self._query_page -= 1
    if self._query_page < 0:
      self._query_page = 0
      return "PYFAIL NEGATIVEPAGE"
    return self.print_query_result()

  
  #####################
  # EMOTION FUNCTIONS #
  #####################
  def calm_down(self):
    '''
      Called when the user needs to calm down because it used profanity or other bad language.  
      To cool the user down, a random song of the chill playlist will be played.

      Returns:
        - "PYOK COOLDOWN" - Playback of a calming song was succesfull.
    '''
    self._sp.start_playback(context_uri='spotify:playlist:37i9dQZF1DWSf2RDTDayIx')
    self.shuffle("on")
    self.next_track()
    return "PYOK COOLDOWN"


  def play_track_emotion(self, emotion):
    '''
      Takes as input a string from one of the emotions.  

      Parameters:
        - emotion - The emotion of the user, used to pick a suitable playlist.
      
      Returns:
        - "PYFAIL EMOTION" - Emotion is not a valid emotion.
        - "PYOK EMOTION" - Emotion was found and the playback of a suitable playlist has been started.
    '''
    emotion = str(emotion).upper()  
    emotion_list = ["HAPPY", "SAD", "RELAX", "ANGRY", "SLEEP", "ENERGETIC", "STUDY", "PARTY", "CHILL", "LOVESICK", "HOLIDAY", "ROADTRIP" ]
    
    if emotion not in emotion_list:
        return "PYFAIL EMOTION"

    else:
        options = {"HAPPY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DWSf2RDTDayIx')", "What do you think of this track?")
                  ,"SAD" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:54ozEbxQMa0OeozoSoRvcL')", "What do you think of this track?")
                  ,"RELAX" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:0RD0iLzkUjrjFKNUHu2cle')", "What do you think of this track?")
                  ,"ANGRY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:6ft4ijUITtTeVC0dUCDdvH')", "What do you think of this track?")
                  ,"SLEEP" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DWStLt4f1zJ6I')", "What do you think of this track?")
                  ,"ENERGETIC" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:0gFLYrJoh1tLxJvlKcd5Lv')", "What do you think of this track?")
                  ,"STUDY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DX9sIqqvKsjG8')", "What do you think of this track?")
                  ,"PARTY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DX0IlCGIUGBsA')", "What do you think of this track?")
                  ,"CHILL" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DX4WYpdgoIcn6')", "What do you think of this track?")
                  ,"LOVESICK" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:6dm9jZ2p8iGGTLre7nY4hf')", "What do you think of this track?")
                  ,"HOLIDAY" : ("self._sp.start_playback(self._device_id, 'spotify:playlist:1KFOvnwqjeCpYTSC91wM4U')", "What do you think of this track?")
                  , "ROADTRIP": ("self._sp.start_playback(self._device_id, 'spotify:playlist:27LXgC5xD1s1vpB7E0pA3W')", "What do you think of this track?")
                  }
        cmd, mess = options[emotion]
        exec(cmd)
        self.shuffle("on")
        self.next_track()
        return "PYOK EMOTION"
  

  def play_track_positivity(self, score):
    '''
      Play a suitable track based on the postivity score measured by the sentiment module in the NLTK module.

      Parameters:
        - score - The positivity score of the conversation with the user.

      Returns:
        - "PYOK POSITIVITY" - A suitable playlist was found and the playback has been started.
    '''
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
        self._sp.start_playback(self._device_id, 'spotify:playlist:7HCXp5mTEkbwb9hYq2JTmO') # starts playing a track from a negative playlist
        print('This is a track from a Sad-playlist')
        return "PYOK POSITIVITY"
    elif score > 0.1:
        self._sp.shuffle(True, device_id=None)
        self._sp.start_playback(self._device_id, 'spotify:playlist:37i9dQZF1DWUAZoWydCivZ') # starts playing a track from a positive
        print('This is a track from a Positive-playlist')
        return "PYOK POSITIVITY"
    else:
        self._sp.shuffle(True, device_id=None)
        self._sp.start_playback(self._device_id, 'spotify:playlist:0RD0iLzkUjrjFKNUHu2cle') # starts playing a track from the Relax playlist
        print('This is a track from a Relax-playlist')
        return "PYOK POSITIVITY"


  ###################
  # RECOMMENDATIONS #
  ###################
  def recommend(self, query="", kind="track", limit=20, play=0):
    '''
      Finds recommended tracks based on the query and kind provided.  
      It can either print the results to let the user pick a track or start playing the results immediately.

      Parameters:
        - query - A 'track', an 'artist' or a 'playlist' to use as reference for the recommendation function.
        - kind - The type of query that is given.
        - limit - The amount of items to recommend.
        - play - 0 to print the results. 1 to start playing them immediately.

      Returns:
        - "PYFAIL RECOMMEND INVALIDTYPE" - The type of recommendation reference is not a valid type.
        - "PYFAIL RECOMMEND NORESULTS" - No recommendations could be found. Make sure the reference is not too specific.
        - "PYOK PLAY [name of track] by [name of artist]" - Playback of first recommendation has been started succesfully.
        - "PYOK FIND [number of recommendations]" - Recommendations have been succesfully found and the number of recommendations.
    '''
    kind = kind.strip()
    if not (kind in ["track", "artist", "genre"]):
      return "PYFAIL RECOMMEND INVALIDTYPE " + kind

    self._query_limit = limit

    self._query_index = 0
    self._query_kind = "track"
    self._query = ""
    self._offset = 0
    self._query_page = 0

    if query == "":
      top_tracks = self._sp.current_user_top_tracks(limit=5, time_range="short_term")
      tracks = self._sp.recommendations(seed_tracks=[x['uri'] for x in top_tracks['items'][:5]], limit=self._query_limit)

    elif kind == "artist":
      found_artist = self._sp.search(query.strip(), limit=1, type="artist")
      if len(found_artist['artists']['items']) > 0:       
        tracks = self._sp.recommendations(seed_artists=[found_artist['artists']['items'][0]['id']], limit=self._query_limit)
      else:
        return "PYFAIL RECOMMEND NORESULTS"

    elif kind == "genre":
      possible_genres = self._sp.recommendation_genre_seeds()['genres']
      if query.strip() in possible_genres:
        tracks = self._sp.recommendations(seed_genres=[query.strip()], limit=self._query_limit)
      else:
        return "PYFAIL RECOMMEND GENREUNKNOWN"

    elif kind == "track":
      found_track = self._sp.search(query.strip(), limit=1, type="track")
      if len(found_track['tracks']['items']) > 0:
        tracks = self._sp.recommendations(seed_tracks=[found_track['tracks']['items'][0]['id']], limit=self._query_limit)
      else:
        return "PYFAIL RECOMMEND NORESULTS"

    else:
      return "PYFAIL RECOMMEND NORESULTS"
    
    self._query_results = tracks['tracks']
    self._query_nresults = len(self._query_results)

    if self._query_nresults == 0:
      return "PYFAIL RECOMMEND NORESULTS"
    elif play:
      self._sp.start_playback(self._device_id, uris=[x['uri'] for x in self._query_results])
      return "PYOK PLAY " + self._query_results[0]['name'] + " by " + self._query_results[0]['artists'][0]['name']
    else:
      return "PYOK FIND " + str(self._query_nresults)


  def get_recommended_artists(self, ref_artist, play=0):
    '''
      This functions returns a list of recommended artists for a certain artist.  
      These artists correspond to the artists shown in "Fans Also Like" when viewing an artist in Spotify.  
      Most times this are 20 artists.

      A random related artist can be played immediately or all results can be returned.

      Parameters:
        - ref_artist - The reference artist to get related artists from.
        - play - 0 to print results, 1 to immediately start playing a random related artist.

      Returns:
        - "PYFAIL RECOMMENDARTIST ARTISTNOTFOUND [name of reference artist]" - The reference artist could not be found.
        - "PYFAIL RECOMMENDARTIST NORELATEDFOUND [name of reference artist]" - No related artists could be found for this reference artist.
        - "PYOK FIND [number of results]" - Related artists have been found succesfully and the number of results.
        - Return value from play_from_query() - When play == 1.
    '''
    ref_artist = str(ref_artist).strip()
    if ref_artist == "":
      return "PYFAIL RECOMMENDARTIST ARTISTNOTFOUND" + ref_artist

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
    '''
      For testing purposes only

        !!! DO NOT USE UNLESS YOU KNOW WHAT YOU ARE DOING !!!
        !!! ALSO, DO NOT DELETE, THIS WILL BREAK THE CODE !!!
    '''
    return "PYOK"