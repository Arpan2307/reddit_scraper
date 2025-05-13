import praw
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import words
from collections import Counter
import string
import os



# Setup
nltk.download('punkt_tab')
nltk.download('words')

REDDIT_CLIENT_ID = 'lai68mRTUnM5sEGofauWnw'
REDDIT_CLIENT_SECRET = 'kKukXStNSV-p3kdlNJjr5hZS6Oe5Jg'
REDDIT_USER_AGENT = 'Extractor by u/Used-Ambassador2989'

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

ENGLISH_WORDS = set(w.lower() for w in words.words())

def extract_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if len(s.split()) > 3]

def scrape_subreddit(subreddit_name, limit=100):
    subreddit = reddit.subreddit(subreddit_name)
    all_sentences = []
    print(f"🔍 Scraping r/{subreddit_name}...")

    for submission in subreddit.hot(limit=limit):
        all_sentences.extend(extract_sentences(submission.title))
        all_sentences.extend(extract_sentences(submission.selftext or ''))
        submission.comments.replace_more(limit=0)
        for comment in submission.comments:
            all_sentences.extend(extract_sentences(comment.body))
    return all_sentences

def extract_hinglish_candidates(sentences, top_k=500):
    freq = Counter()
    for sent in sentences:
        tokens = word_tokenize(sent.lower())
        for token in tokens:
            token = token.strip(string.punctuation)
            if token.isalpha() and token not in ENGLISH_WORDS:
                freq[token] += 1
    return freq.most_common(top_k)

def compute_code_mixing_ratio(sentence):
    tokens = word_tokenize(sentence.lower())
    tokens = [t.strip(string.punctuation) for t in tokens if t.isalpha()]
    if not tokens:
        return 0.0
    non_eng = sum(1 for t in tokens if t not in ENGLISH_WORDS)
    return round(non_eng / len(tokens), 2)

def save_to_files(sentences, hinglish_words, ratio_file='code_mixed_ratios.txt'):
    with open("sentences.txt", "w", encoding='utf-8') as f1:
        for s in sentences:
            f1.write(s.strip() + "\n")

    with open("hinglish_candidates.txt", "w", encoding='utf-8') as f2:
        for word, freq in hinglish_words:
            f2.write(f"{word}\t{freq}\n")

    with open(ratio_file, "w", encoding='utf-8') as f3:
        for s in sentences:
            ratio = compute_code_mixing_ratio(s)
            f3.write(f"{s.strip()}\t[{ratio}]\n")

    print("\n✅ All files generated:")
    print(" - sentences.txt")
    print(" - hinglish_candidates.txt")
    print(" - code_mixed_ratios.txt")

# Run full pipeline
if __name__ == "__main__":
    subreddits = ['JEENEETards', 'IndianTeenagers']  # Multiple subreddits
    all_sentences = []
    for sub in subreddits:
        all_sentences.extend(scrape_subreddit(sub, limit=10))

    hinglish_words = extract_hinglish_candidates(all_sentences, top_k=500)
    save_to_files(all_sentences, hinglish_words)
