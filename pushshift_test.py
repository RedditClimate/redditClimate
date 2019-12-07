import json
import requests
import time
import numpy as np
from collections import deque

pushshift_url = 'https://api.pushshift.io/reddit/search/'

# read in the list of relevant reddits
notable_subreddits = [line[2:].strip() for line in open('notable_subreddits.txt').readlines()]

def param_string(params):
    return "/?" + "&".join(f"{param}={val}" for param,val in params.items())

def get_authors():
    subreddit = 'climateskeptics'
    endpoint = 'comment'

    authors = set()
    # get comments before before_utc (so we can move back in time)
    before_utc = time.time()
    while True:
        # create the URL for the GET request
        URL = pushshift_url + endpoint + '/?'
        args = ['subreddit={}'.format(subreddit),
                'size=1000',
                'sort_type=created_utc',
                'before={}'.format(int(before_utc))]

        for a in args:
            URL += '&' + a

        # make a get request
        response = requests.get(URL)
        if response.status_code == 200:
            j = json.loads(response.content)
            if len(j['data']) == 0: break

            new_authors = [submission['author'] for submission in j['data']]
            authors.update(new_authors)

            before_utc = j['data'][-1]['created_utc']
            print(before_utc, len(authors))

        else:
            print('Request for %s failed' % URL)

    filename = endpoint + '_authors_' + subreddit + '.txt'
    print('Saving to', filename)
    with open(filename, 'w+') as f:
        f.write('\n'.join(authors))


def authors_in_other_subreddits():
    rl = RateLimiter()

    subreddit = 'climateskeptics'
    endpoint = 'submission'

    URL = pushshift_url + endpoint

    filename = endpoint + '_authors_' + subreddit + '.txt'
    with open(filename) as f:
        authors = [line.strip() for line in f.readlines()]

    num_authors = len(authors)
    authors_batch_size = 500

    is_in = np.zeros([len(notable_subreddits), len(authors)], dtype=bool)
    print(is_in.shape)

    params = {
        'subreddit': None,
        'size': 1000,
        'author': None,
        'sort': 'created_utc',
        'before': None
    }

    for i, subreddit in enumerate(notable_subreddits):
        j = 0
        while j < num_authors:
            j_max = min(j + authors_batch_size, num_authors-1)
            authors_batch = authors[j:j_max]
            params['subreddit'] = subreddit
            params['author'] = ','.join(authors_batch)
            params['before'] = int(time.time())

            authors_in_subreddit = set()
            more_comments_to_get = True
            while more_comments_to_get:

                this_url = URL + param_string(params)
                success = False
                while not success: # if the request fails, it's probably because we hit the rate limiter, so retry
                    response = requests.get(this_url)
                    if response.status_code == 200:
                        content_json = response.json()
                        # if the json is empty, we've completed the search
                        if len(content_json['data']) == 0:
                            more_comments_to_get = False
                        # otherwise, add the authors to the set, and update the utc so we continue searching
                        else:
                            authors_in_subreddit.update([submission['author'] for submission in content_json['data']])
                            params['before'] = content_json['data'][-1]['created_utc']
                        success = True

                    else:
                        print(response.content)
                        print('Request for %s failed' % this_url)
                        time.sleep(1)

                time.sleep(0.25) # pause for a moment so we dont hit the rate limiter

            mask = np.array([a in authors_in_subreddit for a in authors_batch])
            print(mask.sum() / float(authors_batch_size))
            is_in[i,j:j_max] = mask
            j += authors_batch_size

        print('Done with subreddit,', subreddit)

    return is_in


class RateLimiter:
    def __init__(self, rate=120):
        self.rate = rate
        self.prev = 0
        self.dt = 60./self.rate

    def get(self, URL, params={}):
        t = time.time()
        elapsed = t - self.prev
        if elapsed < self.dt:
            time.sleep(self.dt - elapsed)
            print('sleep')

        self.prev= t
        return requests.get(URL, params=params)




if __name__ == '__main__':
    # get_authors()
    is_in = authors_in_other_subreddits()