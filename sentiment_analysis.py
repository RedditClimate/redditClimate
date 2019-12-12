from reddit import query_n, BIG_LIST

import matplotlib.pyplot as plt
import seaborn as sns

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import pandas as pd

def sentiment_analysis(category, subreddit, n = float("inf")):
    all_sentences = []
    results = query_n(category, {"subreddit": subreddit}, n=n)
    for result in results:
        text_fields = ["title", "selftext", "body"]
        submissions = [result[field] for field in text_fields if field in result]
        submission_text = "\n".join()
        sentences = sent_tokenize(submission_text)
        all_sentences.extend(sentences)

    sentiment_analyzer = SentimentIntensityAnalyzer()
    score_sums = {"pos": 0, "neu": 0, "neg": 0, "compound": 0}
    
    if not all_sentences:
        print(f"Skipping {subreddit} (no submissions)")
        return score_sums

    for sentence in all_sentences:
        polarity = sentiment_analyzer.polarity_scores(sentence)
        for score_category in polarity:
            score_sums[score_category] += polarity[score_category]
    print("Subreddit:", subreddit)
    score_avgs = {k:round(v/len(all_sentences), 3) for k,v in score_sums.items()}
    print(f"Num sentences: {len(all_sentences)}")
    return score_avgs


def exec_sentiment_analysis(n = float("inf")):
    records = []
    for i, subreddit in enumerate(BIG_LIST):
        score_avgs = sentiment_analysis("comment", subreddit, n = n)
        for score_type in ["compound", "neu", "pos", "neg"]:
            score = score_avgs[score_type]
            record = {"subreddit": subreddit, "score_type": score_type, "score": score}
            records.append(record)

    sentiment_df = pd.DataFrame.from_records(records)
    sentiment_df.to_pickle("sentiment_df.pickle")

    return sentiment_df

# exec_sentiment_analysis(n = 10000)

def plot_sentiment_analysis(sentiment_df = None, sort_score_type = "pos"):
    sentiment_df = sentiment_df or pd.read_pickle("sentiment_df.pickle")
    
    plt.clf()
    f, axs = plt.subplots(
                    15,
                    15,
                    figsize=(60, 60),
                    sharex = True,
                    sharey = True,
                    squeeze = True)
    
    ax_array = axs.flatten()
    def sorter(subreddit):
        df = sentiment_df
        select_subreddit = df["subreddit"] == subreddit
        select_score_type = df["score_type"] == sort_score_type
        return df[select_subreddit & select_score_type].iloc[0]["score"]
        
    sorted_subreddits = sorted(BIG_LIST, reverse = True, key = sorter)
    
    for i,subreddit in enumerate(sorted_subreddits):
        sns.barplot(
                    x="subreddit",
                    y="score",
                    hue="score_type",
                    hue_order=["neg", "neu", "pos"],
                    data=sentiment_df[sentiment_df["subreddit"] == subreddit],
                    ax = ax_array[i])
        ax.set(xlabel=subreddit)
        
    f.savefig(f"sentiment_plot_{sort_key}.png")

# for sort_key in ["pos", "neg", "neu"]:
#     plot_sentiment_analysis(sort_key = sort_key)

def top_domains(category, subreddit = "climateskeptics", n=float("inf"), top_k = 5):
    results = query_n(category, {"subreddit": subreddit}, n=n)
    print(results[0])
    domains_df = pd.DataFrame([r["domain"] for r in results if "domain" in r], columns=["domain"])

    f, ax = plt.subplots(figsize=(10, 10))

    sns.countplot(y="domain", data=domains_df, ax=ax, order = pd.value_counts(domains_df['domain']).iloc[:top_k].index)
    ax.set_title(f"Top {top_k} Domains Linked to from r/{subreddit} {category}s")
    ax.set_xlabel(f"# of links")

    plt.tight_layout()

    f.savefig("domains_plot.png")

 
# top_domains("submission", n = float("inf"), top_k = 7)