import requests
import sys

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

def wikitext(page, namespace="0"):
	"""Fetches the first revision timestamp for a given page.
	Takes page name as single unnamed argument.
	Optionally, you can give a 'namespace' arg with its number."""
	namespace = str(namespace)
	if namespace != "0":
		namespaces = load_namespaces()
		page = f"{namespaces['number'][namespace]}:{page}"
	print(f"Fetching wikitext for '{page}'.")
	params = {
		"action" : "query",
		"format" : "json",
		"titles" : page,
		"prop"   : "revisions",
		"rvprop": "content",
		"rvslots": "main",
		"formatversion": "2"
	}
	response = requests.get(httpApi, params=params)
	
	if response.status_code == 200:
		data = response.json()
		pages = data.get("query", {}).get("pages", {})
		if pages:
			for page_id, page_data in pages.items():
				if "revisions" in page_data:
				    return page_data["revisions"][0]["slots"]["main"]["content"]
				else:
					print("Could not retrieve page content.")
					return page_data
		else:
			print("No pages returned in query.")
			return data
	else:
		print("Could not get a response.")
		return "Could not get a response."
	return None

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python3 get_page.py pagename")
		sys.exit(1)

	page = sys.argv[1]
	wikitext(page)