import sys
import traceback
import os
import time
import tomllib
import requests
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
from natsort import natsorted
from dateutil.parser import parse
import argparse

# From this same project
import first_revision
import tsv_to_wikitable
import get_page

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
#pages.mkdir(mode=0o777, exist_ok=True)

########################################
# Utility functions.
########################################

# Function to log to the logfile.

def aLog(argument, filePath=logfile):
	try:
		with open(filePath, 'a', encoding="utf-8") as f:
			f.write(argument + "\n")
		print(argument)
	except FileNotFoundError:
		with open(filePath, 'w', encoding="utf-8") as f:
			f.write(f"\nSetting up runtime log at {datetime.now(timezone.utc)}\n" + argument)
		print("Setting up runtime log.")
		print(argument)

def write(filepath, content):
	try:
		with open(filepath, "w", encoding="utf-8") as file:
			file.write(content)
			print(f"Wrote {len(content)} to {filepath}.")
	except:
		print(f"Couldn't write to {filepath}.")

# Get an array of all pages with a prefix.

def stripBeginning(string="", prefix=""):
	if string.startswith(prefix):
		return string[len(prefix):]
	return string

def getPrefixIndex(prefix="The", ns="0"):
	#print(f"Prefix: '{prefix}', namespace: '{ns}'")
	#print(namespaces["number"][ns])
	prefix = stripBeginning(prefix, f"{namespaces["number"][ns]}:")
	prevpages = []
	apcontinue = ""

	while True:
		response = requests.get(httpApi, params={
			"action"     : "query",
			"list"       : "allpages",
			"format"     : "json",
			"apprefix"   : prefix,
			"aplimit"    : "500",
			"apnamespace": ns,
			"apcontinue" : apcontinue
		})
		#print(response.request.url)
		data = response.json()
		#print(data)
		for page in data['query']['allpages']:
			prevpages.append(page['title'])
		if 'continue' in data:
			print(f"Retrieving.........  {len(prevpages)}")
			apcontinue = data['continue']['apcontinue']
		else:
			print(f"All pages retrieved: {len(prevpages)}")
			return prevpages

	# "batchcomplete":"","continue":{"apcontinue":"TheYouGeneration","continue":"-||"},
	# {"batchcomplete":"","query":

def measure_back_to(archives, date):
	rev = first_revision.fetch(f"{spacename}:{arch}{page}")

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

def load_namespaces():
	try:
		with open("namespaces.toml", "rb") as file:
			return tomllib.load(file)
	except FileNotFoundError:
		print("Error: namespaces.toml not found.")
		sys.exit(1)
	except tomllib.TOMLDecodeError:
		print("Error: Invalid TOML format in namespaces.toml.")
		sys.exit(1)



