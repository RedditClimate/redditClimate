from reddit import query_n

from collections import Counter

def author_count_plot(category, subreddit_name):
    params  = {
        "subreddit": subreddit,
        "sort": "desc",
        "size": 1000,
        "sort_type": "created_utc",
    }
    results = query_n(category, params, n = float("inf"))
    results_df = pd.DataFrame.from_records(results)

    author_counts = Counter(result["author"] for result in results)
    author_counts_df = pd.DataFrame.from_records(sorted(author_counts.items(), key=lambda x:x[1], reverse = True), columns = ["author", f"n{category}s"]) 
    author_counts_df.to_pickle(f"{subreddit_name}_{category}_author_counts_df.pickle")

    f, ax = plt.subplots(figsize=(10, 50))
    ax = sns.countplot(y="author", data=results_df, order = pd.value_counts(results_df['author']).iloc[:50].index)
    ax.set_title(f"Top 50 Contributors to r/{subreddit_name}")
    ax.set_xlabel(f"# of {category}s")
    plt.tight_layout()
    f.savefig(f"{subreddit_name}_{category}_author_countplot.png")
