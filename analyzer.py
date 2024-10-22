import nltk
import os
import ssl
import json

from nltk.corpus import wordnet
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import words
from nltk import pos_tag

# Create an unverified SSL context if needed
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
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

lemmatizer = WordNetLemmatizer()
corpus_words = set(words.words())

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN 

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
                    tagged_words = pos_tag(words)
                    lemmatized_words = [
                        lemmatizer.lemmatize(word, pos=get_wordnet_pos(tag))
                        for word, tag in tagged_words
                        if word not in stop_words
                    ]
                    word_freq.update(lemmatized_words)
    return word_freq



directory = '/Users/shepherd/Desktop/scraped_articles'
word_freq = read_files(directory)
print("Most common words:")
for word, freq in word_freq.most_common(10):
    print(f"{word}: {freq}")
