import requests
import time
import sys
from datetime import datetime
import version
# From this project
import load_cfg

httpApi = "https://en.wikipedia.org/w/api.php"

def fetch(page, namespace="0"):
    """Fetches the first revision timestamp for a given page.
    Takes page name as single unnamed argument.
    Optionally, you can give a 'namespace' arg with its number."""
    namespace = str(namespace)
    if namespace != "0":
    	namespaces = load_cfg.namespaces()
    	page = f"{namespaces['number'][namespace]}:{page}"
    print(f"Fetching first revision for: {page}")
    params = {
        "action" : "query",
        "format" : "json",
        "titles" : page,
        "prop"   : "revisions",
        "rvlimit": 1,
        "rvdir"  : "newer",
        "rvprop" : "timestamp"
    }
    response = requests.get(httpApi, params=params, headers=version.headers())
    
    if response.status_code == 200:
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "revisions" in page_data:
                print(f"                             {page_data["revisions"][0]["timestamp"]}")
                return page_data["revisions"][0]["timestamp"]
            else:
            	print("                             Could not get revisions from HTTP response.")
            	return page_data
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python first_revision.py pagename")
        sys.exit(1)

    page = sys.argv[1]
    fetch(page)