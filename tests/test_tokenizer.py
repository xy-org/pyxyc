import pytest
from xyc.tokenizer import split_tokens

@pytest.mark.parametrize("code, tokens, token_pos", [
    ("", [], []),
    (" ", [], []),
    ("\n", ["\n"], [0]),
    (" abc", ["abc"], [1]),
    ("import a", ["import", "a"], [0, 7]),
    (
        "import xylib.module.str",
        ["import", "xylib", ".", "module", ".", "str"],
        [0, 7, 12, 13, 19, 20]
    ),
    (
        "import xylib .module.str",
        ["import", "xylib", ".", "module", ".", "str"],
        [0, 7, 13, 14, 20, 21]
    ),
    (
        "import xylib. module.str",
        ["import", "xylib", ".", "module", ".", "str"],
        [0, 7, 12, 14, 20, 21]
    ),
    (
        " import.b,-:\n",
        ["import", ".", "b", ",", "-:", "\n"],
        [1, 7, 8, 9, 10, 12]
    ),
    (
        "# abc",
        ["#", "abc"],
        [0, 2]
    ),
    (
        "#abc",
        ["#", "abc"],
        [0, 1]
    ),
    (
        "; abc",
        [";", "abc"],
        [0, 2]
    ),
    (
        ";;",
        [";;"],
        [0]
    ),
    (
        "def main~EntryPoint()->int{}",
        ["def", "main", "~", "EntryPoint", "(", ")", "->", "int", "{", "}"],
        None
    ),
    (
        "a := 5 + 0.3 + .3 - 4. + 3 .+ 4 .-",
        ["a", ":", "=", "5", "+", "0.3", "+", ".3", "-", "4.", "+", "3",
         ".", "+", "4", ".", "-"],
        None
    ),
    (
        "0 0xFFA 0b00111 0766 0AnyStringYouLike(36) 0Cafe(16)us",
        ["0", "0xFFA", "0b00111", "0766", "0AnyStringYouLike(36)", "0Cafe(16)us"],
        None
    ),
    (
        "3.14 3.14f .5 9^0.5",
        ["3.14", "3.14f", ".5", "9", "^", "0.5"],
        None
    ),
    (
        "return e(a'b.c[d], f);",
        ["return", "e", "(", "a", "'", "b", ".", "c", "[", "d", "]",
         ",", "f", ")", ";"],
        None
    ),
    (
        """def f(x:int)
        >> x > 0
        {}""",
        ["def", "f", "(", "x", ":", "int", ")", "\n", ">>", "x", ">",
         "0", "\n", "{", "}"],
        None
    ),
    (
        "a := b \\func c;",
        ["a", ":", "=", "b", "\\", "func", "c", ";"],
        None
    ),
    (
        "func1(a'func2, func3(), 4);",
        ["func1", "(", "a", "'", "func2", ",", "func3", "(", ")", ",", "4", ")", ";"],
        None
    ),
    (
        "func0x10(); call_me(); _hidden;",
        ["func0x10", "(", ")", ";", "call_me", "(", ")", ";", "_hidden", ";"],
        None
    ),
    (
        '"str"; f"str"; f"str{expr}";',
        ['"', 'str', '"', ";", 'f', '"', 'str', '"', ";", 'f', '"', 'str', "{", "expr", "}", '"', ";"],
        None
    ),
    (
        'f"str\\{expr\\}";',
        ['f', '"', 'str', '\\', '{', 'expr', '\\', '}', '"', ';'],
        None
    ),
    (
        'f "str"',
        ['f', '"', 'str', '"'],
        None
    ),
    (
        '"line1\\line2\\n"',
        ['"', 'line1', '\\', 'line2', '\\', 'n', '"'],
        None
    ),
    (
        'f"before{a+b}after";',
        ['f', '"', 'before', '{', 'a', '+', 'b', '}', 'after', '"', ';'],
        None
    ),
    (
        'f"str={str("abc")}";',
        ['f', '"', 'str', '=', '{', 'str', '(', '"', 'abc', '"', ')', '}', '"', ';'],
        None
    ),
    (
        's := "\\" \\\\ \\a \\b \\f \\n \\0";',
        ['s', ':', '=', '"', '\\', '"', '\\', '\\', '\\', 'a', '\\', 'b',
         '\\', 'f', '\\', 'n', '\\', '0', '"', ';'],
        None
    ),
    (
        's := "    ";',
        ['s', ':', '=', '"', '"', ';'],
        [0, 2, 3, 5, 10, 11],
    ),
    (
        'b := !a',
        ['b', ':', '=', '!', 'a'],
        None
    ),
    (
        'a := b++; c--; --d;',
        ['a', ':', '=', 'b', '++', ';', 'c', '--', ';', '--', 'd', ';'],
        None
    ),
    (
        'a += b;',
        ['a', '+=', 'b', ';'],
        None
    ),
    (
        'a == b; a <= b; a |= b;',
        ['a', '==', 'b', ';', 'a', '<=', 'b', ';', 'a', '|=', 'b', ';'],
        None
    ),
    (
        'a *= 2 ;; comment',
        ['a', '*=', '2', ';;', 'comment'],
        [0, 2, 5, 7, 10]
    ),
    (
        'i *= i; ;; square i',
        ['i', '*=', 'i', ';', ';;', 'square', 'i'],
        None
    ),
    (
        "struct Type~Tag {} ;; comment\n",
        ['struct', 'Type', '~', 'Tag', '{', '}', ';;', 'comment', '\n'],
        None
    ),
    (
        "a = .pending; a = . pending; a =. pending; a=.pending; \n",
        ['a', '=', '.', 'pending', ';', 'a', '=', '.', 'pending', ';',
         'a', '=', '.', 'pending', ';', 'a', '=', '.', 'pending', ';', "\n"],
        None
    ),
    (
        "a = 3.14; a = .14; a =.14; a = 3. 14;",
        ['a', '=', '3.14', ';', "a", "=", ".14", ";",
         "a", "=", ".14", ";", "a", "=", "3.", "14", ";"],
        None
    ),
    (
        'a : b',
        ['a', ':', 'b'],
        None
    ),
    (
        'a +: b',
        ['a', '+:', 'b'],
        None
    ),
    (
        'a +: + b',
        ['a', '+:', '+', 'b'],
        None
    ),
    (
        'b:=:;',
        ['b', ':', '=', ':', ';'],
        None
    ),
    (
        'b: a..to',
        ['b', ':', 'a', '..', 'to'],
        None
    ),
    (
        'b: a...to',  # invalid expression but let's document how it is parsed
        ['b', ':', 'a', '...', 'to'],
        None
    ),
    (
        'b: %a = a',
        ['b', ':', '%', 'a', '=', 'a'],
        None
    ),
    (
        'b: %func(a, c)',
        ['b', ':', '%', 'func', '(', 'a', ',', 'c', ')'],
        None
    ),
    (
        'a .= {b=val};',
        ['a', '.=', '{', 'b', '=', 'val', '}', ';'],
        None
    ),
    (
        "a := 5..tag;",
        ['a', ':', '=', '5.', '.', 'tag', ';'],
        None
    ),
    (
        "a := f(...);",
        ['a', ':', '=', 'f', '(', '...', ')', ';'],
        None
    ),
    (
        "def func(y:Tag = ^x..elem)",
        ['def', 'func', '(', 'y', ':', 'Tag', '=', '^', 'x', '..', 'elem', ')'],
        None
    ),
    (
        "struct 2Struct {}",
        ['struct', '2Struct', '{', '}'],
        None
    ),
    (
        "p1.x = 10.0f;",
        ['p1', '.', 'x', '=', '10.0f', ';'],
        None
    ),
    (
        "a =< b;",
        ['a', '=<', 'b', ';'],
        None
    ),
    (
        "c :=< b;",
        ['c', ':', '=<', 'b', ';'],
        None
    ),
    (
        'f"{#! cast }"',
        ['f', '"', '{', '#', '!', 'cast', '}', '"'],
        None
    ),
    (
        'val := `a`;',
        ['val', ':', '=', '`', 'a', '`', ';'],
        None
    ),
    (
        'val := `\\n`;',
        ['val', ':', '=', '`', '\\', 'n', '`', ';'],
        None
    ),
    (
        'val := f"""\nmulti line\n""";',
        ['val', ':', '=', 'f', '"""', '\n', 'multi', 'line', '\n', '"""', ';'],
        None
    ),
    (
        '10_000 0xAA_BB 0_733 0x_AF(16) 0x_AF()b',
        ['10_000', '0xAA_BB', '0_733', '0x_AF(16)', '0x_AF()b'],
        None
    ),
    (
        'a && b || c',
        ['a', '&&', 'b', '||', 'c'],
        None
    ),
    (
        'import libxy.(cli, array);',
        ['import', 'libxy', '.', '(', 'cli', ',', 'array', ')', ';'],
        None
    ),
    (
        's @= val;',
        ['s', '@=', 'val', ';'],
        None
    ),
    (
        's @ val; s@val;',
        ['s', '@', 'val', ';', 's', '@', 'val', ';'],
        None
    ),
])
def test_split_tokens(code, tokens, token_pos):
    res = split_tokens(code)
    assert res[0] == tokens
    if token_pos is not None:
        assert res[1] == token_pos

