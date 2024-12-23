import pytest
from xyc.tokenizer import split_tokens
from xyc.parser import parse_code, ParsingError
from xyc import ast

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


code_ast = [
    [
        "import xylib",
        [
            ast.Import(lib="xylib")
        ],
    ],
    [
        "import xylib.string",
        [
            ast.Import(lib="xylib.string")
        ],
    ],
    [
        "import xylib in xy\n",
        [
            ast.Import(lib="xylib", in_name="xy"),
        ],
    ],
]
@pytest.mark.parametrize("code, exp_ast", code_ast)
def test_parse_import(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


code_ast = [
    ("import xylib.str, xylib.re", "Unexpected token"),
    ("from xylib import method in c", "The correct syntax to import a library"),
]
@pytest.mark.parametrize("code, err_msg", code_ast)
def test_parse_import_error(code, err_msg):
    act_error = None
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


@pytest.mark.parametrize("code, exp_ast", [
    [
        """# multi word comment
        """,
        [
            ast.Comment(comment=" multi word comment")
        ]
    ],
    [
        """#""",
        [
            ast.Comment(comment="")
        ]
    ],
    [
        """#
        """,
        [
            ast.Comment(comment="")
        ]
    ],
    [
        """#  comment with leading and trailing spaces  
        """,
        [
            ast.Comment(comment="  comment with leading and trailing spaces  ")
        ]
    ],
    [
        """#comment 1
;; comment 2
# comment 3
        """,
        [
            ast.Comment(comment="comment 1"),
            ast.Comment(comment=";; comment 2", is_doc=True),
            ast.Comment(comment=" comment 3"),
        ]
    ],
    [
        """
;; comment part 1
;; comment part 2
        """,
        [
            ast.Comment(
                comment=";; comment part 1\n;; comment part 2", is_doc=True
            ),
        ]
    ],
])
def test_parse_comments(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            print("abc");
        }
        """,
        [
            ast.FuncDef(name="main", params=[], rtype=ast.Type("void"), body=[
                ast.FuncCall(name="print", args=[
                    ast.Var(name="\"abc\"")
                ])
            ])
        ]
    ],
    [
        """# multi word comment
        import xylib

        def main() -> int {
        }
        """,
        [
            ast.Comment(" multi word comment"),
            ast.Import(lib="xylib"),
            ast.FuncDef(name="main", rtype=ast.Type("int"), body=[]),
        ]
    ],
    [
        """# multi word comment
        import xylib

        def main~EntryPoint() -> int {
            return 0;
        }
        """,
        [
            ast.Comment(" multi word comment"),
            ast.Import(lib="xylib"),
            ast.FuncDef(
                name="main",
                tags=ast.TagList(positional=[ast.Var("EntryPoint")]),
                rtype=ast.Type("int"), body=[
                    ast.Return(value=ast.Const(0))
                ]
            ),
        ]
    ],
    [
        """
        def main~EntryPoint(a: int, b: long) -> int | Error
        >> a > b;
        {
            return a+b;
        }
        """,
        [
            ast.FuncDef(
                name="main",
                tags=ast.TagList(positional=[ast.Var("EntryPoint")]),
                params=[
                    ast.Param("a", type=ast.Type("int")),
                    ast.Param("b", type=ast.Type("long"))
                ],
                rtype=ast.Type("int"),
                etype=ast.Type("Error"),
                in_guards=[
                    ast.BinExpr(ast.Var("a"), ast.Var("b"), ">")
                ],
                body=[
                    ast.Return(
                        ast.BinExpr(ast.Var("a"), ast.Var("b"), "+")
                    )
                ]
            )
        ]
    ],
])
def test_parse_simple_func(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            func(a);
            a'func;
            a'func(b);
            a \\func b;
        }
        """,
        [
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.FuncCall("func", args=[ast.Var("a")]),
                ast.FuncCall("func", args=[ast.Var("a")]),
                ast.FuncCall("func", args=[ast.Var("a"), ast.Var("b")]),
                ast.FuncCall("func", args=[ast.Var("a"), ast.Var("b")]),
            ]),
        ]
    ],
])
def test_parse_func_call(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            a := b;
        }
        """,
        [
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.VarDecl("a", type=None, value=ast.Var("b")),
            ]),
        ]
    ],
    [
        """def main() -> void {
            b := 0;
            c : int = 5;
            cv : int;
            a := b + 5 - c;
            d : var = 10;
            pi := 3.14f;
            ptr: Ptr~int;
            pp: Ptr~Ptr~int = ptr'addr;
        }
        """,
        [
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.VarDecl("b", type=None, value=ast.Const(0)),
                ast.VarDecl("c", type=ast.Var("int"), value=ast.Const(5)),
                ast.VarDecl("cv", type=ast.Var("int"), varying=True),
                ast.VarDecl(
                    "a", type=None,
                    value=ast.BinExpr(
                        ast.BinExpr(ast.Var("b"), ast.Const(5), "+"),
                        ast.Var("c"),
                        "-"
                    )
                ),
                ast.VarDecl("d", type=None, value=ast.Const(10), varying=True),
                ast.VarDecl("pi", type=None, value=ast.Const(3.14, "3.14f", "float")),
                ast.VarDecl(
                    "ptr",
                    type=ast.AttachTags(
                        ast.Var("Ptr"), ast.TagList([ast.Var("int")])
                    ),
                    value=None, varying=True
                ),
                ast.VarDecl(
                    "pp",
                    type=ast.AttachTags(
                        ast.Var("Ptr"),
                        ast.TagList([ast.AttachTags(
                            ast.Var("Ptr"), ast.TagList([ast.Var("int")])
                        )]),
                    ),
                    value=ast.FuncCall("addr", args=[ast.Var("ptr")]),
                ),
            ]),
        ]
    ],
])
def test_parse_var_decl(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            a := 0 + 1 * 2 + 3;
        }
        """,
        [
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.VarDecl("a", type=None, value=ast.BinExpr(
                    arg1 = ast.BinExpr(
                        arg1=ast.Const(0),
                        arg2=ast.BinExpr(
                            arg1=ast.Const(1),
                            arg2=ast.Const(2),
                            op="*"
                        ),
                        op = "+"
                    ),
                    arg2 = ast.Const(3),
                    op = "+"
                )),
            ]),
        ]
    ],
])
def test_expressions(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """struct Str{}
        """,
        [
            ast.StructDef(name="Str", fields=[]),
        ]
    ],
    [
        """struct Str{
            ptr: Ptr;
            len: Size;
        }
        """,
        [
            ast.StructDef(name="Str", fields=[
                ast.VarDecl("ptr", type=ast.Var("Ptr"), varying=False),
                ast.VarDecl("len", type=ast.Var("Size"), varying=False),
            ]),
        ]
    ],
    [
        """struct MyName~[copy=False] {
            name: Str;
        }
        """,
        [
            ast.StructDef(name="MyName", fields=[
                ast.VarDecl("name", type=ast.Var("Str"), varying=False),
            ], tags=ast.TagList(
                named={"copy": ast.Var("False")}
            )),
        ]
    ],
])
def test_parse_struct(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        def func() -> void {
            a := int{1};
            p := Pair{1, a};
            func2(Pair{3, 4} * Pair{5, 6});
            b: ComplexType~[OtherType{}] = 5;
            c: Ptr~[Type2~[Type3{val=Type4{val=5}}]{val=1}];
        }
        """,
        [
            ast.FuncDef(name="func", rtype=ast.Type("void"), body=[
                ast.VarDecl("a", type=None, value=ast.StructLiteral(
                    name=ast.Var("int"), args=[ast.Const(1)]
                )),
                ast.VarDecl("p", type=None, value=ast.StructLiteral(
                    name=ast.Var("Pair"), args=[ast.Const(1), ast.Var("a")]
                )),
                ast.FuncCall("func2", args=[
                    ast.BinExpr(
                        arg1=ast.StructLiteral(
                            name=ast.Var("Pair"), args=[ast.Const(3), ast.Const(4)]
                        ),
                        arg2=ast.StructLiteral(
                            name=ast.Var("Pair"), args=[ast.Const(5), ast.Const(6)]
                        ),
                        op="*"
                    )
                ]),
                ast.VarDecl("b", type=ast.AttachTags(
                    ast.Var("ComplexType"), ast.TagList([
                        ast.StructLiteral(ast.Var("OtherType"), args=[])
                    ])
                ), value=ast.Const(5)),
                ast.VarDecl(
                    "c", varying=True, type=ast.AttachTags(
                        ast.Var("Ptr"), ast.TagList([
                            ast.StructLiteral(
                                ast.AttachTags(
                                    ast.Var("Type2"),
                                    tags=ast.TagList([
                                        ast.StructLiteral(
                                            ast.Var("Type3"),
                                            kwargs={"val": ast.StructLiteral(
                                                ast.Var("Type4"),
                                                kwargs={
                                                    "val": ast.Const(5)
                                                }
                                            )}
                                        )
                                    ])
                                ),
                                kwargs={
                                    "val": ast.Const(1)
                                }
                            ),
                        ])
                    )
                ),
            ]),
        ]
    ],
])
def test_struct_literals(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        def func~Tag() -> void {}
        def func~[Tag{val=1}]() -> void {}
        def func~[Tag{val=Tag2{val2=2}}]() -> void {}
        """,
        [
            ast.FuncDef(
                name="func", rtype=ast.Type("void"), body=[],
                tags=ast.TagList(positional=[
                    ast.Var("Tag")
                ])
            ),
            ast.FuncDef(
                name="func", rtype=ast.Type("void"), body=[],
                tags=ast.TagList(positional=[
                    ast.StructLiteral(
                        name=ast.Var("Tag"),
                        kwargs={
                            "val": ast.Const(1)
                        }
                    )
                ])
            ),
            ast.FuncDef(
                name="func", rtype=ast.Type("void"), body=[],
                tags=ast.TagList(positional=[
                    ast.StructLiteral(
                        name=ast.Var("Tag"),
                        kwargs={
                            "val": ast.StructLiteral(
                                name=ast.Var("Tag2"),
                                kwargs={
                                    "val2": ast.Const(2)
                                }
                            ),
                        }
                    )
                ])
            ),
        ]
    ],
])
def test_func_def_with_tags(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


code_ast = [
    ("def func~Tag1~Tag2~Tag3() -> void {}",
     "These long chains of tags get very ambiguous. "
     "Please be explicit and seprate the tags in square brackets."),
    ("def func() -> void {c : Ptr~Type2{val=1}~Type3{val=Type4{val=5}};}",
     "Only simple positional tags can be chained. "
     "Please be explicit and put the tags in square brackets.")
]
@pytest.mark.parametrize("code, err_msg", code_ast)
def test_ambiguous_tags(code, err_msg):
    act_error = None
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)