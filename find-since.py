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
import math
# From this same project
import first_revision
import tsv_to_wikitable
import get_page
import parse_page
import version

print("Hi!")

########################################
# Initialize some things.
########################################
httpApi   = "https://en.wikipedia.org/w/api.php"
sleepTime = 0.01
batchSize = 10
dataName  = "data"
pagesName = "pages"
logName   = "log.txt"

data      = Path(os.getcwd(), dataName)
logfile   = Path(data, logName)
pages     = Path(data, pagesName)

data.mkdir(mode=0o777, exist_ok=True)
logfile.mkdir(mode=0o777, exist_ok=True)
pages.mkdir(mode=0o777, exist_ok=True)

t=[time.perf_counter()]

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
		}, headers=version.headers())
		#print(response.request.url)
		data = response.json()
		#print(data)
		for page in data['query']['allpages']:
			prevpages.append(page['title'])
		if 'continue' in data:
			print(f"Retrieving...............  {len(prevpages)}")
			apcontinue = data['continue']['apcontinue']
		else:
			print(f"All page titles retrieved: {len(prevpages)}")
			return prevpages

	# "batchcomplete":"","continue":{"apcontinue":"TheYouGeneration","continue":"-||"},
	# {"batchcomplete":"","query":

def measure_back_to(archives, date):
	rev = first_revision.fetch(f"{spacename}:{arch}{page}")

def pad(string, width=5):
	a = " " * width
	string = str(string) + a
	return string[0:width]

