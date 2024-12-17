import csv
import json
import math
from typing import List, Dict

def group_lines_by_category(lines_tsv: str):
    # Our typology and corresponding text files
    categories = {
        'm': 'money.txt',  # Money
        'b': 'business.txt',  # Business
        'h': 'health.txt',  # Health
        'l': 'law.txt',  # Law
        'f': 'family.txt',  # Family
        'dl': 'daily_life.txt',  # Daily Life (Catch All)
        'd': 'danger.txt'  # Danger
    }

    # Open all files in write mode and store in a dictionary
    category_files = {}
    for key, filename in categories.items():
        category_files[key] = open(filename, 'w', encoding='utf-8')
    
    try:
        # Open the TSV file for reading
        with open(lines_tsv, 'r', encoding='utf-8') as lines_data:
            reader = csv.reader(lines_data, delimiter='\t')
            next(reader) # Skip header row

            for row in reader: # Row format: episode, character, line, annotation
                if len(row) >= 4: 
                    # Extract the content and category
                    line_content = row[2]  # Line of dialogue
                    category_key = row[3].strip().lower()  # Category key (m, b, d, dl, ...)
                    
                    # Write to the appropriate category file
                    if category_key in category_files: 
                        # Get the open write-to-file object that is the value corresponding to the annotation as the key
                        category_files[category_key].write(line_content + '\n')
                    else:
                        print(f"Warning: Unknown category '{category_key}' for line: {line_content}")
    finally:
        # Done writing, close
        for file in category_files.values():
            file.close()

    return list(categories.values()) # Our filenames for making a JSON later

def stopword_file_to_list(sw_file: str) -> List[str]:
    """
    Load stopwords from a file into a list.
    """
    word_list = []
    with open(sw_file, 'r') as stopwords:
        for line in stopwords:
            word_list.append(line.strip())
    return word_list
    # Copied from HW 11

def process_files_to_word_frequencies(input_files: List[str], stopwords_file: str):
    
    result = {} # 2D Map of category -> word -> count
    stopwords = stopword_file_to_list(stopwords_file) # to use for word filtering

    for file in input_files: # Our dialogue by category
        # Open the file and read all words
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read() 
        
        # Turn words into list by space delimiting
        words = content.split()

        # Remove non-alphabetic characters and filter out empty words
        clean_words = [
            ''.join(char for char in word if char.isalpha()).lower()
            for word in words
        ]
        clean_words = [word for word in clean_words if ((word) and (word not in stopwords))]  # Remove empty words

        # Compute word frequencies (naive frequency)
        word_count = {}
        for word in clean_words: # Listified text in the file
            word_count[word] = word_count.get(word, 0) + 1 # if not yet in map, initialize to 0+1, else increment current value by 1

        result[file] = word_count # value of return map is the map for current category: word -> count

    return result # return giant resulting map (dictionary)

def build_tfidf_lists(freq_lists: Dict[str, Dict[str, int]], category_files: List[str], out_json: str):
    num_documents = len(category_files) # 7 categories = 7 documents
    result = {} # to store category -> word -> tfidf score

    for category in category_files:
        tfidf_scores = {} # given each category: make a map or dict w/ word -> tfidf

        # Get [(word, count), ... ] for the current category
        word_frequencies = freq_lists[category]
        
        # Calculate TF-IDF for each word
        for word, tf in word_frequencies.items():
            # Count how many documents contain this word
            doc_count = sum(1 for file in category_files 
                            if word in freq_lists[file])
            
            # Calculate Inverse document frequency
            idf = math.log(num_documents / doc_count)
            
            # Compute TF-IDF
            tfidf_scores[word] = tf * idf
        
        # Get the top 10 words by TF-IDF scores
        top_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[0:20]
        
        # for category, populate its value as the dict word -> tfidf, so we have category -> word -> tfidf
        result[category] = [[word, score] for word, score in top_tfidf]

    # Write in JSON format to file {"category": [["word", tfidf], ...], ...}
    try:
        with open(out_json, 'w', encoding='utf-8') as output_file:
            json.dump(result, output_file, indent=4)
        print(f"TF-IDF scores written to {out_json}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

def main():
    tfidf_file = "categorized_tfidfs.json" # File with each term and its tfidf score, for each category in the typology
    stopwords_list = "Analysis/stopwords.txt" # stopwords to exclude from tfidf rankings
    category_files = group_lines_by_category("Annotation/dialogue_annotated.tsv") # group dialogue by category
    freq_lists = process_files_to_word_frequencies(category_files, stopwords_list) # calculate term frequency
    build_tfidf_lists(freq_lists, category_files, tfidf_file) # use frequency to find tfidf

if __name__ == "__main__":
    main()