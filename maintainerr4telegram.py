#!/usr/bin/env python3

# Description: This scripts adds Telegram notifications to [Maintainerr](https://github.com/jorenn92/Maintainerr)
# Author: Suka97
# Source: https://github.com/suka97/letterboxd2plex

import argparse, yaml, os
from plexapi.server import PlexServer


# Parse arguments
parser = argparse.ArgumentParser(description='Monitor Plex collection and notify newly added throgh Telegram')
parser.add_argument('--config', default=f'{os.path.dirname(__file__)}/config.yml',
                    help='Configuration file')
parser.add_argument('--silent', action="store_false", help='Run silently without sending messages (for first time run)')
args = parser.parse_args()

# Load configuration
with open(args.config) as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


# Send Telegram message 
import telebot
import requests
from io import BytesIO
bot = telebot.TeleBot(config['telegram']['token'])
def send_notification(plexapi_movie, coll_name):
    msg = f'*Maintainerr* \n"{plexapi_movie.title}" added to "{coll_name}"'
    response = requests.get(plexapi_movie.thumbUrl)
    photo = BytesIO(response.content)
    bot.send_photo(chat_id=config['telegram']['chat_id'], photo=photo.read(), caption=msg, parse_mode='Markdown')

# Connect to Plex
plex = PlexServer(config['plex']['base_url'], config['plex']['token'])
plex_lib = plex.library.section(config['plex']['library'])

# Get last collection items from the json file
try:
    with open(f'{os.path.dirname(__file__)}/.maintainerr_items.yaml') as f:
        last_items = yaml.safe_load(f)
except FileNotFoundError:
    last_items = []


# Aux: Was movie already on the collection?
def was_movie_already_on_collection(plexapi_movie, coll_name):
    for coll in last_items:
        if ( coll['coll_title'] == coll_name ):
            for item in coll['items']:
                if ( item == plexapi_movie.guid ):
                    return True
    return False


# Fetch Plex collection items
new_items = []
plex_coll = plex_lib.collections()
for coll in plex_coll:
    if not ( coll.title in config['maintainerr']['collections'] ):
        continue
    coll_items = coll.items()
    coll_obj = {'coll_title': coll.title, 'items': []}
    for movie in coll_items:
        coll_obj['items'].append(movie.guid)
        if was_movie_already_on_collection(movie, coll.title):
            continue
        print(f'"{movie.title}" added to "{coll.title}"')
        if not args.silent:
            send_notification(movie, coll.title)
    new_items.append(coll_obj)

# Save new items to json file
with open('./.maintainerr_items.yaml', 'w') as f:
    yaml.dump(new_items, f)
