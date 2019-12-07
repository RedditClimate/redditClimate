from reddit import query_n

WORLD_DOMAINS = ["news.google.com", 
                 "news.yahoo.com", 
                 "cnn.com", 
                 "bbc.com", 
                 "nytimes.com", 
                 "theguardian.com",
                 "dailymail.co.uk", 
                 "washingtonpost.com",
                 "indiatimes.com", 
                 "huffingtonpost.com", 
                 "foxnews.com",
                 "usatoday.com", 
                 "wsj.com", 
                 "nbcnews.com", 
                 "abcnews.go.com"]

WORLD_DOMAINS_LEFT_TO_RIGHT = ["nytimes.com",
                               "bbc.com", "huffingtonpost.com", "washingtonpost.com",         
                               
                               "cnn.com",
                               "nbcnews",
                               "news.google.com", "abcnews.go.com",
                               "wsj.com",
                               "foxnews.com",
                               "breitbart.com",
                               ]

DOMAINS = ["cnn.com", 
           "nytimes.com",
           "huffpost.com",
           "foxnews.com",
           "usatoday.com",
           "reuters.com",
           "politico.com",
           "yahoo.com/news",
           "npr.org",
           "latimes.com",
           "breitbart.com",
           "nypost.com",
           "nbcnews.com",
           "cbsnews.com",
           "abcnews.go.com",
           "cbslocal.com",
           "newsweek.com", "nydailynews.com", "chicagotribune.com", "denverpost.com", "boston.com", "theonion.com", "newsmax.com", "seattletimes.com", "mercurynews.com", "stltoday.com", "washingtontimes.com", "miamiherald.com", "ktla.com", "newsday.com", "suntimes.com", "gothamist.com", "abc13.com", "wtop.com", "seattlepi.com", "nbcnewyork.com", "observer.com", "abc7news.com", "wgntv.com", "nbclosangeles.com", "westword.com", "news12.com", "kxan.com", "kdvr.com", "phillyvoice.com", "fox2now.com", "dailyherald.com", "nbcchicago.com", "twincities.com", "nbcsandiego.com", "nbcdfw.com", "laweekly.com"]

def news_domains_by_subreddit(category, subreddits, domains):
    plt.subplots(1,1, figsize=(15,10))
    results = query_n(category, {"subreddit": ",".join(subreddits), "domain": ",".join(domains) }, n=10000) # 50000
    subreddit_counter = Counter([ r["subreddit"] for r in results])

    most_common_subreddits = [subreddit for subreddit,_ in subreddit_counter.most_common(10)]
    results = query_n(category, {"subreddit": ",".join(most_common_subreddits), "domain": ",".join(domains) }, n=20000) # 100000 
    subreddit_counter = Counter([ r["subreddit"] for r in results])
    counter = Counter([(r["domain"], r["subreddit"]) for r in results])
    print(counter)
    for r in results:
        r["count"] = counter[(r["domain"], r["subreddit"])]/subreddit_counter[r["subreddit"]]

    subreddit_domains_df = pd.DataFrame.from_records(results)[["subreddit", "domain", "count"]]

    color_palette = sns.color_palette("coolwarm", len(domains))
    ax = sns.barplot(y = "count", x = "subreddit", hue = "domain", data = subreddit_domains_df, orient = "v", hue_order = domains, palette = color_palette)
    
    ax.set_ylabel(f"# of news links")
    ax.set_xlabel(f"subreddit")
    plt.legend(frameon = False, loc='upper right')
    plt.tight_layout()
    ax.get_figure().savefig("subreddit_news_horizontal.png")


# SECTION: News domains left to right for some climate change related subreddits
CLIMATE_SUBREDDITS = ["globalwarming", "globalclimatechange", "environment", "renewableenergy", "climateskeptics", "climatenews", "climatechange", "climateactionplan"]
news_domains_by_subreddit("submission", CLIMATE_SUBREDDITS, WORLD_DOMAINS_LEFT_TO_RIGHT)
