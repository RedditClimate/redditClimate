""" scrape all the recent posters in a subreddit
"""

import numpy as np
import pickle
import requests
import sys
import time
from util import *

# iterate backwards in time and to get a list of authors that have
# posted in the subreddit
def get_authors(subreddit, endpoint='comment', max_num_authors=None):
    params = {
        'subreddit': subreddit,
        'sort': 'created_utc',
        'size': 1000,
        'before': int(time.time())
    }

    authors = set()
    more_to_get = True # true until we run out of content

    while more_to_get and len(authors) < max_num_authors:
        url = get_url(pushshift_url, endpoint, params)

        request_succeeded = False
        while not request_succeeded:
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    request_succeeded = True
                    resp_json = resp.json()
                    # if the json is empty, we've completed the search
                    if len(resp_json['data']) == 0:
                        more_to_get = False
                    # otherwise append the results to our growing list of content
                    else:
                        content_authors = [c['author'] for c in resp_json['data']]
                        authors.update(content_authors)
                        params['before'] = resp_json['data'][-1]['created_utc']

                        # add a bunch of authors to ignore to speed up the search
                        if len(authors) > 250 and 'author' not in params:
                            to_ignore = list(authors)[:250]
                            params['author'] = '!' + ',!'.join(to_ignore)

                else:
                    print(resp.status_code, '\n', resp.content)
                    print('Request for %s failed' % url)
                    time.sleep(1)
            except Exception as e:
                print(e)

        time.sleep(60.0/rate_limit)

    # sort and clip
    authors = sorted(authors)
    if max_num_authors is not None:
        authors = authors[:max_num_authors]

    return authors


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print('scrape_members.py [subreddit] [output_filename]')
		sys.exit(1)

	subreddit = sys.argv[1]
	output_filename = sys.argv[2]

	authors = get_authors(subreddit, max_num_authors=1000)

	with open(output_filename, 'w') as f:
		print('Saving to {}'.format(output_filename))
		f.write('\n'.join(authors))
