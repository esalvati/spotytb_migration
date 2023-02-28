import spotipy
import os
import sys
from ytmusicapi import YTMusic
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

#load env vars for spotify authentication
load_dotenv()

##### FUNCTIONS
# Get playlists info from Spotify
def get_playlists(sp):
    results = sp.current_user_playlists()
    playlists = []
    for item in (results['items']):
        playlists.append({'id': item['id'], 'name': item['name'], 'description': item['description'], 'owner': list(item['owner'].values())[5]})
    return(playlists)

# Get playlist tracks from Spotify
def get_tracks(playlist):
    offset = 0
    tracks = []
    while True:
        tr_list = sp.user_playlist_tracks(playlist['owner'], playlist['id'], None, 100, offset)
        size_returned = len(tr_list['items'])
        if size_returned == 0:
            break
        offset += size_returned
        for item in (tr_list['items']):
            track = item['track']
            tracks.append({'name': track['name'], 'artist': list(track['artists'][0].values())[3]})
    return(tracks)

# Find tracks in Youtube
def find_tracks(tracks,yt):
    print(f'Searching...')
    ytr_ids = []
    nf_tracks = []
    for track in tracks:
        track_string = track['artist']+' '+track['name']
        tr_results = yt.search(track_string,'songs')
        found = False
        first_result = tr_results[0]
        for trr in tr_results:
            if trr['title'].lower() != track['name'].lower():
                #bad track name handling xD
                #maybe compare albuns...
                if trr['title'].lower() != track['name'].lower().replace('- remastered',''):
                    continue
            else:
                found = True
                ytr_ids.append(trr['videoId'])
                print(f'Adding {track_string}...')
                break
        if not found and first_result is None:
            print(f'! Unable to find {track_string} !')
            nf_tracks.append(track_string)
        elif not found:
            new_string = dict(list(first_result['artists'])[0])['name']+' '+first_result['title']
            print(f'? Unable to find {track_string}. Adding {new_string} instead... ?')
            ytr_ids.append(first_result['videoId'])
    return([ytr_ids, nf_tracks])

# Create the new playlist in Youtube
def create_playlist(playlist,tracks,yt):
    print(f'Creating playlist...')
    ypl_id = yt.create_playlist(playlist['name'],playlist['description'])
    yt.add_playlist_items(ypl_id, tracks)
    print(f'Done!')
    print(f'-----------------------------------------------')

## MAIN PROGRAM
#connect to youtube and spotify
yt = YTMusic('headers_auth.json')
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-read-private"))

#retrieve playlist info from spotify
playlists = get_playlists(sp)

#retrieve tracklist for each playlist
for playlist in (playlists):
    user_input = input('Do you want to migrate the playlist '+playlist['name']+'? (Y/n)')
    if user_input.lower() == 'y':
        #retrieve tracklist from spotify
        tracks = get_tracks(playlist)
        #retrieve track ids from youtube
        ytracks = find_tracks(tracks,yt)
        #create the playlist
        create_playlist(playlist,ytracks[0],yt)
        #print not found tracks
        if ytracks[1]:
            print(f'The tracks below were not found. Please add \'em manually.')
            for ind, i in enumerate(ytracks[1]):
                print(f'{ind}: {i}')
            print(f'-----------------------------------------------')
    else:
        continue
