import json
import os
import time
import requests

# NOTE: Is very brittle, will break if Bloomsky change their schema!
BLOOMSKY_API_KEY_VARIABLE = 'BLOOMSKY_API_KEY'
API_URL = 'https://api.bloomsky.com/api/skydata/'

# Pull data from Bloomsky API
apiKey = os.environ.get(BLOOMSKY_API_KEY_VARIABLE)
response = requests.get(
	API_URL,
	headers={'Authorization': apiKey},
	params={'unit': 'intl'})
response.raise_for_status()
bloomskyAPIData = response.json()[0]

# Cache raw bloomsky data (debugging purposes).
latestJSON = json.dumps(bloomskyAPIData, sort_keys=True, indent=4, separators=(',', ': '))
open("last_bloomsky.json", "w").write(latestJSON)

def filter_unknown_value(val):
	return None if str(val) == "9999" else val

def create_fresh_dataset(bloomskyAPIData):
	bs = bloomskyAPIData
	return {
		"FormatVersion": 1,
		"DeviceInfo": { 
			"DeviceID": bs["DeviceID"],
			"DeviceName": bs["DeviceName"],
			"FullAddress": bs["FullAddress"],
			"StreetName": bs["StreetName"],
			"Latitude": bs["LAT"],
			"Longitude": bs["LON"]
		},
		"Entries": [] # Time series data points
	}


def create_timeseries_entry(bloomskyAPIData):
	bloomsky = bloomskyAPIData["Data"]
	storm = bloomskyAPIData["Storm"]

	return {
		"UnixTimestampUTC": time.time(),
		"BloomskyVoltage": bloomsky["Voltage"],
		"OutdoorTemperature": bloomsky["Temperature"],
		"OutdoorHumidity": bloomsky["Humidity"],
		"Pressure": bloomsky["Pressure"],
		"WindDirection": filter_unknown_value(storm["WindDirection"]),
		"WindGust": filter_unknown_value(storm["WindGust"]),
		"SustainedWindSpeed": filter_unknown_value(storm["SustainedWindSpeed"]),
		"UVIndex": filter_unknown_value(storm["UVIndex"]),
		"IsRaining": filter_unknown_value(bloomsky["Rain"]),
		"RainRate": filter_unknown_value(storm["RainRate"]),
		"RainDaily": storm["RainDaily"],
		"ImageURL": bloomsky["ImageURL"],
	}


# Read existing data
try:	
	dataset = json.loads(open("dataset.json", "r").read())
except Exception as e:
	print("ERROR loading dataset.json: %s" % e)
	print("Creating new blank dataset.")
	dataset = create_fresh_dataset(bloomskyAPIData)

# Append new time series entry
timeseries = create_timeseries_entry(bloomskyAPIData)
dataset["Entries"].insert(0, timeseries)

# Write out updated json
latestJSON = json.dumps(dataset, sort_keys=True, indent=4, separators=(',', ': '))
open("dataset.json", "w").write(latestJSON)

