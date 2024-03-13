#!/bin/bash
# This script is used to run letterboxd.py from Radarr Custom Script Connection
# It should be set to run On Import

script_full_path=$(dirname "$0")
python3 $script_full_path/letterboxd2plex.py --dry_run --tmdb $radarr_movie_tmdbid