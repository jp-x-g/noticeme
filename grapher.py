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
logName			= "log-grapher.txt"
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
# Function to do nothing.
########################################

def derp():
	derp = 1;
	return "derp"

########################################
# Make directories for data to live in.
########################################

data.mkdir(mode=0o777, exist_ok = True)
pages.mkdir(mode=0o777, exist_ok = True)

########################################
# Living in the database, whoa-hoah.
########################################

con = sqlite3.connect(database)
cur = con.cursor()

################################################################################
# Below this are individual graph-logging functions.
################################################################################
################################################################################

def allStatsByBoard():
	####	Board	YYYY-MM	Threads	Avg	Sum	Cmts	Avg
	####	AN	2004-01	0	None	None	None	None
	for board in boards:
		query = ""
		for yyyy in range(2004, 2022):
			for m in range(1,13):
				mm = str(m).zfill(2)
				# Format of lines should be like this:
				# 
	
	
				query = "SELECT COUNT(*) FROM threads WHERE board LIKE '" + board + "' AND date LIKE '" + str(yyyy) + "-" + str(mm) + "%'"
				response = cur.execute(query)
				for i in response:
					threads = str(i).replace("(","").replace(",","").replace(")","")
	
				query = "SELECT AVG(length) FROM threads WHERE board LIKE '" + board + "' AND date LIKE '" + str(yyyy) + "-" + str(mm) + "%'"
				response = cur.execute(query)
				for i in response:
					avgl = str(i).replace("(","").replace(",","").replace(")","")
	
				query = "SELECT SUM(length) FROM threads WHERE board LIKE '" + board + "' AND date LIKE '" + str(yyyy) + "-" + str(mm) + "%'"
				response = cur.execute(query)
				for i in response:
					suml = str(i).replace("(","").replace(",","").replace(")","")
	
	
				query = "SELECT SUM(timestamps) FROM threads WHERE board LIKE '" + board + "' AND date LIKE '" + str(yyyy) + "-" + str(mm) + "%'"
				response = cur.execute(query)
				for i in response:
					sumu = str(i).replace("(","").replace(",","").replace(")","")
	
				query = "SELECT AVG(timestamps) FROM threads WHERE board LIKE '" + board + "' AND date LIKE '" + str(yyyy) + "-" + str(mm) + "%'"
				response = cur.execute(query)
				for i in response:
					avgu = str(i).replace("(","").replace(",","").replace(")","")
	
				aLog("\n" + board + "	" + str(yyyy) + "-" + mm + "	" + threads + "	" + avgl + "	" + suml + "	" + sumu + "	" + avgu)

################################################################################

def allBoardsByBytes():
	firstline = "kbytes"
	for board in boards:
		firstline += "	" + board
	
	aLog("\n" + firstline)
	
	bin = 1000
	
	rlo = 1
	rhi = int((60000 / bin)) + 1
	
	
	for amount in range(rlo,rhi):
		thisline = str(amount)
		for board in boards:
			lo = (amount - 1) * bin
			hi = amount * bin
			query = "SELECT SUM(length) FROM threads WHERE board LIKE '" + board + "' AND length BETWEEN " + str(lo) + " AND " + str(hi)
			response = cur.execute(query)
			for i in response:
				result = str(i).replace("(","").replace(",","").replace(")","")
			thisline += "	" + result
	aLog("\n" + thisline)

################################################################################

def allBoardsByComments():
	###	kbytes	AN	AN3	ANI	AE	BLPN	COIN	DRN	ELN	FTN	NORN	NPOVN	RSN
	
	bin = 1
	
	rlo = 1
	rhi = int((800 / bin)) + 1
	
	for amount in range(rlo,rhi):
		thisline = str(amount)
		for board in boards:
			lo = (amount - 1) * bin
			hi = amount * bin
			query = "SELECT SUM(timestamps) FROM threads WHERE board LIKE '" + board + "' AND timestamps BETWEEN " + str(lo) + " AND " + str(hi)
			response = cur.execute(query)
			for i in response:
				result = str(i).replace("(","").replace(",","").replace(")","")
			thisline += "	" + result
		aLog("\n" + thisline)

################################################################################

