from sclib import SoundcloudAPI, Track, Playlist
import telebot
from telebot import types
from datetime import datetime
import configparser
import os, shutil
import colorama as cl
from tqdm import tqdm, trange
        
cl.init(autoreset=True)
timestamp = datetime.now().strftime('%H:%M:%S')
tag_info = cl.Fore.LIGHTCYAN_EX + "[INFO]"
tag_warn = cl.Fore.LIGHTYELLOW_EX + "[WARN]"
tag_error = cl.Fore.LIGHTRED_EX + "[ERROR]"
tag_fatal = cl.Fore.LIGHTMAGENTA_EX + "[FATAL]"
 
print(f"[{timestamp}]", tag_info, "Test INFO message...")
print(f"[{timestamp}]", tag_warn, "Test WARN message...")
print(f"[{timestamp}]", tag_error, "Test ERROR message...")
print(f"[{timestamp}]", tag_fatal, "Test FATAL message...")
print('='*50)

#Reading config file
try:
    print(f"[{timestamp}]", tag_info, "Initializing configuration...")
    config = configparser.ConfigParser()
    config.read('config.ini')
    TOKEN = config.get('default','token')
    CLIENTID = config.get('default','client_id')
except Exception as error:
    print(f"[{timestamp}]", tag_error, f"Cause: {error}")

#setting up a bot  
try:  
    print(f"[{timestamp}]", tag_info, "Initializing Telegram bot...")
    bot = telebot.TeleBot(TOKEN, parse_mode = 'markdown')
except Exception as error:
    print(f"[{timestamp}]", tag_error, f"Cause: {error}")

#connecting to Soundcloud API
try:
    print(f"[{timestamp}]", tag_info, "Connecting to Soundcloud API...")
    api = SoundcloudAPI(client_id=CLIENTID)
except Exception as error:
    print(f"[{timestamp}]", tag_error, f"Cause: {error}")
    

def clear_title(text: str,pattern: dict = {}) -> str:
    """this function clears filename string from forbidden characters if another pattern is not given and returns result as a string.

    Args:
        text (str): initial string to be cleared
        pattern (dict, optional): dictionary of "old": "new" pairs, where keys are substituted with meanings. Defaults to {}.

    Returns:
        str: clean string
    """
    forbidden_characters = {"/": "", "\\": "", ":": "", "*": "", "?": "", "<": "", ">": "", "|": ""}
    if pattern == {}:
        for old, new in forbidden_characters.items():
            text = text.replace(old, new)
    else:
        for old, new in pattern.items():
            text = text.replace(old, new)
    return text

def fetch_playlist(message, link_to_playlist: str):
    playlist = api.resolve(link_to_playlist)
    assert type(playlist) is Playlist
    
    #creation of the main folder
    path = f'./soundcloud'
    if not os.path.isdir(path):
        print(f"[{timestamp}]", tag_info, f"Creating {path} folder...")
        os.mkdir(path)
        
    #creation of the playlist folder
    path = f'./soundcloud/{playlist.title}'
    if not os.path.isdir(path):
        print(f"[{timestamp}]", tag_info, f"Creating {path} folder...")
        os.mkdir(path)

    #cycling throught playlist to download each track
    pbar = tqdm(playlist.tracks)
    for track in pbar:
        clear_title(track.title)
        trackname = f'{track.artist} - {track.title}.mp3'
        pbar.set_description(f'Downloading {trackname}')
        filename = f'{path}/{trackname}'
        try:
            with open(filename, 'wb+') as file:
                track.write_mp3_to(file)
                print(f"[{timestamp}]", tag_info, "Track is saved.")
                audio = open(filename, 'rb')
                bot.send_audio(message.chat.id, audio)
                print(f"[{timestamp}]", tag_info, "Track is sent to user.")
        except Exception as error:
            print(f"[{timestamp}]", tag_error, f"Cause: {error}")
    #shutil.rmtree(path)
    #print(f"[{timestamp}]", tag_info, f"Playlist {path} is cleared.")

def fetch_track(message, link_to_track: str):
    track = api.resolve(link_to_track)
    assert type(track) is Track
    #creation of the main folder
    path = f'./soundcloud'
    if not os.path.isdir(path):
        print(f"[{timestamp}]", tag_info, f"Creating {path} folder...")
        os.mkdir(path)
    #creation of the tracks folder
    path = f'./soundcloud/tracks'
    if not os.path.isdir(path):
        print(f"[{timestamp}]", tag_info, f"Creating {path} folder...")
        os.mkdir(path) 
    clear_title(track.title)
    trackname = f"{track.artist} - {track.title}.mp3"
    filename = f'{path}/{trackname}'
    try:
        with open(filename, 'wb+') as file:
            track.write_mp3_to(file)
            print(f"[{timestamp}]", tag_info, "Track is saved.")
            audio = open(filename, 'rb')
            bot.send_audio(message.chat.id, audio)
            print(f"[{timestamp}]", tag_info, "Track is sent to user.")
    except Exception as error:
        print(f"[{timestamp}]", tag_error, f"Cause: {error}")
        if "cannot be downloaded" in str(error):
            bot.send_message(message.chat.id, f"Unfortunately, track {trackname} is not marked as Downloadable and so cannot be downloaded.")

#desctibing bot's handlers
@bot.message_handler(commands = ['start'])
def start(message):
    text = f'''Greetings, {message.from_user.first_name}!
I'm bot that helps downloading tracks and full playlists from **Soundcloud**.
Just send me the corresponding Soundcloud link and I will reply with the audio message.
    
by Ewenn'''
    bot.send_message(message.chat.id, text)
                  
@bot.message_handler(commands = ['help'])
def help(message):
    text = '''Send me link to the song or playlist, and I will send you track here.
If error occur in the process - firstly make sure that the link is correct and the song is available.
After that please try and send the message again. If the error is still occurring, don't hesitate contacting me (@nmanshin)'''
    bot.send_message(message.chat.id, text)  
  
@bot.message_handler(content_types = ['text'])
def get_user_text(message):
    link = message.text
    result = api.resolve(link)
    if type(result).__name__ == "Playlist":
        fetch_playlist(message, link)
    elif type(result).__name__ == "Track":
        fetch_track(message, link)
    else:
        bot.send_message(message.chat.id, 'I dont know what is this link for.\nPlease try another one.')  

          

print(f"[{timestamp}]", tag_info, "Bot Started...")
try:
    bot.infinity_polling()
except Exception as error:
    print(f"[{timestamp}]", tag_error, f"Cause: {error}")
    
