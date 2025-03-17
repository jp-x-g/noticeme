import sys
import traceback
import os
import time
import tomllib
import requests
from pathlib import Path
from datetime import datetime, timezone
import json

print("Hi!")

########################################
# Initialize some things.
########################################
httpApi = "https://en.wikipedia.org/w/api.php"
sleepTime = 0.01
batchSize = 10
dataName = "data"
pagesName = "pages"
logName = "log.txt"

data = Path(os.getcwd(), dataName)
logfile = Path(data, logName)
pages = Path(data, pagesName)

data.mkdir(mode=0o777, exist_ok=True)
pages.mkdir(mode=0o777, exist_ok=True)

########################################
# Utility functions.
########################################

# Function to log to the logfile.

def aLog(argument):
	try:
		with open(logfile, 'a', encoding="utf-8") as dalog:
			dalog.write(argument + "\n")
		print(argument)
	except FileNotFoundError:
		with open(logfile, 'w', encoding="utf-8") as dalog:
			dalog.write(f"\nSetting up runtime log at {datetime.now(timezone.utc)}\n" + argument)
		print("Setting up runtime log.")
		print(argument)

# Find the most recent archive of a noticeboard.

def getPrefixIndex(prefix="The", apcontinue="", ns=0, prevpages=[]):
	#print(f"Prefix: '{prefix}', namespace: '{ns}'")
	prefix = prefix.replace("Wikipedia:", "")
	response = requests.get(httpApi, params={
		"action"     : "query",
		"list"       : "allpages",
		"format"     : "json",
		"apprefix"   : prefix,
		"aplimit"    : "500",
		"apcontinue" : apcontinue,
		"apnamespace": ns
	})
	print(response.request.url)
	if (len(prevpages) > 0):
		print(prevpages[0])
	print(f"Retrieving pages (so far: {len(prevpages)})")
	data = response.json()
	#print(data)
	for page in data['query']['allpages']:
		#print(page)
		#print(page['title'])
		prevpages.append(page['title'])
	if 'continue' in data:
		getPrefixIndex(prefix=prefix, ns=ns, prevpages=prevpages, apcontinue=data['continue']['apcontinue'])

	print("Okay")
	return prevpages

	# "batchcomplete":"","continue":{"apcontinue":"TheYouGeneration","continue":"-||"},
	# {"batchcomplete":"","query":

########################################
# Load boards from TOML
########################################

def load_boards():
	try:
		with open("boards.toml", "rb") as file:
			return tomllib.load(file)
	except FileNotFoundError:
		print("Error: boards.toml not found.")
		sys.exit(1)
	except tomllib.TOMLDecodeError:
		print("Error: Invalid TOML format in boards.toml.")
		sys.exit(1)

########################################
# Okay, let's start.
########################################

boards = load_boards()
#print(boards)
for board in boards.items():
	print(board[1])
#	print(board['short'])
#	print(board['name'])
#	print(board['page'])
#	print(board['archive'])

for board in boards.items():
	archivePages = []
	print(f"Processing {board[1]['name']}")
	print(f"Namespace: {board[1]['namespace']}, archive prefix {board[1]['archive']}")
	archivePages = getPrefixIndex(prefix=board[1]['archive'], ns=board[1]['namespace'])
	#boardPath = Path(pages, board)
	#boardPath.mkdir(mode=0o777, exist_ok=True)
	print("asdf")

"""

	archiveNumber = 1
	if details['name'] == "Wikipedia:Arbitration_Committee/Noticeboard":
		archiveNumber = 0

		"https://en.wikipedia.org/w/api.php?format=json&action=query&list=allpages&apprefix="



	while True:
		query = "|".join(f"{details['archive']}{archiveNumber + i}" for i in range(batchSize))
		archiveNumber += batchSize
		print(query)
		time.sleep(sleepTime)

		#response = requests.get(httpApi, params={
			#"action": "query",
			#"prop": "revisions",
			#"rvslots": "*",
			#"rvprop": "content",
			#"formatversion": "2",
			#"format": "json",
			#"titles": query
		#})

		#data = response.json()
		b#rokenYet = False

		for page in data.get("query", {}).get("pages", []):
			if 'missing' in page:
				brokenYet = True
			else:
				number = page['title'].split('Archive')[-1].strip().replace(" ", "").replace("_", "")
				content = page['revisions'][0]['slots']['main']['content']
				
				pageJson = {
					"board": board,
					"archive": number,
					"title": page['title'],
					"pageid": page['pageid'],
					"scrapedate": str(datetime.now(timezone.utc)),
					"content": content
				}
				
				pagePath = Path(boardPath, f"{board}-{number}")
				with open(pagePath, 'w', encoding="utf-8") as pageFile:
					json.dump(pageJson, pageFile, indent=2, ensure_ascii=False)

		if brokenYet:
			break
		print("////////////")

print("Bye!")
"""