def wikiGraphAllByMonth(q, d):
	aLog("\n{{Graph:Chart")
	aLog("\n | type       = line")
	aLog("\n | width      = 4000")
	aLog("\n | height     = 1000")
	aLog("\n | xAxisAngle = -70")
	aLog("\n | xAxisTitle = " + d)
	aLog("\n | legend     =")
	
	# Make the legend.
	boardstring = ""
	y = 0
	for board in boards:
		y += 1
		if y < 10:
			aLog("\n  | y" + str(y) + "Title    = " + board)
		else:
			aLog("\n  | y" + str(y) + "Title   = " + board)

	aLog("\n | x          = ")

	# Labels for x-axis.
	xstring = ""
	for yyyy in range(2004, 2022):
		for m in range(1,13):
			mm = str(m).zfill(2)
			xstring += str(yyyy) + "-" + str(mm) + ","
	xstring = xstring[:-1]
	aLog(xstring)

	# Now we get down to brass tacks and get actual stats.
	y = 0
	for board in boards:
		y += 1
		if y < 10:
			graphstring = "\n | y" + str(y) + "         = "
		else:
			graphstring = "\n | y" + str(y) + "        = "
		query = ""
		for yyyy in range(2004, 2022):
			for m in range(1,13):
				mm = str(m).zfill(2)
				query = q + " board LIKE '" + board + "' AND date LIKE '" + str(yyyy) + "-" + str(mm) + "%'"
				response = cur.execute(query)
				for i in response:
					result = str(i).replace("(","").replace(",","").replace(")","")
					result.replace("None", "0")
				graphstring += str(result) + ","
		graphstring = graphstring[:-1]
		aLog(graphstring)
	aLog("\n}}")

################################################################################

def wikiGraphAllByYear(q, d):
	aLog("\n{{Graph:Chart")
	aLog("\n | type       = line")
	aLog("\n | width      = 4000")
	aLog("\n | height     = 1000")
	aLog("\n | xAxisAngle = -70")
	aLog("\n | xAxisTitle = " + d)
	aLog("\n | legend     =")
	
	# Make the legend.
	boardstring = ""
	y = 0
	for board in boards:
		y += 1
		if y < 10:
			aLog("\n  | y" + str(y) + "Title    = " + board)
		else:
			aLog("\n  | y" + str(y) + "Title   = " + board)

	aLog("\n | x          = ")

	# Labels for x-axis.
	xstring = ""
	for yyyy in range(2004, 2022):
		xstring += str(yyyy).replace("0","O") + ","
	xstring = xstring[:-1]
	aLog(xstring)

	# Now we get down to brass tacks and get actual stats.
	y = 0
	for board in boards:
		y += 1
		if y < 10:
			graphstring = "\n | y" + str(y) + "         = "
		else:
			graphstring = "\n | y" + str(y) + "        = "
		query = ""
		for yyyy in range(2004, 2022):
			query = q + " board LIKE '" + board + "' AND date LIKE '" + str(yyyy) + "%'"
			response = cur.execute(query)
			for i in response:
				result = str(i).replace("(","").replace(",","").replace(")","")
				result.replace("None", "0")
			graphstring += str(result) + ","
		graphstring = graphstring[:-1]
		aLog(graphstring)
	aLog("\n}}")

################################################################################
"""
def wikiGraphInequality(board, bin):
	rlo = 1
	rhi = int((60000 / bin)) + 1
	for board in boards:
		lo = (amount - 1) * bin
			hi = amount * bin
			query = "SELECT SUM(length) FROM threads WHERE board LIKE '" + board + "' AND length BETWEEN " + str(lo) + " AND " + str(hi)
			response = cur.execute(query)
			for i in response:
				result = str(i).replace("(","").replace(",","").replace(")","")
			thisline += "	" + result
	aLog("\n" + thisline)
"""
"""
for each month:
	select sum(length) where length > 1000 and length < 2001



"""
################################################################################
################################################################################

# Main code that actually runs the program.

aLog("\nRunning : " + str(datetime.now(timezone.utc)) + "\n")

#allStatsByBoard()
#allBoardsByBytes()
#allBoardsByComments()


#wikiGraphAllByMonth("SELECT COUNT(*) FROM threads WHERE","Thread count by month")
#wikiGraphAllByMonth("SELECT SUM(length) FROM threads WHERE","Total length by month")
#wikiGraphAllByMonth("SELECT AVG(length) FROM threads WHERE","Average length by month")
wikiGraphAllByYear("SELECT COUNT(*) FROM threads WHERE length > 100000 AND","Threads longer than 100kb")

wikiGraphInequality("ANI", 10000)

con.commit()

aLog("\nGraph rendered. Finished at " + str(datetime.now(timezone.utc)))