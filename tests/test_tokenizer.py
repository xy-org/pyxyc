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
        ["import", "xylib", " ", ".", "module", ".", "str"],
        [0, 7, 12, 13, 14, 20, 21]
    ),
    (
        "import xylib. module.str",
        ["import", "xylib", ".", " ", "module", ".", "str"],
        [0, 7, 12, 13, 14, 20, 21]
    ),
    (
        " import.b,-:\n",
        ["import", ".", "b", ",", "-", ":", "\n"],
        [1, 7, 8, 9, 10, 11, 12]
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
        ["a", ":", "=", "5", "+", "0.3", "+", ".3", "-", "4.", "+", "3", " ",
         ".", "+", "4", " ", ".", "-"],
        None
    ),
    (
        "0 0xFFA 0b00111 0766 0AnyStringYouLike(36)",
        ["0", "0xFFA", "0b00111", "0766", "0AnyStringYouLike(36)"],
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
])
def test_split_tokens(code, tokens, token_pos):
    res = split_tokens(code)
    assert res[0] == tokens
    if token_pos is not None:
        assert res[1] == token_pos