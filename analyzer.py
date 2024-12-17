# Before running, name your word frequency file to "word_frequency.json" to build on top.
# Otherwise the function will create a blank new word frequency file and then start counting.
# After analysis, a new word_freq file will be created with its date of creation in its file name.import os
import json
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import datetime # For naming files

stopwords = stopwords.words("english")

with open('word_families_mapping.json', 'r', encoding='utf-8') as reference_f:
    word_families_mapping = json.load(reference_f)
variants = word_families_mapping.keys() # Used to reduce words to their root forms

# Try to open existing word frequency file
try:
    with open('word_frequency.json', "r") as collection_f:
        word_freq = json.load(collection_f)
except:
    print("Previous word frequency dict not found!!")
    word_freq = {}

# Read files and calculate word frequencies
# Analyze files in scraped_articles folder by default
def read_files_by_year(year1, year2):
    global word_freq
    global word_cap # Maximum number of a specific word counted per article. To reduce bias.
    global article_counter
    article_counter = 0

    for folder_num in range(year1, year2 + 1): # Scrape from starting folder to ending folder. Include both.
        directory = "scraped_articles" + "/" + str(folder_num)
        print("analyzing year:", folder_num)

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.txt'): # Only read text files
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        tokens = word_tokenize(text)

                        word_cap_dict = {} # Clear word cap dict
                        article_counter += 1
                        for token in tokens:
                            if not all([
                                token.isalpha(),
                                len(token) > 2,
                                bool(wordnet.synsets(token)), # Is a word
                                token not in stopwords # Is not a stepword
                            ]):
                                continue
                                
                            token = token.lower()
                            # Reduce word to its root
                            if token in variants:
                                root_word = word_families_mapping[token]

                                if root_word not in word_cap_dict:
                                    word_cap_dict.update({root_word : 1})
                                elif word_cap_dict[root_word] == word_cap: # Don't count it word if it reaches maximum count
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

                            if root_word not in word_freq: 
                                word_freq.update({root_word : {"freq" : 1, "existing" : []}})
                            else:
                                if not capped:
                                    word_freq[root_word]["freq"] += 1
                                #print("updated!")
                                existing_variants = word_freq[root_word]["existing"]

                                if token not in existing_variants: 
                                    existing_variants.append(token)


# Input year
input_year_result = input("Input starting and ending years to analyze (separated by space). Type 'all' to analyze all years.")

if input_year_result == "all":
    print("Analyze all years.")

    word_cap = int(input("Input the maximum number a word can be counted per passage: (recommend:3)"))
    print("Word count cap number per passage:", word_cap)

    read_files_all()
    exit()

year1, year2 = map(int, input_year_result.split())
print("Analyze years:", year1, "to", year2)

# Input word cap
word_cap = int(input("Input the maximum number a word can be counted per passage: (recommend:3)"))
print("Word count cap number per passage:", word_cap)

read_files_by_year(year1, year2)
word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1]["freq"], reverse=True))

# Save the word frequency data to a JSON file
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"word_freq {current_time}.json"
with open(output_file, 'w') as f:
    json.dump(word_freq, f, indent = 4)
print(f"Word frequency data saved to {output_file}")
print(f"Articles analyzed: {article_counter}")


