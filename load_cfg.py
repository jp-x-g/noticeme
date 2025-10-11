import sys
import traceback
import os
import tomllib
from pathlib import Path
# From this same project
import version


def boards(boardPath="cfg/boards.toml", verbose=False):
	try:
		with open(f"{boardPath}", "rb") as file:
			if verbose:
				print(f"Successfully opened {boardPath}.")
			return tomllib.load(file)
	except FileNotFoundError:
		print(f"Error: {boardPath} not found.")
		sys.exit(1)
	except tomllib.TOMLDecodeError:
		print(f"Error: Invalid TOML format in {boardPath}.")
		sys.exit(1)

def namespaces(namesPath="cfg/namespaces.toml", verbose=False):
	try:
		with open(f"{namesPath}", "rb") as file:
			if verbose:
				print(f"Successfully opened {namesPath}.")
			return tomllib.load(file)
	except FileNotFoundError:
		print(f"Error: {namesPath} not found.")
		sys.exit(1)
	except tomllib.TOMLDecodeError:
		print(f"Error: Invalid TOML format in {namesPath}.")
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

if __name__ == "__main__":
	print("""This file shouldn't be called by itself.""")
	print("""It only exists to provide functions to other programs.""")
	print("""Functions:""")
	print("""     load_cfg.boards(boardPath="cfg/boards.toml")""")
	print("""     load_cfg.namespaces(boardPath="cfg/namespaces.toml")""")
	print("""     load_cfg.file(filename="load_cfg.py")""")
	print("""Here's the output of running those:""")
	boards(verbose=True)
	namespaces(verbose=True)
	file(verbose=True)
	sys.exit(1)