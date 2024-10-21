import nltk
import os
import ssl

# Create an unverified SSL context if needed
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()

# Function to ensure required resources are available
def ensure_nltk_resources():
    try:
        nltk.data.find('tokenizers/punkt')
        stop_words = set(nltk.corpus.stopwords.words('english'))
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords')
        stop_words = set(nltk.corpus.stopwords.words('english'))  # Retry after downloading
    return stop_words

# Ensure resources are available
stop_words = ensure_nltk_resources()

# Additional common words to exclude
additional_stop_words = {'strong', 'press', "x"}

# Combine the default stop words with the additional ones
stop_words = stop_words.union(additional_stop_words)

from nltk.corpus import wordnet
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import words

lemmatizer = WordNetLemmatizer()
corpus_words = set(words.words())

def read_files(directory):
    word_freq = Counter()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='ISO-8859-1') as f:
                    text = f.read()
                    words = nltk.word_tokenize(text)
                    words = [word.lower() for word in words if all([word.isalpha(), word in corpus_words, len(word) > 2])]  # Filter out short words
                    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
                    word_freq.update(words)
    return word_freq

directory = 'scraped_articles'
word_freq = read_files(directory)
print(word_freq.most_common())



