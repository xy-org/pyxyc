import re


def split_tokens(code):
    prev_pos = 0
    tokens = []
    pos = []
    splitre = re.compile(
        r'((?:[a-zA-Z_]\w+)|'
        r'(?:\"\"\")|(?:\")|(?:\`)|'
        r'(?:\.?\d[\da-zA-Z_]*(?:\.[\da-zA-Z_]*)?(?:\(\d*\)\w*)?)|'
        r'(?:->)|(?:;;)|(?:\|\|)|(?:&&)|(?:<<)|(?:>>)|(?:\+\+)|(?:\-\-)|(?:[\.+\-*\/&|!=><]=)|(?:=[<>])|'
        r'(?:\.\.\.?)|(?:[\.+\-*\/&|><]:)|[\^+\-*\/&|!=><\n\.,\-:~()\[\]{};#%\'\\])|'
        r'[\t ]+'
    )

    for match in re.finditer(splitre, code):
        start = match.start()
        end = match.end()
        if prev_pos != start:
            tokens.append(code[prev_pos:start])
            pos.append(prev_pos)
        if match.group(1) is not None:
            tok = code[start:end]
            tokens.append(tok)
            pos.append(start)
        prev_pos = end

    if prev_pos < len(code):
        tokens.append(code[prev_pos:])
        pos.append(prev_pos)

    return tokens, pos