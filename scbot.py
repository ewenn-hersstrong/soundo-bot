#from sclib import SoundcloudAPI, Track, Playlist
from sclib.asyncio import SoundcloudAPI, Track, Playlist
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from datetime import datetime
import configparser
import os, shutil
import asyncio
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
    bot = AsyncTeleBot(TOKEN, parse_mode = 'markdown')
except Exception as error:
    print(f"[{timestamp}]", tag_error, f"Cause: {error}")

#connecting to Soundcloud API
try:
    print(f"[{timestamp}]", tag_info, "Connecting to Soundcloud API...")
    api = SoundcloudAPI(client_id='ovyZZ34xgflQFUDCXvS4D07GsPUibGLg')
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

async def fetch_playlist(message, link_to_playlist: str):
    playlist = await api.resolve(link_to_playlist)
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
        assert type(track) is Track
        clear_title(track.title)
        trackname = f'{track.artist} - {track.title}.mp3'
        pbar.set_description(f'Downloading {trackname}')
        filename = f'{path}/{trackname}'
        try:
            with open(filename, 'wb+') as file:
                await bot.send_chat_action(message.chat.id, 'record_audio')
                await track.write_mp3_to(file)
                print(f"[{timestamp}]", tag_info, "Track is saved.")
                audio = open(filename, 'rb')
                await bot.send_chat_action(message.chat.id, 'upload_audio')
                await bot.send_audio(message.chat.id, audio, caption = f"[Track Cover]({track.artwork_url}) | [Source]({track.permalink_url})", reply_to_message_id=message.message_id)
                print(f"[{timestamp}]", tag_info, "Track is sent to user.")
        except Exception as error:
            print(f"[{timestamp}]", tag_error, f"Cause: {error}")
            if "cannot be downloaded" in str(error):
                await bot.send_message(message.chat.id, f"Unfortunately, track {trackname} is not marked as Downloadable and so cannot be downloaded.")
    print(f"[{timestamp}]", tag_info, "Finished sending playlist.")
    shutil.rmtree(path)
    print(f"[{timestamp}]", tag_info, f"Playlist {path} is cleared.")

async def fetch_track(message, link_to_track: str):
    track = await api.resolve(link_to_track)
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
            await bot.send_chat_action(message.chat.id, 'record_audio')
            await track.write_mp3_to(file)
            print(f"[{timestamp}]", tag_info, "Track is saved.")
            audio = open(filename, 'rb')
            await bot.send_chat_action(message.chat.id, 'upload_audio')
            await bot.send_audio(message.chat.id, audio, caption = f"[Track Cover]({track.artwork_url}) | [Source]({track.permalink_url})", reply_to_message_id=message.message_id)
            print(f"[{timestamp}]", tag_info, "Track is sent to user.")
        os.remove(filename)
        print(f"[{timestamp}]", tag_info, f"Track {filename} is cleared.")
    except Exception as error:
        print(f"[{timestamp}]", tag_error, f"Cause: {error}")
        if "cannot be downloaded" in str(error):
            await bot.send_message(message.chat.id, f"Unfortunately, track {trackname} is not marked as Downloadable and so cannot be downloaded.")
        os.remove(filename)
        print(f"[{timestamp}]", tag_info, f"Track {filename} is cleared.")
#desctibing bot's handlers
@bot.message_handler(commands = ['start'])
async def start(message):
    text = f'''Greetings, {message.from_user.first_name}!
I'm bot that helps downloading tracks and full playlists from **Soundcloud**.
Just send me the corresponding Soundcloud link and I will reply with the audio message.
    
by E.H.J.'''
    await bot.send_message(message.chat.id, text)
                  
@bot.message_handler(commands = ['help'])
async def help(message):
    text = f'''Send me link to the song or playlist, and I will send you track here.
If error occur in the process - firstly make sure that the link is correct and the song is available.
After that please try and send the message again. If the error is still occurring, don't hesitate contacting me ([E.H.J.](t.me/nmanshin))'''
    await bot.send_message(message.chat.id, text)  
  
@bot.message_handler(content_types = ['text'])
async def get_user_text(message):
    link = message.text
    result = await api.resolve(link)
    if type(result).__name__ == "Playlist":
        await fetch_playlist(message, link)
    elif type(result).__name__ == "Track":
        await fetch_track(message, link)
    else:
        await bot.send_message(message.chat.id, 'I dont know what is this link for.\nPlease try another one.')  

          
#launching bot
print(f"[{timestamp}]", tag_info, "Bot Started...")
try:
    asyncio.run(bot.polling())
except Exception as error:
    print(f"[{timestamp}]", tag_error, f"Cause: {error}")
    
