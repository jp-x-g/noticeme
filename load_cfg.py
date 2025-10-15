import sys
import traceback
import os
import tomllib
from pathlib import Path
# From this same project
import version


def boards(boardPath="cfg/boards.toml", verbose=False):
	return toml(boardPath, verbose=verbose)

def toml(path, verbose=False):
	try:
		return tomllib.loads(file(path, verbose=verbose))
	except tomllib.TOMLDecodeError:
		print(f"Error: Invalid TOML format in {boardPath}.")
		sys.exit(1)

def file(filename="load_cfg.py", verbose=False):
	try:
		with open(filename, "r", encoding="utf-8") as file:
			if verbose:
				print(f"Successfully opened {filename}.")
			return file.read()
	except FileNotFoundError:
		print(f"Error: {filename} not found.")
		sys.exit(1)
	except:
		print(f"Error: Could not process {filename}.")
		sys.exit(1)

def namespaces(verbose=False):
	if verbose:
		print("Successfully retrieved namespaces.")
	return {
		"number": {
			"0"                      : "",
			"1"                      : "Talk",
			"2"                      : "User",
			"3"                      : "User talk",
			"4"                      : "Wikipedia",
			"5"                      : "Wikipedia talk",
			"6"                      : "File",
			"7"                      : "File talk",
			"8"                      : "MediaWiki",
			"9"                      : "MediaWiki talk",
			"10"                     : "Template",
			"11"                     : "Template talk",
			"12"                     : "Help",
			"13"                     : "Help talk",
			"14"                     : "Category",
			"15"                     : "Category talk",
			"100"                    : "Portal",
			"101"                    : "Portal talk",
			"118"                    : "Draft",
			"119"                    : "Draft talk",
			"126"                    : "MOS",
			"127"                    : "MOS talk",
			"710"                    : "TimedText",
			"711"                    : "TimedText talk",
			"828"                    : "Module",
			"829"                    : "Module talk",
			"1728"                   : "Event",
			"1729"                   : "Event talk",

			"108"                    : "Book",
			"109"                    : "Book talk",
			"442"                    : "Course",
			"443"                    : "Course talk",
			"444"                    : "Institution",
			"445"                    : "Institution talk",
			"446"                    : "Education Program",
			"447"                    : "Education Program talk",
			"2300"                   : "Gadget",
			"2301"                   : "Gadget talk",
			"2302"                   : "Gadget definition",
			"2303"                   : "Gadget definition talk",
			"2600"                   : "Topic",
			"2601"                   : "Topic talk",

			"-1"                     : "Special",
			"-2"                     : "Media"
			},
		"name": {
			""                       : 0,
			"Talk"                   : 1,
			"User"                   : 2,
			"User talk"              : 3,
			"Wikipedia"              : 4,
			"Wikipedia talk"         : 5,
			"File"                   : 6,
			"File talk"              : 7,
			"MediaWiki"              : 8,
			"MediaWiki talk"         : 9,
			"Template"               : 10,
			"Template talk"          : 11,
			"Help"                   : 12,
			"Help talk"              : 13,
			"Category"               : 14,
			"Category talk"          : 15,
			"Portal"                 : 100,
			"Portal talk"            : 101,
			"Draft"                  : 118,
			"Draft talk"             : 119,
			"MOS"                    : 126,
			"MOS talk"               : 127,
			"TimedText"              : 710,
			"TimedText talk"         : 711,
			"Module"                 : 828,
			"Module talk"            : 829,
			"Event"                  : 1728,
			"Event talk"             : 1729,
			
			"Book"                   : 108,
			"Book talk"              : 109,
			"Course"                 : 442,
			"Course talk"            : 443,
			"Institution"            : 444,
			"Institution talk"       : 445,
			"Education Program"      : 446,
			"Education Program talk" : 447,
			"Gadget"                 : 2300,
			"Gadget talk"            : 2301,
			"Gadget definition"      : 2302,
			"Gadget definition talk" : 2303,
			"Topic"                  : 2600,
			"Topic talk"             : 2601,
			
			"Special"                : -1,
			"Media"                  : -2,
			
			"WP"                     : 4,
			"Project"                : 4,
			"WT"                     : 5,
			"Project talk"           : 5,
			"Image"                  : 6,
			"Image talk"             : 7,
			"TM"                     : 10
			}
	}
if __name__ == "__main__":
	print("""This file shouldn't be called by itself.""")
	print("""It only exists to provide functions to other programs.""")
	print("""Functions:""")
	print("""     load_cfg.boards(boardPath="cfg/boards.toml")""")
	print("""     load_cfg.namespaces()""")
	print("""     load_cfg.file(filename="load_cfg.py")""")
	print("""Here's the output of running those:""")
	boards(verbose=True)
	namespaces(verbose=True)
	file(verbose=True)
	sys.exit(1)