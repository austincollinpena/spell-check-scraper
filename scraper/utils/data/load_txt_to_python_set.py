# Load words from a txt file into a set
def load_words(file: str):
    with open(file) as word_file:
        valid_words = set(word_file.read().lower().split())
    return valid_words
