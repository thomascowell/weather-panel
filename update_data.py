import json
import os
import time
import requests

BLOOMSKY_API_KEY_VARIABLE = 'BLOOMSKY_API_KEY'
API_URL = 'https://api.bloomsky.com/api/skydata/'

# Pull data from Bloomsky API
apiKey = os.environ.get(BLOOMSKY_API_KEY_VARIABLE)
response = requests.get(
	API_URL,
	headers={'Authorization': apiKey},
	params={'unit': 'intl'})
response.raise_for_status()
data = response.json()

# Timestamp for now
timestr = time.strftime("%Y_%m_%d-%H_%M_%S")

# Integrate existing "latest.json"

# Save new "latest.json"
latestJSON = json.dumps(data[0], sort_keys=True, indent=4, separators=(',', ': '))
open("latest.json", "w").write(latestJSON)
open("historical/%s.json" % timestr, "w").write(latestJSON)
