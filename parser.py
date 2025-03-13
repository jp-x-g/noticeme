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

import sqlite3
# Required to base data. Base base!


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
httpApi 		= "https://en.wikipedia.org/w/api.php"
sleepTime 		= 0.01
batchSize 		= 10
dataName 		= "data"
pagesName		= "pages"
logName			= "log-parser.txt"
databaseName	= "noticeboards.db"

data 			= Path(os.getcwd() + "/" + dataName)
logfile			= Path(os.getcwd() + "/" + dataName + "/" + logName)
pages 			= Path(os.getcwd() + "/" + dataName + "/" + pagesName)
database		= Path(os.getcwd() + "/" + dataName + "/" + databaseName)

verbose			= 1

boardsDone		= 0
archivesDone 	= 0
threadsDone		= 0
longTitleCount 	= 0
badStamps 		= 0
nullEntries		= 0

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
# Function to ISO-format timestamps.
########################################

def formatStamp(s):
	s = s.strip()
	# 04:20, 31 12 1969
	# 04:20, 1 12 1969
	# 01234567890123456
	if len(s) == 16:
		s = s[0:7] + "0" + s[7:]
	# 04:20, 01 12 1969
	# 01234567890123456

	yyyy = s[13:17]
	mm = s[10:12]
	dd = s[7:9]
	hhmm = s[0:5]

	t = yyyy + "-" + mm + "-" + dd + "T" + hhmm
	return t


########################################
# Function to do nothing.
########################################

def derp():
	derp = 1;
	return "derp"

########################################
# Function to check validity of stamps.
########################################

def checkStamp(s):
	# 1969-12-31T23:59
	# 01234567890123456

	yyyy = s[0:4]
	mo = s[5:7]
	dd = s[8:10]
	hh = s[11:13]
	mn = s[14:16]

	# print(yyyy + "-" + mo + "-" + dd + "-" + hh + "-" + mn)

	if ((yyyy + mo + dd + hh + mn).isdigit()) == False:
		return False
	if (int(yyyy) > 3000) or (int(yyyy) < 2000):
		return False
	if (int(mo) > 12) or (int(mo) < 1):
		return False
	if (int(dd) > 31) or (int(dd) < 1):
		return False
	if (int(hh) > 23) or (int(hh) < 0):
		return False
	if (int(mn) > 59) or (int(mn) < 0):
		return False

	return True

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
# Living in the database, whoa-hoah.
########################################

con = sqlite3.connect(database)
cur = con.cursor()
query = ""
query += "CREATE TABLE IF NOT EXISTS threads ("
query += "title text, "
query += "board text, "
query += "archive integer, "
query += "date text, "
query += "altdate integer, "
query += "length integer, "
query += "timestamps integer, "
query += "userlinks integer, "
query += "usertlinks integer"
query += ")"
print(query)

cur.execute(query)

########################################
# Main loop: iterates over every board.
########################################


