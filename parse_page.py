import requests
import sys
import mwparserfromhell
import tomllib
import re

import time
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
# From this project
import load_cfg

def get_info(filename):
	try:
		boards    = load_cfg.boards();
		# {'short'    : 'AE',
		#  'name'     : 'Arbitration enforcement',
		#  'page'     : 'Arbitration/Requests/Enforcement',
		#  'archive'  : 'Arbitration/Requests/Enforcement/Archive',
		#  'namespace': '4'
		# }
		nses      = load_cfg.namespaces();
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
		# print(f"{namespace}{pagename}")
	except:
		print(f"Error: Could not get info for {filename}.")
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

def parse_page(page, title=None, filename=None, prunedate=parse("1991-12-26"), before=datetime.now(timezone.utc) + timedelta(days=1), minlength=1, verbose=False):
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
		kludge = kludge.replace(garbage, "").replace(garbage, "").replace(garbage, "")

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
			if verbose == True:
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
				print(f"Timestamp parsing error: {stamps}")			
				firsttime  = parse("1970-01-01")
			try:
				lasttime   = max(stamps)
			except:
				print(f"Timestamp parsing error: {stamps}")		
				lasttime   = parse("1970-01-01")
			
			maxindent  = 1
			while True:
				if section.count(":"*maxindent) == 0:
					break
				maxindent += 1
			if verbose == True:
				print(f"sts: {sect.count(" (UTC)")} / rgx: {len(timestamps)} / utk: {sect.count("[[User talk:")} / parse: {len(talklinks)} / users: {distusers} / range: {firsttime} to {lasttime} / indent: {maxindent}")

	#		sections.append({
	#			"head"      : head,
	#			"length"    : len(sect),
	#			"timestamps": len(timestamps),
	#			"userlinks" : len(userlinks),
	#			"usertalks" : len(talklinks),
	#			"distusers" : distusers,
	#		})
			if (before > lasttime) and (lasttime > prunedate) and (len(sect) > minlength):
			#if (lasttime > prunedate) and (len(sect) > 25000):
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

	page = load_cfg.file(sys.argv[1])

	text = parse_page(page, filename=sys.argv[1])
	print(text)