from reddit import query_n
from seaborn import sns
from collections import Counter

import matplotlib.pyplot as plt

LEFT_TO_RIGHT = ["nytimes.com",
                 "bbc.com", "huffingtonpost.com", "washingtonpost.com",         
                 "cnn.com",
                 "nbcnews",
                 "news.google.com", "abcnews.go.com",
                 "wsj.com",
                 "foxnews.com",
                 "breitbart.com",
                 ]

def news_domains_by_subreddit(category, subreddits, domains):
    params = {"subreddit": ",".join(subreddits), "domain": ",".join(domains) }
    results = query_n(category, params, n=10000)
    subreddit_counter = Counter([ r["subreddit"] for r in results])

    news_subreddits = [subreddit for subreddit,_ in subreddit_counter.most_common(10)]
    params = {"subreddit": ",".join(news_subreddits), "domain": ",".join(domains) }
    results = query_n(category, params, n=20000)
    subreddit_counter = Counter([ r["subreddit"] for r in results])
    counter = Counter([(r["domain"], r["subreddit"]) for r in results])

    for r in results:
        domain_count = counter[(r["domain"], r["subreddit"])]
        subreddit_total = subreddit_counter[r["subreddit"]]
        r["proportion"] = domain_count/subreddit_total

    return pd.DataFrame.from_records(results)[["subreddit", "domain", "count"]]

def plot_news_domains_by_subreddit(subreddit_domains_df):
    color_palette = sns.color_palette("coolwarm", len(domains))
    plt.subplots(1,1, figsize=(15,10))
    ax = sns.barplot(y = "proportion",
                     x = "subreddit", 
                     orient = "v",
                     hue = "domain", 
                     hue_order = domains,
                     data = subreddit_domains_df, 
                     palette = color_palette)
    
    ax.set_ylabel(f"# of news links")
    ax.set_xlabel(f"subreddit")
    plt.legend(frameon = False, loc='upper right')
    plt.tight_layout()
    ax.get_figure().savefig("subreddit_news_horizontal.png")

# SECTION: News domains left to right for some climate change related subreddits
CLIMATE_SUBREDDITS = ["globalwarming", "globalclimatechange", "environment", "renewableenergy", "climateskeptics", "climatenews", "climatechange", "climateactionplan"]
df = news_domains_by_subreddit("submission", CLIMATE_SUBREDDITS, LEFT_TO_RIGHT)
plot_news_domains_by_subreddit(df, LEFT_TO_RIGHT)