aLog("\nRunning : " + str(datetime.now(timezone.utc)) + "\n")

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
			if verbose:
				print("B: " + str(boardsDone) + " / A: " + str(archivesDone) + " / T: " + str(threadsDone) + " (" + board + " / archive " + currentjson['archive'] + ")")
		archivesDone += 1
		s = currentjson['content']
		cursor = 0
		thisHeadingEnd = 0
		sectitle = "null_section_title_for_noticeme"

		two = "=="
		three = "==="

		# Dumb hack because some old noticeboards used === instead of ==.
		# What we're looking for:
		
		# board	from to
		#----------------
		# AN3	1	62
		# ANI	1	40
		# AN	2	3

		# COIN also has insanely long heaps of crap around the headlines from archives 1 thru 17, but these don't affect the headings themselves.

		if ((currentjson['board'] == "AN3") and (int(currentjson['archive']) < 63)) or ((currentjson['board'] == "ANI") and (int(currentjson['archive']) < 40)) or ((currentjson['board'] == "AN") and ((int(currentjson['archive']) == 2) or (int(currentjson['archive']) == 3))):
			two = "==="
			three = "===="
			
		lntwo = "\n" + two
		twoln = two + "\n"
		lnthree = "\n" + three
		threeln = three + "\n"

		# All lines with section headings look like "\n=blah blah blah=\n", with the line returns at the beginning and end.
		# There can be basically anything inside those equals signs (including more equals signs, which makes them subheadings).
		# However, putting stuff after the second set of them will cause it to not render properly.
		# The only exception is, apparently, if you put spaces after them. Let's fix that.
		spaces = ""
		tabs = ""

		# Strip all HTML notes.
		# text_after = re.sub(regex_search_term, regex_replacement, text_before)
		s = re.sub("<!--.*-->\n", "\n", s)

		for i in range(0,20):
			spaces = spaces + " "
			tabs = tabs + "	"
			s = s.replace(spaces + "\n", "\n")
			s = s.replace(tabs + "\n", "\n")
			# Note, 2021-11-09: Replacing whitespace characters at the end of headings cuts the # of long (>2000 char) section headings from 282 to 42.
			# Note: Replacing out tabs AND whitespace characters at the end of headings cuts the # down to 33.
			#print("spaces:" + spaces + ".")
			#print("tabs:" + tabs + ".")


		#maxcursor = s.rfind(lntwo)

		#while (cursor != -1) and (cursor != maxcursor):
		while (cursor != -1):
			cursest = s.find(lntwo, cursor)
			# Ignore ===, ====, etc.
			if cursest != s.find(lnthree, cursor):
				# Length of thread is from thisHeadingEnd (i.e. still the ending of the last heading) to cursest (this new cursor location).
				section = s[thisHeadingEnd:cursest]
				length = cursest - thisHeadingEnd

				# Now we generate some fun statistics from the section.
				timesCt = section.count("(UTC)")
				userlCt = section.count("[[User:")
				usertCt = section.count("[[User talk:")
				linksCt = section.count("[[")
				tempsCt = section.count("{{")
				suppsCt = section.count("'''Support")
				opposCt = section.count("'''Oppose")

				# Some obtuse code to (try to) find the timestamp of the OP.

				tsSearch = section.replace("January", "01").replace("February", "02").replace("March", "03").replace("April", "04").replace("May", "05").replace("June", "06").replace("July", "07").replace("August", "08").replace("September", "09").replace("October", "10").replace("November", "11").replace("December", "12")
				tsSearch = tsSearch.replace("Jan", "01").replace("Feb", "02").replace("Mar", "03").replace("Apr", "04").replace("May", "05").replace("Jun", "06").replace("Jul", "07").replace("Aug", "08").replace("Sep", "09").replace("Oct", "10").replace("Nov", "11").replace("Dec", "12")

				stampFound = 0
				stampCount = 1
				lastResort = "1969-12-31T23:42"
				usedResort = 0

				while stampFound == 0:
					#This loop will run until we find a valid stamp.
					firstStampLoc = tsSearch.find("(UTC)")

					if (tsSearch.find("{{") < firstStampLoc) and (firstStampLoc < tsSearch.find("}}")):
						# If the first timestamp is inside a template, it's probably a closer note or a hat note.
						lastResort = formatStamp(tsSearch[(firstStampLoc - 18):(firstStampLoc - 1)].replace("\n", ""))
						# Save the archive timestamp, in case we are totally unable to find anything else.
						firstStampLoc = tsSearch.find("(UTC)", tsSearch.find("}}"))
	
					# 07:56, 31 01 2021 (UTC)
					# 8765432109876543210 (minus)
					# 01234567890123456
	
					fir = tsSearch[(firstStampLoc - 18):(firstStampLoc - 1)]
					# Get the actual string of the first timestamp.
					fir = fir.replace("\n", "")
					#print(fir + "|" + formatStamp(fir))
					fir = formatStamp(fir)

					if (stampCount > 1):
						derp()
						#print(str(firstStampLoc) + " / " + fir + str(checkStamp(fir)))

					
					if firstStampLoc == -1:
						stampFound = 1;
						fir = "1969-12-31T23:59"
						#if (lastResort != "1969-12-31T23:42"):
						#	print(lastResort)
						#	aLog("\nLast resort:" + lastResort + " for sectitle " + sectitle + ", " + board + " / " + currentjson['archive'])
						if  (lastResort != "1969-12-31T23:42") and (checkStamp(lastResort) == True):
							# If there's an archive-top stamp, we can at least use that.
							fir = lastResort
							usedLast = 1
						else:
							badStamps += 1
						break;
					if checkStamp(fir) == True:
						stampFound = 1;
					else:
						tsSearch = tsSearch[(firstStampLoc + 1):]
						stampCount += 1

				stringLog = "B-" + str(boardsDone).ljust(2) + " A-" + str(archivesDone).ljust(5) + " T-" + str(threadsDone).ljust(7) + "| " + board.ljust(5) + " " + currentjson['archive'].ljust(4) + ", " + str(length).ljust(7) + "b, utc " + str(timesCt).ljust(4) + ", us " + str(userlCt).ljust(4) + ", ut " + str(usertCt).ljust(4) + ", ts " + fir + " (stamp count: " + str(stampCount) + ") | " + sectitle

				# we also have stampCount, and usedResort

				# Lot of sections with the title "null". 

				if ((fir == "1969-12-31T23:59") and (sectitle != "null_section_title_for_noticeme")) or (usedResort == 1):
					# Test condition: log these ones to file.
					aLog("\n" + stringLog)
				else:
					if verbose:
						print(stringLog)
				if (sectitle == "null_section_title_for_noticeme"):
					nullEntries += 1

				if (stampCount > 1) or (usedResort == 1):
					altDate = 1
				else:
					altDate = 0
				########################################
				# Time to mess with the actual database
				########################################

				if (sectitle != "null_section_title_for_noticeme"):
					# CREATE TABLE IF NOT EXISTS threads
					# title		board		archive		date		altdate	
					# length	timestamps	userlinks	usertlinks	
					#query = "INSERT INTO threads (title, board, archive, date, altdate, length, timestamps, userlinks, usertlinks) VALUES("
					#query += "'"  + str(sectitle) + "'"
					#query += ",'" + str(board) + "'" 
					#query += ","  + str(currentjson['archive'])
					#query += ",'" + str(fir) + "'"
					#query += ","  + str(altDate)
					#query += ","  + str(length)
					#query += ","  + str(timesCt)
					#query += ","  + str(userlCt)
					#query += ","  + str(usertCt)
					#query += ")"
					cur.execute("INSERT INTO threads (title, board, archive, date, altdate, length, timestamps, userlinks, usertlinks) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (str(sectitle), str(board), str(currentjson['archive']), str(fir), str(altDate), str(length), str(timesCt), str(userlCt), str(usertCt)))

				########################################
				# Done messing with the database
				########################################


				#if (length > 100000):
					#aLog("\nLONGBOY FOUND! B: " + str(boardsDone) + " / A: " + str(archivesDone) + " / T: " + str(threadsDone) + " (" + board + " / archive " + currentjson['archive'] + ") length: " + str(length) + " / " + sectitle)
					#aLog("\n//////////" + str(boardsDone) + "//////////" + str(archivesDone) + "//////////" + str(threadsDone) + "//////////" + board + "//////////" + currentjson['archive'] + "//////////" + str(length) + "//////////" + sectitle)
				thisHeadingEnd = s.find(twoln, (cursor+len(lntwo)))
				sectitle = s[cursest:thisHeadingEnd]
				if (len(sectitle) > 2000):
					longTitleCount += 1
					aLog("\n\n\n")
					aLog("\nLONGTITLE FOUND (" + str(len(sectitle)) + ") B: " + str(boardsDone) + " / A: " + str(archivesDone) + " / T: " + str(threadsDone) + " (" + board + " / archive " + currentjson['archive'] + ") length: " + str(length) + " / " + sectitle[0:100])
					aLog("\n* [http://en.wikipedia.org/w/index.php?title=" + boards[board]['archive'] + currentjson['archive'] + "&action=edit]")
				sectitle = sectitle.replace(lntwo + " ", "").replace(" " + twoln, "").replace(two, "").replace("\n", "")
				threadsDone += 1
				cursor = thisHeadingEnd
			else:
				cursor = s.find(twoln, cursest)
			if cursor == -1:
				break;


#	Note to self, 2021 November 9: There are currently 282 sections with "headings" longer than 2,000 characters. This is probably a parsing bug.



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
aLog("\nRun over: " + str(datetime.now(timezone.utc)) + "\n")
aLog("Run successful. Processed " + str(boardsDone) + " boards, " + str(archivesDone) + " archives, " + str(threadsDone) + " threads.")
aLog("\n     Long titles: " + str(longTitleCount) + " / bad stamps: " + str(badStamps) + " / null entries: " + str(nullEntries))
con.commit()