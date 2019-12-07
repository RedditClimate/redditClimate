import numpy as np
import pickle
import requests
import sys
import time
from util import *

"""
Load the set of users and subreddits from the given files. 
"""

users_files = ['comment_authors_climateskeptics.txt', 'comment_authors_green.txt']
subreddit_files = ['subreddits/big_list_of_subreddits.txt']


# iterate backwards in time and to get everything
def get_all(subreddit, endpoint='comment', author=None):
    params = {
        'subreddit': subreddit,
        'sort': 'created_utc',
        'size': 1000,
        'params': int(time.time())
    }
    if author is not None: params['author'] = ','.join(author)

    content = []
    more_to_get = True # true until we run out of content

    while more_to_get:
        url = get_url(pushshift_url, endpoint, params)

        request_succeeded = False
        while not request_succeeded:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    request_succeeded = True
                    resp_json = resp.json()
                    # if the json is empty, we've completed the search
                    if len(resp_json['data']) == 0:
                        more_to_get = False
                    # otherwise append the results to our growing list of content
                    else:
                        content += resp_json['data']
                        params['before'] = resp_json['data'][-1]['created_utc']
                        print(params['before'])

                else:
                    print(resp.status_code, '\n', resp.content)
                    print('Request for %s failed' % url)
                    time.sleep(1)
            except Exception as e:
                print(e)

        time.sleep(60.0/rate_limit)

    return content


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please supply a filename to save the matrix.')
        sys.exit(1)
    
    output_filename = sys.argv[1]

    users = list(load_set_from_list_of_files(users_files))
    subreddits = list(load_set_from_list_of_files(subreddit_files))
    subreddits = [r[2:] for r in subreddits] # strip the r/
    num_users = len(users)
    num_subreddits = len(subreddits)

    is_in = np.zeros([num_users, num_subreddits], dtype=bool)
    user_batch_size = 250
    num_batches = np.ceil(num_users/user_batch_size).astype(int)

    for i, subreddit in enumerate(subreddits):
        print('Starting subreddit, {}'.format(subreddit))
        for j in range(num_batches):
            j_lower = j * user_batch_size
            j_upper = min((j+1) * user_batch_size, num_users)

            user_batch = users[j_lower:j_upper]

            comments = get_all(subreddit, endpoint='comment', author=user_batch)
            submissions = get_all(subreddit, endpoint='submission', author=user_batch)
            print('Collected {} comments and {} submissions'.format(len(comments), len(submissions)))

            comment_authors = set([c['author'] for c in comments])
            submission_authors = set([s['author'] for s in submissions])

            is_commenter = np.array([u in comment_authors for u in user_batch])
            is_submitter = np.array([u in submission_authors for u in user_batch])

            is_in[j_lower:j_upper, i] = np.logical_or(is_submitter, is_commenter)

        print('Overlap is {} for subreddit, {}'.format(is_in[:,i].mean(), subreddit))

    with open(output_filename, 'wb') as f:
        print('Saving to {}'.format(output_filename))
        pickle.dump((users, subreddits, is_in), f)
