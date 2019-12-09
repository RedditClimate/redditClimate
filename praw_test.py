import os
import praw
from util import *
import pickle

reddit = praw.Reddit(client_id='KRHdsxBD5oQpOw',
                     client_secret='YixSmgF0aNeAtOTZPpwhX1qfDVo',
                     user_agent='testscript by /u/6S898')


subreddit_files = ['subreddits/' + f for f in os.listdir('subreddits')]
list_of_subreddits = load_set_from_list_of_files(subreddit_files)

j = {}

for subreddit in list_of_subreddits:
	try:
		moderators = list(reddit.subreddit(subreddit).moderator())
		j[subreddit] = [m.name for m in moderators]
	except Exception as e:
		print(subreddit)
		print(e)
		j[subreddit] = []

output_filename = 'generated_data/moderator_json.pkl'
with open(output_filename, 'wb') as f:
	pickle.dump(j, f)