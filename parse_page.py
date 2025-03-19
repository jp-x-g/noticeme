import requests
import sys
import mwparserfromhell
import tomllib
import re

import time
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse

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

def load_file(filename):
	try:
		with open(filename, "r", encoding="utf-8") as file:
			return file.read()
	except FileNotFoundError:
		print(f"Error: {filename} not found.")
		sys.exit(1)
	except:
		print(f"Error: Could not process {filename}.")
		sys.exit(1)


def get_info(filename):
	try:
		boards    = load_boards();
		# {'short'    : 'AE',
		#  'name'     : 'Arbitration enforcement',
		#  'page'     : 'Arbitration/Requests/Enforcement',
		#  'archive'  : 'Arbitration/Requests/Enforcement/Archive',
		#  'namespace': '4'
		# }
		nses      = load_namespaces();
		short     = filename.split("/")[-1:][0].split("-")[0]
		arch      = filename.split("/")[-1:][0].split("-")[1].replace(".txt", "")
		#print(board)
		namespace = nses['number'][boards[short]['namespace']]
		if namespace != "":
			namespace += ":"
		if arch == "999999":
			pagename = f"{boards[short]['page']}"
		else:
			pagename  = f"{boards[short]['archive']}{arch}"
		print(f"{namespace}{pagename}")
	except:
		pagename = filename
	return {
		"short"    : short,
		"arch"     : arch,
		"namespace": namespace,
		"pagename" : pagename
	}

############################################################
# Those are utility functions; this is the main logic.
############################################################

def parse_page(page, title=None, filename=None, prunedate=parse("1991-12-26")):
	if (title is None) and (filename is not None):
		i = get_info(filename)
		short     = i['short']
		arch      = i['arch']
		namespace = i['namespace']
		pagename  = i['pagename']

	# Now we are actually parsing the page.
	wikicode = mwparserfromhell.parse(page)
	stampgex = r"\d{2}:\d{2}, \d{1,2} [A-Z][a-z]{2,8} \d{4} \(UTC\)"
	utalkgex = r"\[\[User talk:^\]"
	#print(wikicode.filter_headings())
	#print(wikicode.filter_headings()[0])

	sections = []

	kludge = page
	print(kludge.count("=="))
	for garbage in ["=======", "======", "=====", "====", "==="]:
		kludge = kludge.replace(garbage, "").replace(garbage, "")

	for section in kludge.split("\n=="):
		section = "\n==" + section
		#print(section)
#	for section in wikicode.get_sections(levels=[2]):
		section = mwparserfromhell.utils.parse_anything(section)
		if len(section.filter_headings()) > 0:
			head = section.filter_headings()[0]
			sect = section[len(head):]
			head = head[2:-2].strip()
			#print(head)
			head = mwparserfromhell.utils.parse_anything(head)
			#print(head)
			head = head.strip_code()
			print(head)
			#print("Hoomba baroomba")
			timestamps = re.findall(stampgex, sect)
			talklinks  = [str(x) for x in section.filter_wikilinks() if "User talk:" in x]
			userlinks  = [str(x) for x in section.filter_wikilinks() if "User:" in x]
			distusers  = len(set(talklinks + userlinks))
			stamps     = [parse(str(x.replace(" (UTC)", ""))).astimezone(timezone.utc).replace(tzinfo=None) for x in timestamps]
			try:
				firsttime  = min(stamps)
			except:
				print(stamps)			
				firsttime  = parse("1970-01-01")
			try:
				lasttime   = max(stamps)
			except:
				print(stamps)
				lasttime   = parse("1970-01-01")
			print(f"Simple timestamp count: {sect.count(" (UTC)")} / regex count: {len(timestamps)}")
			print(f"Simple usertalks count: {sect.count("[[User talk:")} / parse count: {len(talklinks)}")
			print(f"Distinct users linked : {distusers}")
			print(f"Timestamp range: {firsttime} to {lasttime}")

			maxindent  = 1
			while True:
				if section.count(":"*maxindent) == 0:
					break
				maxindent += 1
			print(f"Max indent level: {maxindent}")

	#		sections.append({
	#			"head"      : head,
	#			"length"    : len(sect),
	#			"timestamps": len(timestamps),
	#			"userlinks" : len(userlinks),
	#			"usertalks" : len(talklinks),
	#			"distusers" : distusers,
	#		})
			if lasttime > prunedate:
				if (title is None) and (filename is not None):
					sections.append({
						"short"     : short,
						"archive"   : f"{arch}",
						"head"      : head,
						"length"    : len(sect),
						"timestamps": len(timestamps),
						"userlinks" : len(userlinks),
						"usertalks" : len(talklinks),
						"distusers" : distusers,
						"maxindent" : maxindent,
						"firsttime" : f"{firsttime}",
						"lasttime"  : f"{lasttime}"
					})
				else:
					sections.append({
						"short"     : "",
						"archive"   : "",
						"head"      : "",
						"length"    : len(sect),
						"timestamps": len(timestamps),
						"userlinks" : len(userlinks),
						"usertalks" : len(talklinks),
						"distusers" : distusers,
						"maxindent" : maxindent,
						"firsttime" : f"{firsttime}",
						"lasttime"  : f"{lasttime}"
					})

	#	return {
	#			"short"    : short,
	#			"name"     : boards[short]['name'],
	#			"page"     : boards[short]['page'],
	#			"archive"  : boards[short]['archive'],
	#			"namespace": boards[short]['namespace'],
	#			"title"    : f"{namespace}{pagename}",
	#			"archno"   : f"{arch}",
	#			"sections" : sections
	#	}
	return sections

	#print(wikicode.get_sections())
	#headings = [str(h.title).strip() for h in wikicode.filter_headings() if h.level == 2]

############################################################
# This runs when the program is invoked from the terminal.
############################################################

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python3 get_page.py pagename")
		sys.exit(1)

	page = load_file(sys.argv[1])

	text = parse_page(page, filename=sys.argv[1])
	print(text)