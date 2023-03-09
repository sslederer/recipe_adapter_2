import requests
from bs4 import BeautifulSoup
from retrying import retry
import time

@retry(stop_max_attempt_number=3)
def get_metadata(url):
    
    #extract metadata to get image
    # print('requesting')
	source = requests.get(url)
	# print(type(source.status_code), source.status_code)
	start = time.time()
	if True:
		source = source.text
	print('trying to parse')
	soup = BeautifulSoup(source, features="html.parser")
	result = {}
	print('parsing took', time.time()-start)
	start = time.time()
	def find_metadata(metadata_key):
		metadata = soup.find("meta", attrs={'property': 'og:' + metadata_key})
		if metadata:
			result[metadata_key] = metadata["content"]
	
	find_metadata("site_name")
	find_metadata("title")
	find_metadata("image")
	find_metadata("description")
	print('forming result took', time.time()-start)
	return result