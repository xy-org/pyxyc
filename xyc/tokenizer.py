import re


def split_tokens(code):
    prev_pos = 0
    tokens = []
    pos = []
    splitre = re.compile(
        r'((?:[a-zA-Z_]\w+)|'
        r'(?:\")|'
        r'(?:0[\da-zA-Z]+(?:\(\d+\))?)|(?:\.\d+f?)|(?:\d+(?:\.\d*f?)?)|(?:->)|'
        r'(?:;;)|(?:<<)|(?:>>)|'
        r'[+\-*\/&|!=><\n\.,\-:~()\[\]{};#\'\\]|[\t ]+(?=\.\D)|(?<=\D\.)[\t ])|'
        r'[\t ]+'
    )

    for match in re.finditer(splitre, code):
        start = match.start()
        end = match.end()
        if prev_pos != start:
            tokens.append(code[prev_pos:start])
            pos.append(prev_pos)
        if match.group(1) is not None:
            tokens.append(code[start:end])
            pos.append(start)
        prev_pos = end

    if prev_pos < len(code):
        tokens.append(code[prev_pos:])
        pos.append(prev_pos)

    return tokens, pos