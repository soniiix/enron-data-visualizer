from nltk.corpus import stopwords
import nltk

def getExcludedWords():
    """
    Renvoie un ensemble de mots à exclure (stopwords).

    Utile pour analyser de manière cohérente un message.
    """
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    custom_excluded_words = {"ect", "hou", "com"}
    excluded_words = stop_words | custom_excluded_words
    return excluded_words