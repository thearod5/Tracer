"""
TODO
"""
import javac_parser
from comment_parser import comment_parser
from comment_parser.comment_parser import UnsupportedError

from api.constants.paths import PATH_TO_RESERVED_WORDS
from api.datasets.cleaning import cleaners
from api.datasets.cleaning.cleaners import is_alpha_or_space

java = javac_parser.Java()


def create_class_doc(class_text, stop_at_index=None):
    """
    Extracts the identifiers from the given java class and cleans each identifier.
    Cleaning includes removing non-alphanumeric characters, splitting chained method calls,
    split camel case phrases, and stemming each word.
    : param class_text - A string representing a compiling java class.
    : param stop_at_index - Used for testing to stop the cleaning process before a certain step (e.g. Stemming)
    """
    class_doc = extract_java_identifiers(class_text)
    class_doc = cleaners.clean_doc(class_doc, stop_at_index)
    return class_doc


def extract_java_identifiers(class_text):
    """
    Returns a string of space-delimited code identifiers from given text
    :param class_text: a string containing some java source code
    :return:
    """

    parsed_syntax_items = java.lex(class_text)
    java_reserved_words = get_java_reserved_words()

    def filter_java_identifier(syntax_item):
        # returns true if identifier and not a reserved word
        word_label = syntax_item[0]
        word = syntax_item[1]
        return word_label == "IDENTIFIER" and word.lower() not in java_reserved_words

    identifiers = list(
        map(lambda id: id[-1], filter(filter_java_identifier, parsed_syntax_items))
    )
    assert (
        len(identifiers) > 0
    ), "Not enough identifiers found in class text. Perhaps file is commented out."
    return " ".join(identifiers) + extract_class_comments(class_text)


def extract_class_comments(class_text, mime_type="text/x-java-source"):
    """
    Extracts the class or inline comments in given source file
    :param class_text: the str representation of the source file
    :param mime_type: the type of source file to parse.
    See https://pypi.org/project/comment-parser/ for list of potential mime_types.
    :return: string of comments in class without any comment related syntax
    """
    try:
        comments = comment_parser.extract_comments_from_str(str(class_text), mime_type)
    except UnsupportedError:
        return ""

    def get_clean_comment(comment):
        body = comment.text()
        words = body.split(" ")
        clean_words = []
        for word in words:
            if len(word) == 0 or not is_alpha_or_space(word[0]):
                continue
            clean_words.append(word.strip())

        return " ".join(clean_words).replace("\n", "")

    return " ".join(list(map(get_clean_comment, comments)))


def get_java_reserved_words():
    """
    Returns a list of java reserved words or unwanted class identifiers (e.g. Double, String, Integer, etc. wrapper
    classes).
    """
    reserved_keywords_file = open(PATH_TO_RESERVED_WORDS, "r")
    words_file_content = reserved_keywords_file.read()
    reserved_keywords_file.close()
    words = map(lambda word: word.strip(), words_file_content.split("\n"))
    words = filter(lambda word: len(word) != 0, words)
    words = list(words)
    assert len(words) > 0
    return words