########################################
# Okay, let's start.
########################################
def find_since(since):
	#print(boards)
	#print(namespaces["number"]["108"])

	for board in boards.items():
		print(board[1])
	#	print(board['short'])
	#	print(board['name'])
	#	print(board['page'])
	#	print(board['archive'])

	allPages = []

	for board in boards.items():
		archivePages = []
		pagesNumeric = []
		# We have to filter out goofy legacy stuff from 2007, like "WP:ANI/Archives/U/User:"
		pagesSince   = []
		datesSince   = []
		arch         = board[1]['archive']
		archSpace    = arch.replace("_", " ")
		spacename    = f"{namespaces["number"][board[1]['namespace']]}"
		print(f"{board[1]['name']} (archive prefix: {spacename}:{board[1]['archive']})")
		# This actually hits the API a bunch of times.
		archivePages = getPrefixIndex(prefix=board[1]['archive'], ns=board[1]['namespace'])
		# archivePages.sort()
		#for page in archivePages
		#	print(page)
		for page in natsorted(archivePages):
			page = stripBeginning(page, f"{spacename}:{arch}")
			page = stripBeginning(page, f"{spacename}:{archSpace}")
			try:
				int(page)
				pagesNumeric.append(page)
			except:
				pass
				#print(f"Non-numeric archive: {page}")
			#print(page)

		pagesNumeric.reverse()
		print(f"Numeric archives: {len(pagesNumeric)}, highest: {pagesNumeric[0]}")

		# Now we assemble the list of all the pages that are actually since the date.

		pagesSince.append(f"{board[1]['page']}") 
		datesSince.append(f"{nowstamp}")
		allPages.append([f"{board[1]['page']}", f"{nowstamp}", f"{board[1]['short']}"])
		# One-off handler for the current page

		areWeDoneYet = False 
		for page in pagesNumeric:
			rev = first_revision.fetch(f"{spacename}:{arch}{page}")
			# This hits the API.
			# 2025-02-23T12:00:37Z
			revdate = parse(rev).astimezone(timezone.utc).replace(tzinfo=None)
			pagesSince.append(f"{spacename}:{arch}{page}")
			datesSince.append(f"{revdate}")

			allPages.append([f"{spacename}:{arch}{page}", f"{revdate}", f"{board[1]['short']}"])
			if areWeDoneYet == True:
				break
			if revdate < since:
				areWeDoneYet = True
		#print(pagesSince)
		#print(datesSince)
	if args.list is not None:
		stringy = ""
		for item in allPages:
			stringy += f"{item[0]}\t{item[1]}\n"
		write(stringy, args.list)
		print(f"Saved to {args.list}")
		exit()
	if args.scrape is not None:
		print(f"args.scrape is {args.scrape}")
		scrapeDir = Path(os.getcwd(), dataName, args.scrape)
		scrapeDir.mkdir(mode=0o777, exist_ok=True)
		count = 0
		for item in allPages:
			print(f"{count} of {len(allPages)}: getting wikitext for {item[0]}")
			text = get_page.wikitext(item[0])
			path = scrapeDir / f"{item[2]}"
			write(text, path)
		exit()

	if args.analyze is not None:
		print(f"args.analyze is {args.analyze}")
		# Write this function.
	if args.format is not None:
		print(f"args.format is {args.format}")
		# Write this function.

if __name__ == "__main__":
	nao = datetime.now(timezone.utc).date()
	nowstamp = nao.strftime("%Y-%m-%d %H:%M:%S")

	boards = load_boards()
	namespaces = load_namespaces()

	parser = argparse.ArgumentParser(
		description = "This program looks at all the boards listed in boards.toml, determines what number their archives go up to, and then determines their creation dates, going back from the current board to the date specified. After that, its behavior is specified by the output options.",
		epilog      = ""
	)
	parser.add_argument(
		"date",
		help    = "Date (UTC) to fetch archives back to, inclusive of the date: you will get whatever archive was current as of that date. This does not require a particular format (although YYYY-MM-DD is best). Default is ereyesterday.",
		default = (nao - timedelta(days=2))
	)
	parser.add_argument(
		"-l",
		"--list",
		nargs   = "?",
		const   = f"data/{nowstamp} list.txt",
		default = None,
		help    = "Just list the archives, and don't bother retrieving them all. If you specify a path, the list will be saved there. Default is: ./data/YYYY-MM-DD HH:MM:SS list.txt",
	)
	parser.add_argument(
		"-s",
		"--scrape",
		nargs   = "?",
		const   = f"data/{nowstamp}/",
		default = None,
		help    = "Downloads the wikitext of the archives, as plain text files, to specified path. Default is: ./data/YYYY-MM-DD HH:MM:SS/"
	)

	parser.add_argument(
		"-a",
		"--analyze",
		nargs   = "?",
		const   = f"data/{nowstamp} analyze",
		default = None,
		help    = "Analyzes the wikitext, and writes a report to specified path. Default is: ./data/YYYY-MM-DD HH:MM:SS analyze(file extension)"
	)

	parser.add_argument(
		"-f",
		"--format",
		default = "tsv",
		help    = "Output format for wikitext analysis. Options are \"tsv\" or \"wikitable\"."
	)
	#help    = "Output format for wikitext analysis. Options are \"TSV\", \"wikitable\", or \"json\"."

	args = parser.parse_args()

	print("Arguments: ", args)

	try:
		since = parse(args.date).astimezone(timezone.utc).replace(tzinfo=None)
		print(f"Parsed date: {since}")
	except:
		print("Couldn't parse date. Exiting.")
		exit()

	find_since(since)