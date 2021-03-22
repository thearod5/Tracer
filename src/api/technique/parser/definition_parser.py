"""
Lisp parser copied from : https://norvig.com/lispy.html
"""
Symbol = str  # A Scheme Symbol is implemented as a Python str
SNumber = (int, float)  # A Scheme Number is implemented as a Python int or float
Atom = (Symbol, SNumber)  # A Scheme Atom is a Symbol or Number
SList = list  # A Scheme List is implemented as a Python list
Exp = (Atom, SList)  # A Scheme expression is an Atom or List
Env = dict  # A Scheme environment (defined below)


# is a mapping of {variable: value}
def tokenize(chars: str) -> SList:
    """
    Convert a string of characters into a list of tokens.
    :param chars: TODO
    :return:
    """
    return chars.replace("(", " ( ").replace(")", " ) ").split()


def parse_technique_definition(program: str) -> Exp:
    """
    Read a Scheme expression from a string.
    :param program: TODO
    :return:
    """
    return read_from_tokens(tokenize(program))


def read_from_tokens(tokens: list) -> Exp:
    """
    Read an expression from a sequence of tokens.
    :param tokens: TODO
    :return:
    """
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF")
    token = tokens.pop(0)
    if token == "(":
        token_list = []
        while tokens[0] != ")":
            token_list.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return token_list
    if token == ")":
        raise SyntaxError("unexpected )")
    return token
