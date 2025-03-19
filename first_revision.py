import requests
import time
import sys
from datetime import datetime

httpApi = "https://en.wikipedia.org/w/api.php"

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

def fetch(page, namespace="0"):
    """Fetches the first revision timestamp for a given page.
    Takes page name as single unnamed argument.
    Optionally, you can give a 'namespace' arg with its number."""
    namespace = str(namespace)
    if namespace != "0":
    	namespaces = load_namespaces()
    	page = f"{namespaces['number'][namespace]}:{page}"
    print(f"Trying to fetch first revision for '{page}'.")
    params = {
        "action" : "query",
        "format" : "json",
        "titles" : page,
        "prop"   : "revisions",
        "rvlimit": 1,
        "rvdir"  : "newer",
        "rvprop" : "timestamp"
    }
    response = requests.get(httpApi, params=params)
    
    if response.status_code == 200:
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "revisions" in page_data:
                return page_data["revisions"][0]["timestamp"]
            else:
            	print("Could not retrieve revisions from HTTP response.")
            	return page_data
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python first_revision.py pagename")
        sys.exit(1)

    page = sys.argv[1]
    fetch(page)