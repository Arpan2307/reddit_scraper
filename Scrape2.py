import praw
import re
import string

# Replace these with your Reddit app credentials
REDDIT_CLIENT_ID = 'lai68mRTUnM5sEGofauWnw'
REDDIT_CLIENT_SECRET = 'kKukXStNSV-p3kdlNJjr5hZS6Oe5Jg'
REDDIT_USER_AGENT = 'Extractor by u/Used-Ambassador2989'

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def extract_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if len(s.split()) > 3]  # filter short ones

def clean_sentence(sentence):
    # Remove emojis
    sentence = re.sub(r'[^\x00-\x7F]+', '', sentence)
    # Remove punctuation and special characters
    sentence = re.sub(rf"[{re.escape(string.punctuation)}]", '', sentence)
    # Remove extra whitespace
    sentence = re.sub(r'\s+', ' ', sentence).strip()
    # Convert to lowercase
    sentence = sentence.lower()
    return sentence

def scrape_subreddit(subreddit_name, limit=100):
    subreddit = reddit.subreddit(subreddit_name)
    all_sentences = []

    print(f"Scraping r/{subreddit_name}...")

    for submission in subreddit.hot(limit=limit):
        all_sentences.extend(extract_sentences(submission.title))
        all_sentences.extend(extract_sentences(submission.selftext or ''))

        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            all_sentences.extend(extract_sentences(comment.body))

    return all_sentences

def scrape_multiple_subreddits(subreddits, limit=10):
    all_sentences = []
    for sub in subreddits:
        sentences = scrape_subreddit(sub, limit)
        all_sentences.extend(sentences)
    return all_sentences

def filter_sentences_by_keywords(sentences, keywords):
    keywords_lower = [kw.lower() for kw in keywords]
    return [s for s in sentences if any(kw in s.lower() for kw in keywords_lower)]

def save_sentences_to_file(sentences, filename='filtered_sentences.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for i, sentence in enumerate(sentences, 1):
            cleaned = clean_sentence(sentence)
            if cleaned:  # skip empty sentences after cleaning
                f.write(f"{i}\t{cleaned}\n")
    print(f"\n✅ Sentences saved to '{filename}'")

# Main
if __name__ == "__main__":
    subreddits = ['JEENEETards', 'JEE', 'NEET']  # ← add more subreddits here
    keywords = ['exam', 'neet', 'jee', 'iit']    # ← filter based on these keywords
    post_limit = 10  # number of hot posts per subreddit

    raw_sentences = scrape_multiple_subreddits(subreddits, post_limit)
    filtered_sentences = filter_sentences_by_keywords(raw_sentences, keywords)

    print(f"\nExtracted {len(filtered_sentences)} filtered sentences:")
    for i, s in enumerate(filtered_sentences[:20], 1):
        print(f"{i}. {clean_sentence(s)}")

    save_sentences_to_file(filtered_sentences, 'filtered_jee_neet_sentences.txt')
