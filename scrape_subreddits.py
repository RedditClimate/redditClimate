""" pull a list of subreddits where posts have been made about any of the
listed words
"""

import numpy as np
import pickle
import requests
import sys
import time
from util import *

words = [
    'climate change',
    'global warming',
    'sea level rise',
    'greenhouse gas',
    'emmissions',
    'polution',
    'fossil fuels',
    'renewable',
    'ipcc'
][:1]

endpoint = 'submission'

def format_for_request(words):
    return ','.join([w.replace(' ', '_').lower() for w in words])

subreddits = set()
def accumulate(content):
    subreddits.update(c['subreddit'].lower() for c in content)
    print(len(subreddits))


params['q'] = format_for_request(words)
params['before'] = int(time.time())

try: # wrap in a try-except so we can stop early
    while True:
        content = pushshift_get(endpoint, params)
        if content is None:
            continue
        elif len(content) == 0:
            print('We\'re out!')
            break
        else:
            accumulate(content)
            # move back in time through the content
            params['before'] = content[-1]['created_utc']

except KeyboardInterrupt:
    print('Stopping at {}'.format(params['before']))


filename = 'subreddits/scraped.txt'

with open(filename, 'w') as f:
    f.write('\n'.join(sorted(subreddits)))
