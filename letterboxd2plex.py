import argparse, yaml
import feedparser
from plexapi.server import PlexServer

# For use with float comparison
def cmp_float(n1, n2):
    return abs(n1-n2) < 0.1

# Parse arguments
parser = argparse.ArgumentParser(description='Import Letterboxd ratings to Plex')
parser.add_argument('--config', default='./config.yml',
                    help='Configuration file')
parser.add_argument('--exit_on_match', action="store_true")
parser.add_argument('--dry_run', action="store_true")
args = parser.parse_args()

# Load configuration
with open(args.config) as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

# Fetch Letterboxd RSS
feed = feedparser.parse(config['letterboxd']['rss'])
reviews = []
for entry in feed.entries:
    rev = {
        "title": entry.letterboxd_filmtitle,
        "tmdb": entry.tmdb_movieid,
        "rating": float(entry.letterboxd_memberrating) * 2,
        "link": entry.link
    }
    reviews.append(rev)
print(f'Fetched {len(reviews)} reviews from Letterboxd')

# Connect to Plex
plex = PlexServer(config['plex']['base_url'], config['plex']['token'])
plex_lib = plex.library.section(config['plex']['library'])

# Update Plex Ratings
for rev in reviews:
    # Match Plex movie using tmbd id
    try:
        plex_movie = plex_lib.getGuid(f'tmdb://{rev["tmdb"]}')
    except KeyboardInterrupt:
        print("User aborted...")
        exit(0)
    except:
        # print(f'Could not find {rev["title"]} in Plex')
        continue

    # print(f'### {rev["title"]}')
    
    # Skip if ratings match
    if ( cmp_float(plex_movie.userRating, rev["rating"]) ):
        # print(f'Skipping {rev["title"]} as ratings match')
        if args.exit_on_match:
            exit(0)
        continue

    # Update Plex Rating
    if not args.dry_run:
        plex_movie.rate(rev["rating"])
    print(f'Updated rating for {rev["title"]} to {rev["rating"]}')
