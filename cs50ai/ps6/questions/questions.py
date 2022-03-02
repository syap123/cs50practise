import nltk
import sys
import os
import math
from collections import Counter
import string

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    file_contents = {}

    for root, subdirectories, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            split_path = path.split(os.sep)
            filename = split_path[-1]
            if filename.split('.')[-1] != 'txt':
                continue
            with open(path) as f:
                s = f.read()
            file_contents[filename] = s
    return file_contents


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = nltk.word_tokenize(document.lower())

    processed_words = []
    for word in words:
        # should also lemmatise words but will leave it for now
        if word not in nltk.corpus.stopwords.words("english") and word not in string.punctuation:
            processed_words.append(word)
    return processed_words   


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    word_docset = {}

    for document in documents:
        for word in documents[document]:
            if word not in word_docset:
                word_docset[word] = {'appear_in_documents':set()}
            word_docset[word]['appear_in_documents'].add(document)

    num_documents = len(documents)

    for word in word_docset:
        word_docset[word] = math.log(num_documents/len(word_docset[word]['appear_in_documents']))

    return word_docset


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    file_tfidf = {}
    
    for file in files:
        word_tf = Counter(files[file])
        if file not in file_tfidf:
            file_tfidf[file] = {}
        for word in query:
            if word in word_tf:
                file_tfidf[file][word] = word_tf[word] * idfs[word]

    for file in file_tfidf:
        sum_tfidf = 0
        for word in file_tfidf[file]:
            sum_tfidf = sum_tfidf + file_tfidf[file][word]
        file_tfidf[file] = sum_tfidf

    top_file_list = sorted(file_tfidf, key=(lambda key:file_tfidf[key]), reverse=True)

    return top_file_list[:n]
    


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_metrics = {}
    
    for sentence in sentences:
        word_tf = Counter(sentences[sentence])
        if sentence not in sentence_metrics:
            sentence_metrics[sentence] = {}
        for word in query:
            if word in word_tf:
                sentence_metrics[sentence][word] = {'idfs':idfs[word]}
                sentence_metrics[sentence][word]['td'] = word_tf[word]

    for sentence in sentence_metrics:
        sum_idf = 0
        for word in sentence_metrics[sentence]:
            sum_idf = sum_idf + sentence_metrics[sentence][word]['idfs']
        sentence_metrics[sentence] = {'idf':sum_idf}
        query_words_appear_in_sentence = 0
        for word in query:
            if word in word_tf:
                query_words_appear_in_sentence = query_words_appear_in_sentence + word_tf[word]
        query_term_density = query_words_appear_in_sentence / len(sentences[sentence])

        sentence_metrics[sentence]['qtd'] = query_term_density

    top_sentences_list = sorted(sentence_metrics, key=(lambda key:(sentence_metrics[key]['idf'], sentence_metrics[key]['qtd']) ), reverse=True)

    return top_sentences_list[:n]


if __name__ == "__main__":
    main()
