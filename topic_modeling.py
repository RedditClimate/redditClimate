from reddit import query_n

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import gensim

STOP_WORDS = set(stopwords.words('english'))

def lda(docs, num_topics = 2, num_words = 4, num_passes=20):
    tokenizer = RegexpTokenizer(r'\w+')
    porter_stemmer = PorterStemmer()

    for i, doc in enumerate(docs):
        # 1. Lowercase and tokenize each document
        tokens = tokenizer.tokenize(doc.lower())
        # 2. Remove any stop words
        stopped_tokens = [tok for tok in tokens if tok not in STOP_WORDS]
        # 3. Apply porter stemming
        docs[i] = [porter_stemmer.stem(stopped_tok) for stopped_tok in stopped_tokens]
    
    # Create a dictionary and a corpus for LDA
    dictionary = gensim.corpora.Dictionary(docs)
    corpus = list(map(dictionary.doc2bow, docs))
    # Train the LDA model
    lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics = num_topics, id2word = dictionary, passes = num_passes)
    # Return the generated topics
    return lda_model.print_topics(num_topics=num_topics, num_words = num_words)

def reddit_topic_modeling():
    docs = []
    for i, subreddit in enumerate(CLIMATE_SUBREDDITS):
        print(f"creating doc {i} for subreddit: {subreddit}" )
        results = query_n("submission", {"subreddit": subreddit},  n = 20000)
        doc = "\n".join([result.get("title", "") + "\n" + result.get("selftext", "") for result in results])
        docs.append(doc)
    return lda(docs)

# reddit_topic_modeling()

def topic_modeling_within_subreddit(subreddit):
    print(f"creating doc for subreddit: {subreddit}" )
    results = query_n("submission", {"subreddit": subreddit},  n = 25000)
    results.extend(query_n("comment", {"subreddit": subreddit},  n = 25000))
    docs = ["\n".join([result.get(field, "") for field in ["title", "selftext", "body"]]) for result in results]

    with open('climateskeptics.json', 'w') as f:
        json.dump(docs, f)
    return lda(docs, num_topics = 10)

# topics = topic_modeling_within_subreddit("sustainability")
# for topic in topics:
#     print(topic)