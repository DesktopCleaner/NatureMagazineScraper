import json
import os
import math
import numpy as np
from collections import defaultdict
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize

class BetterDataCleaner:
    """
    Better and more scientific data cleaning method, featuring:
    - TF-IDF to identify domain-specific terms and boost their weight
    - Document frequency analysis
    - Statistical outlier detection using Z-scores and IQR
    - Frequency percentile filtering to remove common words
    """
    
    def __init__(self, word_freq_file='word_freq.json', common_words_file='1000_common_words.json', 
                 scraped_articles_dir='scraped_articles'):
        print(f"Loading word frequency data from {word_freq_file}...")
        with open(word_freq_file, 'r') as f:
            self.word_freq = json.load(f)
        
        try:
            with open(common_words_file, 'r') as f:
                self.common_words = set(json.load(f))
            print(f"Loaded {len(self.common_words)} common words")
        except:
            self.common_words = set()
            print("No common words file found, continuing without it")
        
        self.stopwords = set(stopwords.words("english"))
        self.scraped_articles_dir = scraped_articles_dir
        self.total_docs = 0
        self.doc_freq = defaultdict(int)  # How many documents contain each word
        self.total_words = sum(item['freq'] for item in self.word_freq.values())
        
    def calculate_document_frequency(self):
        """
        Calculate document frequency for each word across all articles.
        High document frequency = common/field-specific term that appears globaly.
        """
        print("Calculating document frequency across all articles...")
        doc_id = 0
        
        for root, dirs, files in os.walk(self.scraped_articles_dir):
            for file in files:
                if file.endswith('.txt'):
                    self.total_docs += 1
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                            tokens = word_tokenize(text.lower())
                            
                            # Track unique words per document
                            doc_words = set()
                            for token in tokens:
                                if (token.isalpha() and 
                                    len(token) > 2 and 
                                    token not in self.stopwords and
                                    bool(wordnet.synsets(token))):
                                    doc_words.add(token)
                            
                            # Update document frequency
                            for word in doc_words:
                                self.doc_freq[word] += 1
                            
                            doc_id += 1
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
        
        print(f"Processed {self.total_docs} documents")
        print(f"Found {len(self.doc_freq)} unique words across documents")
        return self.doc_freq
    
    def calculate_tfidf_scores(self):
        """
        Calculate TF-IDF scores to identify domain-specific terms.
        Low TF-IDF = common words, High TF-IDF = domain-specific terms.
        Remove words with very low TF-IDF.
        """
        print("Calculating TF-IDF scores...")
        tfidf_scores = {}
        
        for word, data in self.word_freq.items():
            freq = data['freq']
            
            # Term Frequency (TF) - normalized by total word count
            tf = freq / self.total_words if self.total_words > 0 else 0
            
            # Document Frequency (DF) - how many docs contain this word
            df = self.doc_freq.get(word, 1)  # Default to 1 to avoid division by zero
            
            # Inverse Document Frequency (IDF)
            # Using log to dampen the effect
            if self.total_docs > 0:
                idf = math.log(self.total_docs / (df + 1))
            else:
                idf = 0
            
            # TF-IDF score
            tfidf = tf * idf
            tfidf_scores[word] = {
                'tfidf': tfidf,
                'df': df,
                'df_ratio': df / self.total_docs if self.total_docs > 0 else 0
            }
        
        return tfidf_scores
    
    def detect_statistical_outliers(self, threshold=2.0):
        """
        Detect outliers using Z-score method with threshold.
        
        Removes words with Z-score > threshold (default 2.0)
        
        Returns:
            set: Words identified as outliers to be removed
        """
        print(f"Detecting outliers using Z-score method (threshold={threshold})...")
        frequencies = np.array([data['freq'] for data in self.word_freq.values()])
        
        if len(frequencies) == 0:
            return set()
        
        mean_freq = np.mean(frequencies)
        std_freq = np.std(frequencies)
        
        if std_freq == 0:
            return set()
        
        outliers = set()
        for word, data in self.word_freq.items():
            z_score = abs((data['freq'] - mean_freq) / std_freq)
            # Remove words that are too common (high frequency outliers)
            if z_score > threshold and data['freq'] > mean_freq:
                outliers.add(word)
        
        print(f"Found {len(outliers)} outliers using Z-score method (threshold={threshold})")
        return outliers
    
    def filter_by_tfidf(self, tfidf_scores, min_tfidf_threshold=None, max_df_ratio=0.8, min_tfidf_percentile=10):
        """
        Filter words based on TF-IDF scores.
        - Remove words with very low TF-IDF (too common)
        - Remove words that appear in too many documents (max_df_ratio)
        """
        print(f"Filtering by TF-IDF (max_df_ratio={max_df_ratio})...")
        
        if min_tfidf_threshold is None:
            # Calculate threshold as bottom percentile of TF-IDF scores
            tfidf_values = np.array([score['tfidf'] for score in tfidf_scores.values()])
            if len(tfidf_values) > 0:
                min_tfidf_threshold = np.percentile(tfidf_values, min_tfidf_percentile)
            else:
                min_tfidf_threshold = 0
        
        filtered_words = set()
        for word, score_data in tfidf_scores.items():
            # Remove words that appear in too many documents (common words)
            if score_data['df_ratio'] > max_df_ratio:
                filtered_words.add(word)
            # Remove words with very low TF-IDF (not distinctive)
            elif score_data['tfidf'] < min_tfidf_threshold:
                filtered_words.add(word)
        
        print(f"Filtered out {len(filtered_words)} words based on TF-IDF")
        return filtered_words
    
    def clean(self, outlier_threshold=2.0, 
              max_df_ratio=0.8, min_tfidf_percentile=10, 
              remove_common_words=True, output_file='word_freq(cleaned).json'):
        """
        Main cleaning function that combines all methods.
        
        - outlier_threshold: Threshold for Z-score method
        - max_df_ratio: Maximum document frequency ratio
        - min_tfidf_percentile: Minimum TF-IDF percentile to keep
        """

        print("\n" + "="*60)
        print("Starting BetterDataCleaner")
        print("="*60)
        
        words_to_remove = set()
        
        # Step 1: Calculate document frequency
        self.calculate_document_frequency()
        
        # Step 2: Calculate TF-IDF scores
        tfidf_scores = self.calculate_tfidf_scores()
        
        # Step 3: Filter by TF-IDF and document frequency
        tfidf_filtered = self.filter_by_tfidf(tfidf_scores, 
                                               max_df_ratio=max_df_ratio,
                                               min_tfidf_threshold=None,
                                               min_tfidf_percentile=min_tfidf_percentile)
        words_to_remove.update(tfidf_filtered)
        
        # Step 4: Detect statistical outliers using Z-score
        outliers = self.detect_statistical_outliers(threshold=outlier_threshold)
        words_to_remove.update(outliers)
        
        # Step 5: Remove common words if requested
        if remove_common_words:
            words_to_remove.update(self.common_words)
            print(f"Removed {len(self.common_words)} common words")
        
        # Step 6: Remove words from word_freq
        cleaned_word_freq = {}
        removed_count = 0
        
        for word, data in self.word_freq.items():
            if word not in words_to_remove:
                cleaned_word_freq[word] = data
            else:
                removed_count += 1
        
        print(f"\nRemoved {removed_count} words total")
        print(f"Kept {len(cleaned_word_freq)} words")
        print(f"Removal rate: {removed_count/len(self.word_freq)*100:.2f}%")
        
        # Step 7: Save cleaned data
        with open(output_file, 'w') as f:
            json.dump(cleaned_word_freq, f, indent=4)
        
        print(f"\nCleaned data saved to {output_file}")
        print("="*60)
        
        return cleaned_word_freq


if __name__ == "__main__":
    # Clean the targeted file
    cleaner = BetterDataCleaner(
        word_freq_file='word_freq.json',
        common_words_file='1000_common_words.json',
        scraped_articles_dir='scraped_articles'
    )
    
    cleaned_data = cleaner.clean(
        outlier_threshold=2.0,
        max_df_ratio=0.8,
        remove_common_words=True
    )
    
    print("\nCleaning complete!")

