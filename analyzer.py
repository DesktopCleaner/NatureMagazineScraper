import os
import json
from collections import Counter
import nltk
from nltk.corpus import wordnet
# from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stopwords = stopwords.words("english")
# Download necessary NLTK data
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('stopwords')

# Method 1: Using wordnet.synsets()
# def is_english_word(word):
#     if wordnet.synsets(word):
#         return True
#     else:
#         return False

# Define additional stop words
# additional_stop_words = {'strong', 'press', "x"}

# # Initialize WordNet lemmatizer
# lemmatizer = WordNetLemmatizer()

# # Get English stop words
# stop_words = set(stopwords.words('english')).union(additional_stop_words)

# def get_wordnet_pos(token):
#     tag = nltk.pos_tag([token])[0][1]
#     """Map NLTK POS tags to WordNet POS tags"""
#     tag_map = {
#         'J': wordnet.ADJ,        # Adjectives
#         'N': wordnet.NOUN,       # Nouns
#         'V': wordnet.VERB,       # Verbs
#         'R': wordnet.ADV         # Adverbs
#     }
#     return tag_map.get(tag[0], wordnet.NOUN)
# Load the word families mapping from the JSON file

with open('/Users/shepherd/Desktop/Inputs/word_families_mapping.json', 'r', encoding='utf-8') as reference_f:
    word_families_mapping = json.load(reference_f)
variants = word_families_mapping.keys()

try:
    with open('/Users/shepherd/Desktop/Outputs/word_frequency.json', "r") as collection_f:
        word_freq = json.load(collection_f)
except:
    print("Previous word_freq dict not found!!")
    word_freq = {}

# Function to read files and calculate word frequencies
def read_files_by_page(stem_directory, folder_num1, folder_num2):
    global word_freq
    global word_cap
    global article_counter
    folder_num = folder_num1
    article_counter = 0

    for folder_num in range(folder_num1, folder_num2 + 1):
        directory = stem_directory + f"/scraped_articles_page_{str(folder_num)}"
        print("analyzing page:", folder_num)

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        tokens = word_tokenize(text)

                        word_cap_dict = {}
                        article_counter += 1
                        for token in tokens:
                            if not all([
                                token.isalpha(),
                                len(token) > 2,
                                bool(wordnet.synsets(token)),
                                token not in stopwords
                            ]):
                                continue
                                
                            token = token.lower()
                            if token in variants:
                                root_word = word_families_mapping[token]

                                if root_word not in word_cap_dict:
                                    word_cap_dict.update({root_word : 1})
                                elif word_cap_dict[root_word] == word_cap:
                                    continue
                                else:
                                    word_cap_dict[root_word] += 1

                                if root_word not in word_freq:
                                    word_freq.update({root_word : {"freq" : 1, "existing" : []}})
                                else:
                                    word_freq[root_word]["freq"] += 1
                                    #print("updated!")
                                    existing_variants = word_freq[root_word]["existing"]

                                    if token not in existing_variants:
                                        existing_variants.append(token)

def read_files_all(directory):
    global word_freq
    global word_cap
    global article_counter
    article_counter = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    tokens = word_tokenize(text)

                    word_cap_dict = {}
                    article_counter += 1
                    for token in tokens:
                        if not all([
                            token.isalpha(),
                            len(token) > 2,
                            bool(wordnet.synsets(token)),
                            token not in stopwords
                        ]):
                            continue
                            
                        token = token.lower()
                        if token in variants:
                            root_word = word_families_mapping[token]
                            capped = 0

                            if root_word not in word_cap_dict:
                                word_cap_dict.update({root_word : 1})
                            elif word_cap_dict[root_word] == word_cap:
                                capped = 1
                            else:
                                word_cap_dict[root_word] += 1

                            if root_word not in word_freq: #Apparently not capped
                                word_freq.update({root_word : {"freq" : 1, "existing" : []}})
                            else:
                                if not capped:
                                    word_freq[root_word]["freq"] += 1
                                #print("updated!")
                                existing_variants = word_freq[root_word]["existing"]

                                if token not in existing_variants: #Still add variant even capped
                                    existing_variants.append(token)

stem_directory = '/Users/shepherd/Desktop/scraped_articles'
year = int(input("Which year's articles to analyze?"))
print("Analyzing year:", year)
stem_directory += "/" + str(year)
#folder_num1, folder_num2 = map(int, input("Please type in starting and ending page numbers to be analyzed:").split())
#print(f"Analyzing page from {str(folder_num1)} to {str(folder_num2)}")
word_cap = int(input("Input word count cap per passage:"))
print("Word count cap number per passage:", word_cap)
read_files_all(stem_directory)
word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1]["freq"], reverse=True))

# Save the word frequency data to a JSON file
output_file = '/Users/shepherd/Desktop/Outputs/word_frequency.json'
with open(output_file, 'w') as f:
    json.dump(word_freq, f, indent = 4)
print(f"Word frequency data saved to {output_file}")
print(f"Articles analyzed: {article_counter}")