def tick(verbose=False):
	if verbose:
		print(f"⏳{time.perf_counter()-t[0]:.3f}s")
	t[0]=time.perf_counter()

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
def find_since(since, before=parse((datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")).astimezone(timezone.utc).replace(tzinfo=None)):
	v = False
	#print(boards)
	#print(namespaces["number"]["108"])

	for board in boards.items():
		print(board[1])
		pagePath = Path(pages, board[1]['short'])
		pagePath.mkdir(mode=0o777, exist_ok=True)
	#	print(board['short'])
	#	print(board['name'])
	#	print(board['page'])
	#	print(board['archive'])

	allPages = []
	metrics  = {}
	tick(v)

	for board in boards.items():
		# For each board, we get a PrefixIndex of all its archive pages,
		# then go back from the highest number to find all relevant archives
		# (those with first-revision dates that indicate relevant threads).

		# We add these archive pages, and their metadata, to allPages.

		archivePages = []
		pagesNumeric = []
		# We have to filter out goofy legacy stuff from 2007, like "WP:ANI/Archives/U/User:"
		pagesSince   = []
		datesSince   = []
		arch         = board[1]['archive']
		archSpaced   = arch.replace("_", " ")
		spacename    = f"{namespaces["number"][board[1]['namespace']]}"
		print(f"{board[1]['name']} (archive prefix: {spacename}:{board[1]['archive']})")
		########################################
		archivePages = getPrefixIndex(prefix=board[1]['archive'], ns=board[1]['namespace'])
		# Wowzers! This hits the API.
		########################################
		# archivePages.sort()
		#for page in archivePages
		#	print(page)`
		for page in natsorted(archivePages):
			page = stripBeginning(page, f"{spacename}:{arch}")
			page = stripBeginning(page, f"{spacename}:{archSpaced}")
			try:
				int(page)
				pagesNumeric.append(page)
			except:
				pass
				#print(f"Non-numeric archive: {page}")
			#print(page)

		pagesNumeric.reverse()
		print(f"Numeric archives: {len(pagesNumeric)}, highest: {pagesNumeric[0]}")
		tick(v)

		# Now we assemble the list of all the pages that are actually since the date.

		pagesSince.append(f"{spacename}:{board[1]['page']}") 
		datesSince.append(f"{nowstamp}")
		allPages.append([f"{spacename}:{board[1]['page']}", f"{nowstamp}", f"{board[1]['short']}-999999"])
		metrics[board[1]['short']] = 0
		# One-off handler for the current page

		for page in pagesNumeric:
			########################################
			rev = first_revision.fetch(f"{spacename}:{arch}{page}")
			# Wowzers! This hits the API.
			########################################
			# 2025-02-23T12:00:37Z
			revdate = parse(rev).astimezone(timezone.utc).replace(tzinfo=None)
			pagesSince.append(f"{spacename}:{arch}{page}")
			datesSince.append(f"{revdate}")
			allPages.append([f"{spacename}:{arch}{page}", f"{revdate}", f"{board[1]['short']}-{page}"])

			if revdate < since:
				break
		tick(v)
		#print(pagesSince)
		#print(datesSince)

	# We have now successfully retrieved the list of all the archive page titles
	# for all the boards we want to look at.

	# Now it is time to look at the supplied args and decide what to do with that list.
	# We might just save it and be done, or we might actually get wikitext for all of them.

	# It will look something like this:
	#  
	if args.list is not None:
		stringy = ""
		for item in allPages:
			stringy += f"{item[0]}\t{item[1]}\n"
		write(args.list, stringy)
		print(f"Saved to {args.list}")

	if (args.scrape is not None) or (args.analyze is not None):
		print(f"args.scrape is {args.scrape}")
		print(f"args.analyze is {args.analyze}")
		# This was goofy: they should just scrape to the per-board folders.
		# Commenting it out since those are created now. -2025-09-30
		# if (args.scrape is None):
		# 	scrape = f"data/{nowstamp}/"
		# else:
		# 	scrape = args.scrape
		# scrapeDir = Path(scrape)
		# scrapeDir.mkdir(mode=0o777, exist_ok=True)
		if (args.analyze is not None):
			analyzed = []
		count = 0

		w = math.ceil(math.log(len(allPages)+1, 10))
		# Number of digits needed to display the whole number
		# 2 is 1, 69 is 2, 420 is 3, 1984 is 4
		tick(v)
		for item in allPages:
			# ["Wikipedia:Administrators'_noticeboard", '2025-10-01 09:37:28', 'AN-999999']
			count += 1
			shortname = item[2].split("-")[0]
			filepath = Path(pages, shortname, item[2] + ".txt")
			#text = "Hooma baroomba"

			if (args.scrape is not None):
				print(f"{pad(count, w)} of {pad(len(allPages), w)}: getting wikitext for {item[0]}")
				########################################
				text = get_page.wikitext(item[0])
				tick()
				# Wowzers! This hits the API!
				########################################
				write(filepath, text)
			else:
				# Try to retrieve page from disk, if it doesn't work, fetch it.
				print(f"{pad(count, w)} of {pad(len(allPages), w)}: reading diskfile for {item[0]}")
				try:
					text = get_page.from_disk(str(filepath))
					tick()
				except:
					print(f"Didn't work: fetching from server.")
					text = get_page.wikitext(item[0])
					tick()
					write(filepath, text)
			if (args.analyze is not None):
				bolus = parse_page.parse_page(text, filename=f"{item[2]}", prunedate=since, minlength=minimum, before=before)
				for bitem in bolus:
					i = parse_page.get_info(f"{item[2]}")
					short     = i['short']
					arch      = i['arch']
					namespace = i['namespace']
					pagename  = i['pagename']

					bitem['head'] = bitem['head'].replace("[","").replace("]","")
					bitem['head'] = f"[[{namespace}{pagename}#{bitem['head']}|{bitem['head']}]]"

					if bitem['archive'] == "999999":
						bitem['archive'] = "Current"
					try:
						metrics[i['short']] += 1
					except:
						print("Couldn't increment metrics.")
				tick(v)
				analyzed += bolus
		i = 0
		for key in metrics:
			print(f"{pad(key, 10)}: {metrics[key]}")
			i += int(metrics[key])
		print(f"{pad("Total", 10)}: {i}")


	if args.analyze is not None:
		write(f"{args.analyze}.json", json.dumps(analyzed, indent=2))

		tsv = "\t".join(analyzed[0].keys())
		tsv += "\n"
		for row in analyzed[1:]:
			tsv += "\t".join(map(str, row.values()))
			tsv += "\n"

		if (args.format == "tsv") or (args.format == "all"):
			write(f"{args.analyze}.tsv", tsv)

		if (args.format == "wikitable") or (args.format == "all"):
			wikitable = tsv_to_wikitable.convert(
				inputtext   = tsv,
				output      = None,
				rotate      = False,
				skipheader  = False,
				classes     = "wikitable sortable",
				attrs       = None,
				headerattrs = None,
				rowattrs    = None,
				altattrs    = None
				)
			write(f"{args.analyze}.txt", wikitable)


	if args.format is not None:
		print(f"args.format is {args.format}")
		# Write this function.

if __name__ == "__main__":
	nao = datetime.now(timezone.utc).date()
	nowstamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
	tomstamp = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

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
		help    = "Freshly downloads the wikitext of the archive pages, as plain text files, to /data/pages/. Default is to try reading them from disk."
	)

	parser.add_argument(
		"-a",
		"--analyze",
		nargs   = "?",
		const   = f"data/{nowstamp} analyze",
		default = None,
		help    = "Analyzes the wikitext, from the scrape directory, and writes a report to specified path. Default is: ./data/YYYY-MM-DD HH:MM:SS analyze(file extension)"
	)

	parser.add_argument(
		"-f",
		"--format",
		default = "json",
		help    = "Output format for wikitext analysis. Options are \"tsv\", \"json\", \"wikitable\" or \"all\"."
	)

	parser.add_argument(
		"-m",
		"--minimum",
		default = "1",
		help    = "Ignore all sections below this many bytes of content. Optional. Default is no restriction (e.g. 1)."
	)

	parser.add_argument(
		"-b",
		"--before",
		default = f"{tomstamp}",
		help    = "Restrict to discussions before a certain date. Optional. Default is no restriction (e.g. tomorrow)."
	)
	#help    = "Output format for wikitext analysis. Options are \"TSV\", \"wikitable\", or \"json\"."

	args = parser.parse_args()

	print("Arguments: ", args)

	# Sanity checks for arguments, lest the program run for several minutes and THEN fail because of a typo
	try:
		minimum = int(args.minimum)
		if minimum < 0:
			raise ValueError("Minimum length must be positive")
	except:
		print(f"ERROR: couldn't parse minimum (\"{args.minimum}\").")
		exit()

	try:
		since = parse(args.date).astimezone(timezone.utc).replace(tzinfo=None)
		print(f"Parsed after date : {since}")
	except:
		print(f"ERROR: couldn't parse after date (\"{args.date}\").")
		exit()

	try:
		before = parse(args.before).astimezone(timezone.utc).replace(tzinfo=None)
		print(f"Parsed before date: {before}")
	except:
		print(f"ERROR: couldn't parse before date (\"{args.before}\").")
		exit()

	if args.format not in ["tsv", "json", "wikitable", "all"]:
		print(f"ERROR: couldn't parse format (\"{args.format}\").")
		exit()
	find_since(since, before=before)

