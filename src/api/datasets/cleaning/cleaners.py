"""
TODO
"""
import functools
import re

from nltk.stem import PorterStemmer

from api.constants.paths import PATH_TO_STOP_WORDS

ps = PorterStemmer()

with open(PATH_TO_STOP_WORDS) as stop_word_file:
    stop_words = list(filter(lambda w: w != "", map(lambda w: w.lower(), stop_word_file.read().split("\n"))))
assert len(stop_words) > 0, "Could not load stop words file"


def split_chained_calls(line):
    """
    TODO
    :param line:
    :return:
    """
    return line.replace(".", " ").strip()


def separate_camel_case(doc: str):
    """
    TODO
    :param doc:
    :return:
    """
    split_doc = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', doc)).split()
    return " ".join(split_doc)


def remove_stop_words(doc):
    """
    TODO
    :param doc:
    :return:
    """
    word_tokens = doc.split(" ")
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    cleaned = " ".join(filtered_sentence)
    return cleaned


def is_alpha_or_space(letter):
    """
    TODO
    :param letter:
    :return:
    """
    return str.isalpha(letter) or str.isspace(letter)


def remove_non_alphanumeric_characters(doc):
    """
    TODO
    :param doc:
    :return:
    """
    return ''.join(filter(is_alpha_or_space, doc))


def to_lower(doc):
    """
    TODO
    :param doc:
    :return:
    """
    return " ".join(map(lambda word: word.lower(), doc.split(" ")))


def remove_one_name_words(doc):
    """
    TODO
    :param doc:
    :return:
    """
    return " ".join(list(filter(lambda w: len(w) > 1, doc.split(" "))))


def stem_doc(doc):
    """
    Removes numbers, newlines, parenthesis, stems words, and makes them all lower case
    :param doc: {String} The uncleaned string.
    :return: {String} Cleaned string.
    """
    if doc is None:
        raise Exception("Received None as text document")
    return " ".join([ps.stem(word) for word in doc.split(" ")])


CLEANING_PIPELINE = [
    split_chained_calls,
    remove_non_alphanumeric_characters,  # remaining non-alpha chars are not part of code
    separate_camel_case,
    remove_one_name_words,
    to_lower,
    remove_stop_words,
    stem_doc]


def clean_doc(doc, stop_at_index=None):
    """
    TODO
    :param doc:
    :param stop_at_index:
    :return:
    """
    pipeline = CLEANING_PIPELINE[:stop_at_index]
    return functools.reduce(lambda acc, value: value(acc), pipeline, doc)
