from sclib.asyncio import SoundcloudAPI, Track, Playlist
import asyncio

client_id = 'ovyZZ34xgflQFUDCXvS4D07GsPUibGLg'

api = SoundcloudAPI(client_id)

async def fetch_track(link):
    track = await api.resolve(link)
    print(track.title)
    print(track.artwork_url)
    print(track.get_stream_url)
    print(track.STREAM_URL)
    print(track.permalink_url)
    
async def main():
    link = 'https://soundcloud.com/connorpricemusic/violet-feat-killa?si=cb22a531abf84f3b8ddd0326dc92209c&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing'
    await fetch_track(link)

asyncio.run(main())