import sys
import traceback
import os
import time
import tomllib
import requests
from pathlib import Path
from datetime import datetime, timezone

print("Hi!")

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

boards = load_boards()

for board in boards:
	print(board['short'])
	print(board['name'])
	print(board['page'])
	print(board['archive'])

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
pages.mkdir(mode=0o777, exist_ok=True)

########################################
# Function to log to the logfile.
########################################

def aLog(argument):
    try:
        with open(logfile, 'a', encoding="utf-8") as dalog:
            dalog.write(argument + "\n")
        print(argument)
    except FileNotFoundError:
        with open(logfile, 'w', encoding="utf-8") as dalog:
            dalog.write(f"\nSetting up runtime log at {datetime.now(timezone.utc)}\n" + argument)
        print("Setting up runtime log.")
        print(argument)

########################################
# Main loop: iterates over every board.
########################################

for board, details in boards.items():
    print(f"Processing {details['name']}")
    boardPath = Path(pages, board)
    boardPath.mkdir(mode=0o777, exist_ok=True)

    archiveNumber = 1
    if details['name'] == "Wikipedia:Arbitration_Committee/Noticeboard":
        archiveNumber = 0

    while True:
        query = "|".join(f"{details['archive']}{archiveNumber + i}" for i in range(batchSize))
        archiveNumber += batchSize
        print(query)
        time.sleep(sleepTime)

        response = requests.get(httpApi, params={
            "action": "query",
            "prop": "revisions",
            "rvslots": "*",
            "rvprop": "content",
            "formatversion": "2",
            "format": "json",
            "titles": query
        })

        data = response.json()
        brokenYet = False

        for page in data.get("query", {}).get("pages", []):
            if 'missing' in page:
                brokenYet = True
            else:
                number = page['title'].split('Archive')[-1].strip().replace(" ", "").replace("_", "")
                content = page['revisions'][0]['slots']['main']['content']
                
                pageJson = {
                    "board": board,
                    "archive": number,
                    "title": page['title'],
                    "pageid": page['pageid'],
                    "scrapedate": str(datetime.now(timezone.utc)),
                    "content": content
                }
                
                pagePath = Path(boardPath, f"{board}-{number}")
                with open(pagePath, 'w', encoding="utf-8") as pageFile:
                    json.dump(pageJson, pageFile, indent=2, ensure_ascii=False)

        if brokenYet:
            break
        print("////////////")

print("Bye!")
