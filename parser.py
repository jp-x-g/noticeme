# Little Oracle Annie, JPxG, 2021 November 9

import sys
import traceback
import os
import time
# This is used so that happy programs can sleep warmly. Snooze snooze!
from pathlib import Path
# For filesystem interactions. Read read! Write write!
from datetime import datetime
from datetime import timedelta
from datetime import timezone
# Required to use time. Tick tock!
import json
# Required to parse json. Parse parse!
import argparse
# Required to parse arguments. Parse parse...!!
import re
# Required to parse regexes.



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
logName		= "log-parser.txt"

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

# return re.compile(r"/n=+(.*?)=+/n").findall(s)


#def find_section_headings(s):
#    res = []
#    for equal_length in range(1, 7):
#        equals = r"=" * equal_length
#        pattern = re.compile(r"/n" + equals + r"(.*?)" + equals + r"/n")
#        for match in pattern.findall(s):
#            res.append(match)
#    return res

########################################
# Main loop: iterates over every board.
########################################

boardsDone = 0
archivesDone = 0
threadsDone = 0

for board in boards:
	print("Processing " + boards[board]['name'])
	# Try to set up a folder for the board.
	boardPath = Path(os.getcwd() + "/" + dataName + "/" + pagesName + "/" + board)
	boardPath.mkdir(mode=0o777, exist_ok = True)

	for path in boardPath.iterdir():
		if path.is_file():
			currentfile = open(path, "r")
			currentjson = json.load(currentfile)
			currentfile.close()
			print("B: " + str(boardsDone) + " / A: " + str(archivesDone) + " / T: " + str(threadsDone) + " (" + board + " / archive " + currentjson['archive'] + ")")
		archivesDone += 1
		s = currentjson['content']
		cursor = 0
		thisHeadingEnd = 0
		sectitle = "null"

		two = "=="
		three = "==="

		# Dumb hack because some old noticeboards used === instead of ==.
		if ((currentjson['board'] == "AN3") and (int(currentjson['archive']) < 63)) or ((currentjson['board'] == "ANI") and (int(currentjson['archive']) < 40)) or ((currentjson['board'] == "AN") and ((int(currentjson['archive']) == 2) or (int(currentjson['archive']) == 3))):
			two = "==="
			three = "===="
			
		lntwo = "\n" + two
		twoln = two + "\n"
		lnthree = "\n" + three
		threeln = three + "\n"

		#maxcursor = s.rfind(lntwo)

		#while (cursor != -1) and (cursor != maxcursor):
		while (cursor != -1):
			cursest = s.find(lntwo, cursor)
			# Ignore ===, ====, etc.
			if cursest != s.find(lnthree, cursor):
				# Length of thread is from thisHeadingEnd (i.e. still the ending of the last heading) to cursest (this new cursor location).
				length = cursest - thisHeadingEnd
				print("B: " + str(boardsDone) + " / A: " + str(archivesDone) + " / T: " + str(threadsDone) + " (" + board + " / archive " + currentjson['archive'] + ") length: " + str(length) + " / " + sectitle)
				#if (length > 100000):
					#aLog("\nLONGBOY FOUND! B: " + str(boardsDone) + " / A: " + str(archivesDone) + " / T: " + str(threadsDone) + " (" + board + " / archive " + currentjson['archive'] + ") length: " + str(length) + " / " + sectitle)
					#aLog("\n//////////" + str(boardsDone) + "//////////" + str(archivesDone) + "//////////" + str(threadsDone) + "//////////" + board + "//////////" + currentjson['archive'] + "//////////" + str(length) + "//////////" + sectitle)
				if (len(sectitle) > 2000):
					aLog("\nLONGTITLE FOUND (" + str(len(sectitle)) + ") B: " + str(boardsDone) + " / A: " + str(archivesDone) + " / T: " + str(threadsDone) + " (" + board + " / archive " + currentjson['archive'] + ") length: " + str(length) + " / " + sectitle[0:1000])
				thisHeadingEnd = s.find(twoln, (cursor+len(lntwo)))
				sectitle = s[cursest:thisHeadingEnd]
				sectitle = sectitle.replace(lntwo + " ", "").replace(" " + twoln, "").replace(two, "").replace("\n", "")
				print(cursor)
				threadsDone += 1
				cursor = thisHeadingEnd
			else:
				cursor = s.find(twoln, cursest)
			if cursor == -1:
				break;






#		res = []
#		for equal_length in range(1, 7):
#			equals = r"=" * equal_length
#			pattern = re.compile(r"/n" + equals + r"(.*?)" + equals + r"/n")
#			for match in pattern.findall(currentjson['content']):
#				res.append(match)
#		print(res)

		#print(nonexistent_variable_that_crashes_the_program)
	boardsDone += 1
print("Bye!")