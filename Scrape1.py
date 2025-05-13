import praw
import re

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

def scrape_subreddit(subreddit_name, limit=1000):
    subreddit = reddit.subreddit(subreddit_name)
    all_sentences = []

    print(f"Scraping r/{subreddit_name}...")

    for submission in subreddit.hot(limit=limit):
        all_sentences.extend(extract_sentences(submission.title))
        all_sentences.extend(extract_sentences(submission.selftext or ''))

        submission.comments.replace_more(limit=0)
        for comment in submission.comments:
            all_sentences.extend(extract_sentences(comment.body))

    return all_sentences

def save_sentences_to_file(sentences, filename='JEENEETards.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(sentence.strip() + '\n')
    print(f"\n✅ Sentences saved to '{filename}'")

# Example usage
if __name__ == "__main__":
    subreddit_name = 'JEENEETards'
    sentences = scrape_subreddit(subreddit_name, limit=1000)

    print(f"\nExtracted {len(sentences)} sentences:")
    for i, s in enumerate(sentences[:20], 1):
        print(f"{i}. {s}")

    # Save all sentences to file
    save_sentences_to_file(sentences)
