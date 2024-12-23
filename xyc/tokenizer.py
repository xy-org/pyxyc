import re


def split_tokens(code):
    prev_pos = 0
    tokens = []
    pos = []
    splitre = re.compile(
        r'((?:[a-zA-Z_]\w+)|'
        r'(?:\")|'
        r'(?:0[\da-zA-Z]+(?:\(\d+\))?)|(?:\.\d+f?)|(?:\d+(?:\.\d*f?)?)|(?:->)|'
        r'(?:;;)|(?:\|\|)|(?:<<)|(?:>>)|(?:\+\+)|(?:\-\-)|(?:[+\-*\/&|!=><]=)|'
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
            tok = code[start:end]
            if tok == ";;":
                # insert and additional ';' in order to simplify parsing
                insert_semicolomn = False
                for i in range(prev_pos-1, -1, -1):
                    if code[i] == '\n':
                        break
                    elif code[i] == ';':
                        break
                    elif code[i].isalnum():
                        insert_semicolomn = True
                        break
                if insert_semicolomn:
                    tokens.append(";")
                    pos.append(start)
            tokens.append(tok)
            pos.append(start)
        prev_pos = end

    if prev_pos < len(code):
        tokens.append(code[prev_pos:])
        pos.append(prev_pos)

    return tokens, pos