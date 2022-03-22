import nltk
import sys
import os
import string
import numpy as np

from sklearn.cluster import k_means

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
    dict = {}
    for filename in os.listdir(directory):
        with open (os.path.join(directory, filename)) as f:
            dict[str(filename)] = f.read()
    return dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    word_list_temp = nltk.tokenize.word_tokenize(document)
    word_list = []
    for word in word_list_temp:
        if word not in string.punctuation and word not in nltk.corpus.stopwords.words("english"):
            word_list.append(word.lower())
    return word_list


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    dict = {}
    num_of_documents = len(documents)
    for key in documents:
        for word in documents[key]:
            if word not in dict:#New encounter of the word
                dict[word] = np.log((num_of_documents/num_documents_with_word(documents, word)))
    return dict


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    files_tf_idf = {file: 0 for file in files}
    for file in files:
        for word in query:
            if word in files[file]:
                files_tf_idf[file] += idfs[word]* files[file].count(word)
    return sorted(list(files.keys()), key=lambda k: files_tf_idf[k], reverse=True)[:n]
    # return [filename for filename, v in sorted(files_tf_idf.items(), key=lambda item: item[1], reverse=True)][:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    sentence_idf = {sentence: 0 for sentence in sentences}
    query_term_density = {sentence: 0 for sentence in sentences} 
    for sentence in sentences:
        for word in query:
            if word in sentences[sentence]:
                sentence_idf[sentence] += idfs[word]
                query_term_density[sentence] += 1/len(sentences[sentence])
    return sorted(list(sentences.keys()), key=lambda k: (sentence_idf[k], query_term_density[k]), reverse=True)[:n]

def num_documents_with_word(documents, word):
    count = 0
    for key in documents:
        if word in documents[key]:
            count += 1
    return count

if __name__ == "__main__":
    main()
