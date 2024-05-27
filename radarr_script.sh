#!/bin/bash
# This script is used to run letterboxd.py from Radarr Custom Script Connection
# It should be set to run On Import

if [[ "$radarr_eventtype" != "Download" ]]; then
    echo "Radarr wrong event, skipping"
    exit 0
fi

sleep 5
script_full_path=$(dirname "$0")
python3 $script_full_path/letterboxd2plex.py --tmdb $radarr_movie_tmdbid