@pytest.mark.parametrize("code, tokens, token_pos", [
    (
        "a := .5.;", # invalid expression but let's document how it is parsed
        ['a', ':', '=', '.5.', ';'],
        None
    ),
    (
        "a := .5 . ;", # invalid expression but let's document how it is parsed
        ['a', ':', '=', '.5', '.', ';'],
        None
    ),
    (
        "a := ..tag;", # invalid expression but let's document how it is parsed
        ['a', ':', '=', '..', 'tag', ';'],
        None
    ),
    (
        "a := ..5;", # invalid expression but let's document how it is parsed
        ['a', ':', '=', '..', '5', ';'],
        None
    ),
    (
        "a := 0.5.0;", # invalid expression but let's document how it is parsed
        ['a', ':', '=', '0.5', '.0', ';'],
        None
    ),
    (
        "a := ...;", # invalid expression but let's document how it is parsed
        ['a', ':', '=', '...', ';'],
        None
    ),
    (
        "a := ....;", # invalid expression but let's document how it is parsed
        ['a', ':', '=', '...', '.', ';'],
        None
    ),
])
def test_split_invalid_expressions(code, tokens, token_pos):
    # this test documents how invalid expressions are tokenized
    res = split_tokens(code)
    assert res[0] == tokens
    if token_pos is not None:
        assert res[1] == token_pos