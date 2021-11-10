# Little Oracle Annie, JPxG, 2021 November 9

import sys
import traceback
import os
import time
# This is used so that happy programs can sleep warmly. Snooze snooze!
from pathlib import Path
# For filesystem interactions. Read read! Write write!
import requests
# For scraping webpages. Scrape scrape!
from html.parser import HTMLParser
# Required to use BeautifulSoup. Parse parse!
from bs4 import BeautifulSoup
# The real meat and potatoes of the HTML parsing. Slurp slurp!
# Documentation for this is recommended reading to get how the program works.
from datetime import datetime
from datetime import timedelta
from datetime import timezone
# Required to use time. Tick tock!
import json
# Required to parse json. Parse parse!
import argparse
# Required to parse arguments. Parse parse...!!



# I should parse args here.

# Stuff that ought to be specifiable:
# "how many archives to go back"
# "Just scrape/analyze the current ones"
# "Ignore current ones"
# "omit actual api query"
# "omit actual write to disk"


# Set base URL for API.


# Array of all the noticeboards we want to monitor.

boards = {
	"AN": {
		"short":	"AN",
		"name":		"Wikipedia:Administrators'_noticeboard",
		"archive":	"Wikipedia:Administrators'_noticeboard/Archive"
		},
	"AN3": {
		"short":	"AN3",
		"name":		"Wikipedia:Administrators'_noticeboard/Edit_warring",
		"archive":	"Wikipedia:Administrators'_noticeboard/3RRArchive",
		},
	"ANI": {
		"short":	"ANI",
		"name":		"Wikipedia:Administrators'_noticeboard/Incidents",
		"archive":	"Wikipedia:Administrators'_noticeboard/IncidentArchive",
		},
	"AE": {
		"short":	"AE",
		"name":		"Wikipedia:Arbitration/Requests/Enforcement",
		"archive":	"Wikipedia:Arbitration/Requests/Enforcement/Archive",
		},
	"BLPN": {
		"short":	"BLPN",
		"name":		"Wikipedia:Biographies_of_living_persons/Noticeboard",
		"archive":	"Wikipedia:Biographies_of_living_persons/Noticeboard/Archive",
		},
	"COIN": {
		"short":	"COIN",
		"name":		"Wikipedia:Conflict_of_interest/Noticeboard",
		"archive":	"Wikipedia:Conflict_of_interest/Noticeboard/Archive_",
		},
	"DRN": {
		"short":	"DRN",
		"name":		"Wikipedia:Dispute_resolution_noticeboard",
		"archive":	"Wikipedia:Dispute_resolution_noticeboard/Archive_",
		},
	"ELN": {
		"short":	"ELN",
		"name":		"Wikipedia:External_links/Noticeboard",
		"archive":	"Wikipedia:External_links/Noticeboard/Archive_",
		},
	"FTN": {
		"short":	"FTN",
		"name":		"Wikipedia:Fringe_theories/Noticeboard",
		"archive":	"Wikipedia:Fringe_theories/Noticeboard/Archive_",
		},
	"NORN": {
		"short":	"NORN",
		"name":		"Wikipedia:No_original_research/Noticeboard",
		"archive":	"Wikipedia:No_original_research/Noticeboard/Archive_",
		},
	"NPOVN": {
		"short":	"NPOVN",
		"name":		"Wikipedia:Neutral_point_of_view/Noticeboard",
		"archive":	"Wikipedia:Neutral_point_of_view/Noticeboard/Archive_",
		},
	"RSN": {
		"short":	"RSN",
		"name":		"Wikipedia:Reliable_sources/Noticeboard",
		"archive":	"Wikipedia:Reliable_sources/Noticeboard/Archive_",
		},
	"BN": {
		"short":	"BN",
		"name":		"Wikipedia:Bureaucrats'_noticeboard",
		"archive":	"Wikipedia:Bureaucrats'_noticeboard/Archive_",
		},
	"ARBN": {
		"short":	"ARBN",
		"name":		"Wikipedia:Arbitration_Committee/Noticeboard",
		"archive":	"Wikipedia:Arbitration_Committee/Noticeboard/Archive_",
		}
}
print("Hi!")

########################################
# Initialize some things.
########################################
httpApi 	= "https://en.wikipedia.org/w/api.php"
sleepTime 	= 0.01
batchSize 	= 10
dataName 	= "data"
pagesName	= "pages"
logName		= "log.txt"

data 		= Path(os.getcwd() + "/" + dataName)
logfile		= Path(os.getcwd() + "/" + dataName + "/" + logName)
pages 		= Path(os.getcwd() + "/" + dataName + "/" + pagesName)

########################################
# Function to log to the logfile.
########################################

def aLog(argument):
	try:
		dalog = open(str(logfile), 'a')
		dalog.writelines(argument)
		dalog.close()
		print(argument)
	except (FileNotFoundError):
		dalog = open(str(logfile), 'w')
		dalog.write("\nSetting up runtime log at " + str(datetime.now(timezone.utc)) + "\n" + argument)
		dalog.close()
		print("Setting up runtime log.")
		print(argument)

########################################
# Make directories for data to live in.
########################################

data.mkdir(mode=0o777, exist_ok = True)
pages.mkdir(mode=0o777, exist_ok = True)

########################################
# Main loop: iterates over every board.
########################################

for board in boards:
	print("Processing " + boards[board]['name'])
	# Try to set up a folder for the board.
	boardPath = Path(os.getcwd() + "/" + dataName + "/" + pagesName + "/" + board)
	boardPath.mkdir(mode=0o777, exist_ok = True)

	archiveNumber = 1
	# Stupid, stupid, stupid hack for the stupid zero-indexed arbitration noticeboard.
	if boards[board]['name'] == "Wikipedia:Arbitration_Committee/Noticeboard":
		archiveNumber = 0

	# Repeat this until we break it.
	while True:
		query = ""
		for i in range(0,batchSize):
			query += boards[board]['archive'] + str(archiveNumber + i) + "|"
		# Trim the last "|"
		query = query[0:-1]
		# Increment the archive number
		archiveNumber += batchSize
		print(query)
		time.sleep(sleepTime)
		#####
		# Actually query the API.
		#####
		r = requests.get(httpApi, params={
								"action": "query",
								"prop": "revisions",
								"rvslots": "*",
								"rvprop": "content",
								"formatversion": "2",
								"format": "json",
								"titles": query
								})
		r = r.text
		r = json.loads(r)

		# Page now loaded. Time to process it.
		brokenYet = 0

		# This iterates over every page.
		for j in r['query']['pages']:
			if 'missing' in j:
				brokenYet = 1
			#print(j)
			#print("///////")
			else:
				number = j['title'][j['title'].lower().index('archive'):]
				number = number.replace("Archive","").replace(" ","").replace("_","")
				print(number)
				content = j['revisions'][0]['slots']['main']['content']
				pageJson = {
							"board"		: board,
							"archive"	: number,
							"title"		: j['title'],
							"pageid"	: j['pageid'],
							"scrapedate": str(datetime.now(timezone.utc)),
							"content"	: content
				}
				#print(pageJson)

				#####
				# Now we are going to write that json into a file.
				#####
				pagePath = Path(os.getcwd() + "/" + dataName + "/" + pagesName + "/" + board + "/" + board + "-" + number)
				pageFile = open(str(pagePath), 'w')
				pageFile.write(json.dumps(pageJson, indent=2, ensure_ascii= False))
				pageFile.close()

		if brokenYet == 1:
			break;

		# print(r)
		print("////////////")
print("Bye!")