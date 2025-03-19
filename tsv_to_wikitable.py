#! /usr/bin/python
# -*- coding: utf-8 -*-
# JPxG, 2023 January 14
# Takes a TSV as input and outputs a simple, sortable wikitable.
import sys
import os

def convert(
	inputtext   = None,
	output      = None,
	rotate      = False,
	skipheader  = False,
	classes     = "wikitable sortable",
	attrs       = None,
	headerattrs = None,
	rowattrs    = None,
	altattrs    = None
	):
	
	data = inputtext.strip().split("\n")
	if not data:
		print("Error: Couldn't read data.")
		return "Error: Couldn't read data."

	table_data = [row.split("\t") for row in data]

	#if rotate:
	#	table_data = list(map(list, zip(*table_data)))  # Transpose table
	rows, cols = len(table_data), len(table_data[0])
	if rotate:
		data = [[table_data[row][col] for row in range(rows)] for col in range(cols)]
		cols, rows = rows, cols

	print(f"Processing input: {rows} rows of {cols} columns.")
	
	r = "!"
	if skipheader == True:
		r = "|"
	# If we're skipping the header we will just format the top row as a normal table.

	stringy  = '{|class="' + str(classes) + '"'
	if attrs is not None:
		stringy += f' {attrs}'
	stringy += "\n"
	for n in table_data[0]:
		if headerattrs is not None:
			stringy += f'{r} {headerattrs} | {str(n)}\n'
		else:
			stringy += f"{r} {str(n)}\n"

	# Four possible cases for rowattrs and altattrs.
	if rowattrs is not None:
		if altattrs is not None:
			altrows = [f" {rowattrs}", f" {altattrs}"] # 11: Two different sets of attributes alternate.
		else:
			altrows = [f" {rowattrs}", f" {rowattrs}"] # 10: Every row has the same attributes.
	else:
		if altattrs is not None:
			altrows = [""            , f" {altattrs}"] # 01: Alternating row attributes, but no normal ones.
		else:
			altrows = [""            , ""            ] # 00: No attributes specified whatsoever.

	for row in table_data[1:]:
		strangy = f"|-{altrows[0]}\n"
		for cell in row:
			strangy += f"| {cell}\n"
		stringy += strangy
		altrows.reverse()

	stringy += "|}"

	#print(stringy)
	if output is None:
		return stringy
	if output is not None:
		f = open(output, "w")
		f.write(str(stringy))
		f.close()
		print("")
		print(f"Saved to: {output}")
		exit()

if (__name__ == "__main__"):
	print("TSV to Wikitable V2.0, JPxG March 2025")

	helpstring = """
    convert(input_file, output_file, classes, style, headerstyle, cellstyle, rotate)
Converts input file to Wikitable.
Each row of the TSV (linebreak-separated) will be a row of the table.
Defaults are input.txt and output.txt.
Usage should be like this:
    python3 main.py uglytext.txt nicetable.txt

If calling convert(), there are optional additional keyword arguments:
    rotate      - Transpose (top left stays put, rows become cols & vice versa)
    skipheader  - Format all rows as normal rows
    classes     - Classes to apply to whole table (default 'wikitable sortable')
    attrs       - Attribute string of any sort, to apply to the whole table e.g.
                    style="hoomba: baroomba;" baba="booey"
    headerattrs - Same, but to apply to just the header row
    rowattrs    - Or to apply to each row of the rest of the table
    altattrs    - Or to every-other-row (alternates with rowattrs, or default)
"""


	if len(sys.argv) == 1:
		with open("input.txt", "r") as f:
			data = f.read()
		convert(data, "output.txt")
#		convert(data, "output.txt",	
#			rotate      = True,
#			skipheader  = True,
#			classes     = "wikitable sortable plainlinks",
#			attrs       = "style='font-family: monospace;'",
#			headerattrs = "style='background:#0FF'",
#			rowattrs    = "style='background:#FF0'",
#			altattrs    = "style='background:#F0F'")
		exit()
	else:
		if (sys.argv[1] == "-h") or (sys.argv[1] == "--help") or (sys.argv[1] == "help"):
			print(helpstring)
			exit()
		else:
			if len(sys.argv) == 2:
				with open(str(sys.argv[1]), "r") as f:
					data = f.read()
				convert(data, "output.txt")
				exit()
			if len(sys.argv) == 3:
				with open(str(sys.argv[1]), "r") as f:
					data = f.read()
				convert(data, str(sys.argv[2]))
				exit()
			print("Error: too many arguments provided.")
			print(helpstring)
			exit()


