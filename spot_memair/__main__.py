from optparse import OptionParser
from spot_sdk import Feed
import timestring
import requests
import json

# Get input params
parser = OptionParser()
parser.add_option("-s", "--spotkey", dest="spotkey", help="spot api key", metavar="FILE")
parser.add_option("-m", "--memairkey", dest="memairkey", help="memair api key", metavar="FILE")
(options, args) = parser.parse_args()

feed = Feed(options.spotkey)
feed.collect()

def get_latest_timestamp():
  query = "{Locations(first: 1, order: timestamp_desc){timestamp, source}}"
  data = {
  'query' : query,
  'access_token': options.memairkey
  }
  r = requests.post("https://memair.com/graphql", data)
  response = json.loads(r.text)
  return timestring.Date(response['data']['Locations'][0]['timestamp']).date

latest_timestamp = get_latest_timestamp()

mutations = []
for i, location in enumerate(feed.messages):
  if timestring.Date(location.datetime).date > latest_timestamp:
    mutations.append('loc' + str(i) + ': CreateLocation(lat:' + str(location.latitude) + ', lon:' + str(location.longitude) + ', timestamp: "' + str(location.datetime) + '", source: "Spot: ' + location.type + '") {id}')

if len(mutations) > 0:
  data = {
  'query' : 'mutation{' + ' '.join(mutations) + '}',
  'access_token': options.memairkey
  }
  r = requests.post("https://memair.com/graphql", data)
  print(json.loads(r.text))
