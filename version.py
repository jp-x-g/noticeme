def str():
	return "1.0"

def summary():
	return f"NoticeMe/{str()} (https://en.wikipedia.org/wiki/User:JPxG)"

def headers():
	return {"User-Agent": f"{summary()}"}

# The only function of this script is to return the version string and/or user-agent headers.