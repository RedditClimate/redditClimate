import numpy as np
import requests
import sys
import re
import time
import pickle
from util import *
from urllib.parse import urlparse  
from matplotlib import pyplot as plt


subreddit = 'climateskeptics'
if len(sys.argv) > 1:
    subreddit = sys.argv[1]

endpoint = 'submission'

links = {}
links_to_ignore = ['www.reddit.com', 'www.youtube.com', 'i.redd.it', 'youtu.be']

def get_domain(url):
	return urlparse(url).netloc

def find_url(string): 
    # findall() has been used  
    # with valid conditions for urls in string 
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] |[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string) 
    return [re.split('\.|\/', url)[2] for url in urls]

def count_links_in_submissions(content):
	for c in content:
		if 'url' in c:
			domain = get_domain(c['url'])
	
			if domain in links:
				links[domain] += 1
			else:
				links[domain] = 1

def build_links(subreddit, params=default_params):
	params['subreddit'] = subreddit

	try: # wrap in a try-except so we can stop early
	    while True:
	        content = pushshift_get(endpoint, params)
	        if content is None: continue
	        elif len(content) == 0: break
	        count_links_in_submissions(content)
	        # move back in time through the content
	        params['before'] = content[-1]['created_utc']

	except KeyboardInterrupt:
	    print('Stopping at {}'.format(params['before']))

	print(links)
	return links

def save_links(links):
	with open('generated_data/link_{}.pkl'.format(subreddit), 'wb') as f:
		pickle.dump(links, f)

def analyze_links(filename):
	with open(filename, 'rb') as f:
		links = pickle.load(f)

	urls = list(links.keys())
	counts = np.array([links[url] for url in urls])

	idx = np.argsort(-counts)

	print(subreddit)
	for i in range(10):
		print('{}\t{}'.format(counts[idx[i]], urls[idx[i]]))

if __name__ == '__main__':
	links = build_links(subreddit)
	save_links(links)
	analyze_links('generated_data/link_{}.pkl'.format(subreddit))

