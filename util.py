import requests
import time

pushshift_url = 'https://api.pushshift.io/reddit/search'

rate_limit = 120

default_params = {
    'size': 1000,
    'sort': 'created_utc',
    'filter': 'subreddit,author,body,title,selftext,created_utc,url'
}

def utc_to_year(utc):
    return utc / 31556926. + 1970

# take a param dictionary and create the param string
def param_string(params):
    return "&".join(f"{param}={val}" for param,val in params.items())

# build a URL given the endpoint and params
def get_url(URL, endpoint, params):
    return URL + '/' + endpoint + '/?' + param_string(params)

# the pushshift server is ratelimited. Get that limit
def get_rate_limit():
    resp = requests.get('https://api.pushshift.io/meta')
    if resp.status_code == 200:
        return resp.json()['server_ratelimit_per_minute']
    else:
        print('Rate limit request failed with code:', resp.status_code)
        return 60 # return a conservative rate

# load a set of elements from a list of files containing elements on each line
def load_set_from_list_of_files(list_of_files, sort=True):
    items = set()
    for filename in list_of_files:
        with open(filename) as f:
            items.update([line.strip().lower() for line in f.readlines()])

    if sort:
        return sorted(items)
    else:
        return list(items)

def remove_r_slash(list_of_subreddits):
    return [r[2:] for r in list_of_subreddits]


def sort_list_in_file(filename):
    l = load_set_from_list_of_files([filename], sort=True)
    with open(filename, 'w') as f:
        f.write('\n'.join(l))

def pushshift_get(endpoint, params={}, max_retries=5):
    url = get_url(pushshift_url, endpoint, params)

    for _ in range(max_retries):
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                request_succeeded = True
                resp_json = resp.json()
                return resp_json['data']

            else:
                print(resp.status_code, '\n', resp.content)
                print('Request for %s failed' % url)
                time.sleep(1)
        except Exception as e:
            print(e)

    return None


# iterate backwards in time and to get everything
def pushshift_accumulate(subreddit, endpoint='comment', params=default_params):
    params['created_utc'] = int(time.time())
    params['sort'] = 'created_utc'

    content = []
    while True:

        resp = pushshift_get(endpoint, params)
        if resp is None:
            continue
        elif resp == []:
            break
        else:
            content += resp
            params['before'] = resp[-1]['created_utc']

        # request_succeeded = False
        # while not request_succeeded:
        #     try:
        #         resp = requests.get(url, timeout=5)
        #         if resp.status_code == 200:
        #             request_succeeded = True
        #             resp_json = resp.json()
        #             # if the json is empty, we've completed the search
        #             if len(resp_json['data']) == 0:
        #                 more_to_get = False
        #             # otherwise append the results to our growing list of content
        #             else:
        #                 content += resp_json['data']
        #                 params['before'] = resp_json['data'][-1]['created_utc']
        #                 print(params['before'])

        #         else:
        #             print(resp.status_code, '\n', resp.content)
        #             print('Request for %s failed' % url)
        #             time.sleep(1)
        #     except Exception as e:
        #         print(e)

        # time.sleep(60.0/rate_limit)

    return content