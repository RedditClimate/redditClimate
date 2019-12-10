# Analyzing Climate Change Discourse and Communities on Reddit

## Introduction

In this project, we set out to explore climate skepticism as it manifests on [Reddit](https://www.reddit.com/). Our goals for this project are two-fold:

 1. Gain a deeper understanding of climate skepticism in a data-driven way
 2. Empower others to use Reddit data for research

## Background

The role of humans in climate change was predicted over 100 years ago by Svante Arrhenius [[ref]](https://www.rsc.org/images/Arrhenius1896_tcm18-173546.pdf), and since then a formidable body of scientific evidence has accumulated leading over 97% of scientists to conclude that human activity has a significant impact on the climate [[ref]](https://skepticalscience.com/global-warming-scientific-consensus-intermediate.htm). An ever-improving collection of climate models even allow us to estimate the exact degree to which we will cause the planet to warm, and the details of how this will impact specific ecosystems and industries. Increasingly, these predictions are being validated by an increase in extreme weather events, collapsing ecosystems, and warming temperatures around the globe.

Despite the overwhelming evidence of anthropogenic global warming (AGW), in general we have been incredibly slow to take significant action to mitigate our impact on the climate. There are **many** factors contributing to this hesitation — one of which is widespread skepticism or denial of the reality of AGW. For certain individuals and companies (most notably fossil-fuel industries), avoiding climate action is a profitable strategy in the short term. As a result, they have mounted numerous campains to spread misinformation and discredit climate science [[ref]](https://www.merchantsofdoubt.org/).

Moving the needle on climate action will likely require us to convince climate skeptics of the reality and severity of this issue. Before we can do so effectively, it is critical to understand why and how people deny AGW. This is by no means a novel research endevour, and we discuss a number of related studies in the [Related Work](#-related-work) section.


## Pushshift API

Reddit is special among the large social-media platforms in that it provides a free, extensive API for interacting with content on the platform. The API exposes nearly all the functionality that a regular user would have when browsing reddit.


The pushshift API has two active endpoints, which can be found at:
1. https://api.pushshift.io/reddit/search/comment
2. https://api.pushshift.io/reddit/search/submission

Try following these links and inspect the results in your browser.

If we go to https://api.pushshift.io/meta, we'll see that the Pushshift API has a rate limit of 120 requests per minute - that's one every 0.5 seconds. Therefore, we will want to slow our requests down by waiting 0.5 seconds between requests.

The pushshift API caps the number of results returned for a single request to 1000. Each result contains data about either a comment or a submission depending on the endpoint queried.

## Experiments

### Making Simple Queries

Let's start by using python to programatically make a request.

First, we'll want to import python's `requests` library for making API requests, as well as the `time` library so that we can make sure not to exceed the Pushshift API's rate limit.
```python
import requests
import time
```

Now, let's write a function called `query` which takes in as input the name of the endpoint, which should be `"comment` or `"submission"`, as well as a dictionary of query parameters. The function should query the endpoint with the given parameters and return the result as a list of dictionaries.

```python
def query(endpoint, params):
    
    params_string = "&".join(f"{param}={val}" for param,val in params.items())
    url = f"https://api.pushshift.io/reddit/search/{endpoint}/?{params_string}"

    r = requests.get(url = url)
    data = r.json()
    return data["data"]
```
This works great if we want up to 1000 results, but if we try to ask for more than 1000 results, this will not work because of pushshift's size limit. This means that we'll have to make multiple requests until we have the desired number of results. For example, if we want to get 2500 results, then we can make 3 API calls, querying for 1000 results in the first 2, and 500 results in the third.

We'll also want to call time.sleep

```python
def query_n(category, params, n = 1000):
    params.update({"sort_type": "created_utc", "sort":"desc", "size":n})

    results = []
    while len(results) < n:
        query_res = query(category, {**params, "before": results[-1]["created_utc"] if results else int(time.time()) })
        if not query_res:
            return results
        results.extend(query_res)
        time.sleep(0.5)
    return results
```

Great! Now we're ready to make some requests.


### Topic Modelling




### Clustering

### Word usage trends

![Comments in the subreddit r/Green that mention climate change or global warming](figures/green_comments_over_time.png)

### Linking

### Sentiment Analysis

## Discussion

## Related Work

