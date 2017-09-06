from optparse import OptionParser
from spot_sdk import Feed
import http.client
import json

# Get input params
parser = OptionParser()
parser.add_option("-s", "--spotkey", dest="spotkey", help="spot api key", metavar="FILE")
parser.add_option("-m", "--memairkey", dest="memairkey", help="memair api key", metavar="FILE")
(options, args) = parser.parse_args()

feed = Feed(options.spotkey)
feed.collect()

parsed_locations = []
for i, location in enumerate(feed.messages):
  params = {
    'latitude':  str(location.latitude),
    'longitude': str(location.longitude),
    'timestamp': str(location.datetime),
    'source':    'Spot: ' + location.type,
  }
  parsed_locations.append(params)

conn = http.client.HTTPSConnection(host='memair.herokuapp.com', port=443)
headers = {"Content-type": "application/json"}
conn.request("POST", "/api/v1/bulk/locations", json.dumps({'json': parsed_locations, 'access_token': options.memairkey}), headers)
content = conn.getresponse()
response = json.loads(content.read())
print(response)
conn.close()
