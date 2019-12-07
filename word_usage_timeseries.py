import numpy as np
import requests
import sys
import time
from util import *
from matplotlib import pyplot as plt

subreddit = 'climateskeptics'
if len(sys.argv) > 1:
    subreddit = sys.argv[1]


author = None
words = ['global warming', 'climate change']
endpoint = 'comment'

reference_time_series = []
# reference_wordcount = []
time_series = {}
for w in words:
    time_series[w] = []

def build_timeseries(content):
    for c in content:
        for w in words:
            # check if the word is in the title, body or selftext
            if ('title' in c and w in c['title'].lower())\
            or ('selftext' in c and w in c['selftext'].lower())\
            or ('body' in c and w in c['body'].lower()):
                time_series[w].append(c['created_utc'])

        # also maintain a reference of all content timestamps so that
        # we can compare the word frequency
        reference_time_series.append(c['created_utc'])

# def save_words(content):
#     for c in content:


# def build_wordcount(content):
#     for c in content:

#         ref_count = 0
#         count = {}

#         for field in ['title', 'selftext', 'body']:
#             if field in c:
#                 ref_count += len(c[field].split())
#                 for w in words:
#                     count += c[field].count(w)



#         reference_wordcount.append([c['created_utc'], ])

def plot_histograms(num_bins):
    start_time = min(reference_time_series)
    end_time = max(reference_time_series)
    bins = np.linspace(start_time, end_time, num_bins)

    ref = np.histogram(reference_time_series, bins)[0]
    for w in words:
        hist = np.histogram(time_series[w], bins)[0]
        plt.plot(utc_to_year(bins[:-1]), hist.astype(float)/ref*100, label=w)

    plt.xlabel('Post Date (yr)')
    plt.ylabel('Percentage of posts containing word')
    plt.title('Word usage over time for r/{} {}s'.format(subreddit, endpoint))
    plt.legend()
    plt.plot()
    plt.show()


params = {
    'subreddit': subreddit,
    'sort': 'created_utc',
    'size': 1000,
    'params': int(time.time())
}
if author is not None: params['author'] = ','.join(author)


try: # wrap in a try-except so we can stop early
    while True:
        content = pushshift_get(endpoint, params)
        if content is None: continue
        elif len(content) == 0: break
        build_timeseries(content)
        # move back in time through the content
        params['before'] = content[-1]['created_utc']

except KeyboardInterrupt:
    print('Stopping at {}'.format(params['before']))


for w in words:
    print('Got {} from {}'.format(len(time_series[w]), w))

plot_histograms(100)