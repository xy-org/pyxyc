import pytest
from xyc.parser import parse_code, ParsingError
import xyc.ast as ast


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
    [
        "import libc~[CLib{headers=[c\"unistd.h\"]}] in c",
        [
            ast.Import(lib="libc", in_name="c", tags=ast.TagList(
                args=[ast.StructLiteral(
                    ast.Id("CLib"),
                    kwargs={
                        "headers": ast.ArrayLit([
                            ast.StrLiteral(
                                prefix="c", parts=[ast.Const("unistd.h")],
                                full_str="unistd.h"
                            )
                        ])
                    }
                )]
            )),
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
    [
        """
;; function
def main() {}
        """,
        [
            ast.Comment(
                comment=";; function", is_doc=True
            ),
            ast.FuncDef(
                name=ast.Id("main")
            )
        ]
    ],
    [
        """
def main() -> int {
    # i := 0
    return i;
}
        """,
        [
            ast.FuncDef(
                name=ast.Id("main"),
                body=[
                    ast.Comment(" i := 0"),
                    ast.Return(ast.Id("i")),
                ],
                returns=ast.SimpleRType("int"),
            )
        ]
    ],
    [
        """
def main(i: int) -> int {
    i *= i; # square i
    i *= i; ;; square i
    i *= i ;; square i
    return i;
}
        """,
        [
            ast.FuncDef(
                name=ast.Id("main"),
                params=[ast.param("i", type=ast.Id("int"))],
                body=[
                    ast.BinExpr(arg1=ast.Id("i"), arg2=ast.Id("i"), op="*="),
                    ast.Comment(" square i"),
                    ast.BinExpr(arg1=ast.Id("i"), arg2=ast.Id("i"), op="*="),
                    ast.Comment(";; square i", is_doc=True),
                    ast.BinExpr(arg1=ast.Id("i"), arg2=ast.Id("i"), op="*="),
                    ast.Comment(";; square i", is_doc=True),
                    ast.Return(ast.Id("i")),
                ],
                returns=ast.SimpleRType("int"),
            )
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
            ast.FuncDef(ast.Id("main"), params=[],
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[
                    ast.FuncCall(name=ast.Id("print"), args=[
                        ast.StrLiteral(parts=[ast.Const("abc")], full_str="abc")
                    ])
                ]
            ),
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
            ast.FuncDef(
                ast.Id("main"),
                returns=[ast.VarDecl(type=ast.Id("int"))],
            ),
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
                ast.Id("main"),
                tags=ast.TagList(args=[ast.Id("EntryPoint")]),
                returns=[ast.VarDecl(type=ast.Id("int"))],
                body=[
                    ast.Return(value=ast.Const(0))
                ]
            ),
        ]
    ],
    [
        """
        def main~EntryPoint(a: int, b: long) -> int || Error
        >> a > b;
        {
            return a+b;
        }
        """,
        [
            ast.FuncDef(
                ast.Id("main"),
                tags=ast.TagList(args=[ast.Id("EntryPoint")]),
                params=[
                    ast.param("a", type=ast.Id("int")),
                    ast.param("b", type=ast.Id("long"))
                ],
                returns=[ast.VarDecl(type=ast.Id("int"))],
                etype=ast.Id("Error"),
                in_guards=[
                    ast.BinExpr(ast.Id("a"), ast.Id("b"), ">")
                ],
                body=[
                    ast.Return(
                        ast.BinExpr(ast.Id("a"), ast.Id("b"), "+")
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
        """def func() -> (int, int) {
           return 0, 1;
        }
        """,
        [
            ast.FuncDef(ast.Id("func"), params=[],
                returns=[
                    ast.VarDecl(type=ast.Id("int")),
                    ast.VarDecl(type=ast.Id("int")),
                ],
                body=[
                    ast.Return(value=[ast.Const(0), ast.Const(1)])
                ]
            ),
        ]
    ],
    [
        """def func() -> (a: int, b: int) {
           return 0, 1;
        }
        """,
        [
            ast.FuncDef(ast.Id("func"), params=[],
                returns=[
                    ast.VarDecl(name="a", type=ast.Id("int"), varying=True),
                    ast.VarDecl(name="b", type=ast.Id("int"), varying=True),
                ],
                body=[
                    ast.Return(value=[ast.Const(0), ast.Const(1)])
                ]
            ),
        ]
    ],
    [
        """
        def double(x: int) x * 2
        def sqr(x: int) = x * x
        """,
        [
            ast.FuncDef(ast.Id("double"),
                params=[
                    ast.param("x", type=ast.Id("int")),
                ],
                body=ast.BinExpr(ast.Id("x"), ast.Const(2), op="*")
            ),
            ast.FuncDef(ast.Id("sqr"),
                params=[
                    ast.param("x", type=ast.Id("int")),
                ],
                body=ast.BinExpr(ast.Id("x"), ast.Id("x"), op="*")
            ),
        ]
    ],
    [
        """
        def pseudoParam(x: pseudo int) 0
        def unnamedParam(:int) 0
        """,
        [
            ast.FuncDef(ast.Id("pseudoParam"),
                params=[
                    ast.param("x", type=ast.Id("int"), is_pseudo=True),
                ],
                body=ast.Const(0)
            ),
            ast.FuncDef(ast.Id("unnamedParam"),
                params=[
                    ast.param(type=ast.Id("int"), is_pseudo=True),
                ],
                body=ast.Const(0)
            ),
        ]
    ],
    [
        """
        def func(x: int) -> void || Error {
            error Error{x};
        }
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[
                    ast.param("x", type=ast.Id("int")),
                ],
                returns=[
                    ast.VarDecl(type=ast.Id("void")),
                ],
                etype=ast.Id("Error"),
                body=[
                    ast.Error(ast.StructLiteral(
                        name=ast.Id("Error"),
                        args=[
                            ast.Id("x")
                        ]
                    )),
                ]
            ),
        ]
    ],
])
def test_parse_advanced_funcs(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def func(a: int, b: int = 0, c := a + b) -> int {
        }
        """,
        [
            ast.FuncDef(ast.Id("func"),
                returns=[
                    ast.VarDecl(type=ast.Id("int")),
                ],
                params=[
                    ast.VarDecl(
                        "a", type=ast.Id("int"), is_param=True, is_in=True
                    ),
                    ast.VarDecl(
                        "b", type=ast.Id("int"), value=ast.Const(0),
                        is_param=True, is_in=True
                    ),
                    ast.VarDecl(
                        "c", value=ast.BinExpr(ast.Id("a"), ast.Id("b"), op="+"),
                        is_param=True, is_in=True
                    ),
                ],
                body=[
                ],
            ),
        ]
    ],
])
def test_parse_default_param_values(code, exp_ast):
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
            ast.FuncDef(
                ast.Id("main"),
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a")]),
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a")]),
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a"), ast.Id("b")]),
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a"), ast.Id("b")]),
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
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", type=None, value=ast.Id("b")),
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
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("b", type=None, value=ast.Const(0)),
                ast.VarDecl("c", type=ast.Id("int"), value=ast.Const(5)),
                ast.VarDecl("cv", type=ast.Id("int"), varying=True),
                ast.VarDecl(
                    "a", type=None,
                    value=ast.BinExpr(
                        ast.BinExpr(ast.Id("b"), ast.Const(5), "+"),
                        ast.Id("c"),
                        "-"
                    )
                ),
                ast.VarDecl("d", type=None, value=ast.Const(10), varying=True),
                ast.VarDecl("pi", type=None, value=ast.Const(3.14, "3.14f", "float")),
                ast.VarDecl(
                    "ptr",
                    type=ast.AttachTags(
                        ast.Id("Ptr"), tags=ast.TagList([ast.Id("int")])
                    ),
                    value=None, varying=True
                ),
                ast.VarDecl(
                    "pp",
                    type=ast.AttachTags(
                        ast.Id("Ptr"),
                        tags=ast.TagList([ast.AttachTags(
                            ast.Id("Ptr"), tags=ast.TagList([ast.Id("int")])
                        )]),
                    ),
                    value=ast.FuncCall(ast.Id("addr"), args=[ast.Id("ptr")]),
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
            a := :;
            b:=:;
            c := :a;
            d := a:;
            e := :a+b;
            f := (a:):(:b):(d);
            (a: int) = 5;
            g[a:b] = c[e:f];
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", value=ast.SliceExpr()),
                ast.VarDecl("b", value=ast.SliceExpr()),
                ast.VarDecl("c", value=ast.SliceExpr(end=ast.Id("a"))),
                ast.VarDecl("d", value=ast.SliceExpr(start=ast.Id("a"))),
                ast.VarDecl("e", value=ast.SliceExpr(
                    end=ast.BinExpr(ast.Id("a"), ast.Id("b"), op="+"),
                )),
                ast.VarDecl("f", value=ast.SliceExpr(
                    start=ast.SliceExpr(start=ast.Id("a")),
                    end=ast.SliceExpr(end=ast.Id("b")),
                    step=ast.Id("d"),
                )),
                ast.VarDecl(
                    "a",
                    type=ast.Id("int"),
                    value=ast.Const(5),
                ),
                ast.BinExpr(
                    arg1=ast.Select(
                        ast.Id("g"),
                        args=ast.Args(
                            [ast.SliceExpr(ast.Id("a"), ast.Id("b"))]
                        )
                    ),
                    arg2=ast.Select(
                        ast.Id("c"),
                        args=ast.Args(
                            [ast.SliceExpr(ast.Id("e"), ast.Id("f"))]
                        )
                    ),
                    op="=",
                )
            ]),
        ]
    ],
])
def test_parse_slices(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            a := 0 + 1 * 2 + 3;
            b := (0 + 1) * (2 + 3);
            c := (0 + 1) * 2 + 3;
            d := 0 * 1 + 2 * 3;
            e := (a + b - a + b);
            f := a'func1 \\func2 b'func2;
            g := (a + b)'func1'func2 \\func3 c'func4;
            func(a, b'func, d \\add c);
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
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
                ast.VarDecl("b", type=None, value=ast.BinExpr(
                    arg1 = ast.BinExpr(
                        arg1=ast.Const(0),
                        arg2=ast.Const(1),
                        op = "+"
                    ),
                    arg2 = ast.BinExpr(
                        arg1=ast.Const(2),
                        arg2=ast.Const(3),
                        op = "+"
                    ),
                    op = "*"
                )),
                ast.VarDecl("c", type=None, value=ast.BinExpr(
                    arg1 = ast.BinExpr(
                        arg1=ast.BinExpr(
                            ast.Const(0),
                            ast.Const(1),
                            "+"
                        ),
                        arg2=ast.Const(2),
                        op = "*"
                    ),
                    arg2 = ast.Const(3),
                    op = "+"
                )),
                ast.VarDecl("d", type=None, value=ast.BinExpr(
                    arg1 = ast.BinExpr(
                        ast.Const(0),
                        ast.Const(1),
                        "*"
                    ),
                    arg2 = ast.BinExpr(
                        ast.Const(2),
                        ast.Const(3),
                        "*"
                    ),
                    op = "+"
                )),
                ast.VarDecl("e", type=None, value=ast.BinExpr(
                    ast.BinExpr(
                        ast.BinExpr(
                            ast.Id("a"), ast.Id("b"), "+"
                        ),
                        ast.Id("a"), "-"
                    ),
                    ast.Id("b"),
                    op = "+"
                )),
                ast.VarDecl("f", type=None, value=ast.FuncCall(
                    ast.Id("func2"),
                    [
                        ast.FuncCall(ast.Id("func1"), [ast.Id("a")]),
                        ast.FuncCall(ast.Id("func2"), [ast.Id("b")]),
                    ]
                )),
                ast.VarDecl("g", type=None, value=ast.FuncCall(
                    ast.Id("func3"),
                    [
                        ast.FuncCall(ast.Id("func2"), [ast.FuncCall(ast.Id("func1"), [
                            ast.BinExpr(ast.Id("a"), ast.Id("b"), "+")
                        ])]),
                        ast.FuncCall(ast.Id("func4"), [ast.Id("c")])
                    ]
                )),
                ast.FuncCall(ast.Id("func"), [
                    ast.Id("a"),
                    ast.FuncCall(ast.Id("func"), [ast.Id("b")]),
                    ast.FuncCall(ast.Id("add"), [ast.Id("d"), ast.Id("c")]),
                ]),
            ]),
        ]
    ],
    [
        """def main() -> void {
            minusone := -1;
            plusone := +1;
            addneg := a + -5;
            negadd := -b + a*-c;
            notOp := !a & !true & !b | !(c & d);
            doubleMinus := -b - -c;
            a := b~Tag-c;
        }""",
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("minusone", type=None, value=ast.Const(-1)),
                ast.VarDecl("plusone", value=ast.Const(1)),
                ast.VarDecl("addneg", value=ast.BinExpr(
                    op="+",
                    arg1=ast.Id("a"),
                    arg2=ast.Const(-5)
                )),
                ast.VarDecl("negadd", value=ast.BinExpr(
                    op="+",
                    arg1=ast.UnaryExpr(op='-', arg=ast.Id("b")),
                    arg2=ast.BinExpr(
                        op='*',
                        arg1=ast.Id("a"),
                        arg2=ast.UnaryExpr(op="-", arg=ast.Id("c"))
                    )
                )),
                ast.VarDecl("notOp", value=ast.BinExpr(
                    op='|',
                    arg1=ast.BinExpr(
                        op='&',
                        arg1=ast.BinExpr(
                            op='&',
                            arg1=ast.UnaryExpr(op='!', arg=ast.Id("a")),
                            arg2=ast.UnaryExpr(
                                op='!', arg=ast.Const(True, "true", "bool")
                            ),
                        ),
                        arg2=ast.UnaryExpr(op='!', arg=ast.Id("b")),
                    ),
                    arg2=ast.UnaryExpr(op='!', arg=ast.BinExpr(
                        op='&',
                        arg1=ast.Id("c"),
                        arg2=ast.Id("d"),
                    )),
                )),
                ast.VarDecl("doubleMinus", value=ast.BinExpr(
                    op='-',
                    arg1=ast.UnaryExpr(op='-', arg=ast.Id("b")),
                    arg2=ast.UnaryExpr(op='-', arg=ast.Id("c")),
                )),
                ast.VarDecl("a", value=ast.BinExpr(
                    op='-',
                    arg1=ast.AttachTags(arg=ast.Id("b"), tags=ast.TagList(
                        args=[ast.Id("Tag")]
                    )),
                    arg2=ast.Id("c"),
                )),
            ]),
        ]
    ],
    [
        """def main() -> void {
            a : var = 1;
            b := a++;
            a++;
            c := b--;
            d := a++ + b;
            f := d---b;
        }""",
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", value=ast.Const(1), varying=True),
                ast.VarDecl("b", value=ast.UnaryExpr(arg=ast.Id("a"), op="++")),
                ast.UnaryExpr(op="++", arg=ast.Id("a")),
                ast.VarDecl("c", value=ast.UnaryExpr(op="--", arg=ast.Id("b"))),
                ast.VarDecl("d", value=ast.BinExpr(
                    op="+",
                    arg1=ast.UnaryExpr(op="++", arg=ast.Id("a")),
                    arg2=ast.Id("b")
                )),
                ast.VarDecl("f", value=ast.BinExpr(
                    op="-",
                    arg1=ast.UnaryExpr(op="--", arg=ast.Id("d")),
                    arg2=ast.Id("b")
                )),
            ])
        ]
    ]
])
def test_expressions(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, err_msg", [
    ("""def func() -> void {
        ++a;
    }""",
     "Prefix increment and decrement are not supported"),
    ("""def func() -> void {
        b := ++a;
    }""",
     "Prefix increment and decrement are not supported"),
    ("""def func() -> void {
        a+;
    }""",
     "Unexpected end of expression"),
    ("""def func() -> void {
        a----b;
    }""",
     "Malformed expression."),
    ("""def func() -> void {
        a-- b;
    }""",
     "Malformed expression."),
    ("""def func() -> void {
        (b + (a+1)
    }""",
     "Missing closing bracket"),
])
def test_invalid_expressions(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


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
                ast.VarDecl("ptr", type=ast.Id("Ptr"), varying=False),
                ast.VarDecl("len", type=ast.Id("Size"), varying=False),
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
                ast.VarDecl("name", type=ast.Id("Str"), varying=False),
            ], tags=ast.TagList(
                kwargs={"copy": ast.Id("False")}
            )),
        ]
    ],
    [
        "struct Count~Unit {} ;; Units of count i.e. 1, 2, 3 of something\n",
        [
            ast.StructDef(name="Count", fields=[], tags=ast.TagList(
                [ast.Id("Unit")]
            )),
            ast.Comment(";; Units of count i.e. 1, 2, 3 of something", is_doc=True)
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
            ast.FuncDef(ast.Id("func"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", type=None, value=ast.StructLiteral(
                    name=ast.Id("int"), args=[ast.Const(1)]
                )),
                ast.VarDecl("p", type=None, value=ast.StructLiteral(
                    name=ast.Id("Pair"), args=[ast.Const(1), ast.Id("a")]
                )),
                ast.FuncCall(ast.Id("func2"), args=[
                    ast.BinExpr(
                        arg1=ast.StructLiteral(
                            name=ast.Id("Pair"), args=[ast.Const(3), ast.Const(4)]
                        ),
                        arg2=ast.StructLiteral(
                            name=ast.Id("Pair"), args=[ast.Const(5), ast.Const(6)]
                        ),
                        op="*"
                    )
                ]),
                ast.VarDecl("b", type=ast.AttachTags(
                    ast.Id("ComplexType"), tags=ast.TagList([
                        ast.StructLiteral(ast.Id("OtherType"), args=[])
                    ])
                ), value=ast.Const(5)),
                ast.VarDecl(
                    "c", varying=True, type=ast.AttachTags(
                        ast.Id("Ptr"), tags=ast.TagList([
                            ast.StructLiteral(
                                ast.AttachTags(
                                    ast.Id("Type2"),
                                    tags=ast.TagList([
                                        ast.StructLiteral(
                                            ast.Id("Type3"),
                                            kwargs={"val": ast.StructLiteral(
                                                ast.Id("Type4"),
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
                ast.Id("func"), returns=ast.SimpleRType("void"), body=[],
                tags=ast.TagList(args=[
                    ast.Id("Tag")
                ])
            ),
            ast.FuncDef(
                ast.Id("func"), returns=ast.SimpleRType("void"), body=[],
                tags=ast.TagList(args=[
                    ast.StructLiteral(
                        name=ast.Id("Tag"),
                        kwargs={
                            "val": ast.Const(1)
                        }
                    )
                ])
            ),
            ast.FuncDef(
                ast.Id("func"), returns=ast.SimpleRType("void"), body=[],
                tags=ast.TagList(args=[
                    ast.StructLiteral(
                        name=ast.Id("Tag"),
                        kwargs={
                            "val": ast.StructLiteral(
                                name=ast.Id("Tag2"),
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


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            empty := "";
            str := "abc";
            prefixed := prefix"String with prefix";
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("empty", type=None, value=ast.StrLiteral(
                    parts=[]
                )),
                ast.VarDecl("str", type=None, value=ast.StrLiteral(
                    parts=[ast.Const("abc")], full_str="abc"
                )),
                ast.VarDecl("prefixed", type=None, value=ast.StrLiteral(
                    prefix="prefix",
                    parts=[ast.Const("String with prefix")],
                    full_str="String with prefix"
                )),
            ]),
        ]
    ],
    [
        """def main() -> void {
            f := f"before{a + b}after";
            g := f"complex {a + b, 2, arg=3}";
            h := f"literal {arg=MyStruct{field=10}}";
            i := f"{a}{b} {c}\n{d} ";
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("f", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Const("before"),
                        ast.BinExpr(ast.Id("a"), ast.Id("b"), "+"),
                        ast.Const("after"),
                    ],
                    full_str="before{a + b}after"
                )),
                ast.VarDecl("g", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Const("complex "),
                        ast.Args([
                            ast.BinExpr(ast.Id("a"), ast.Id("b"), "+"),
                            ast.Const(2),
                        ], {
                            "arg": ast.Const(3)
                        }),
                    ],
                    full_str="complex {a + b, 2, arg=3}",
                )),
                ast.VarDecl("h", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Const("literal "),
                        ast.Args([], {
                            "arg": ast.StructLiteral(
                                name=ast.Id("MyStruct"),
                                kwargs={
                                    "field": ast.Const(10)
                                }
                            )
                        }),
                    ],
                    full_str="literal {arg=MyStruct{field=10}}"
                )),
                ast.VarDecl("i", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Id("a"),
                        ast.Id("b"),
                        ast.Const(" "),
                        ast.Id("c"),
                        ast.Const("\n"),
                        ast.Id("d"),
                        ast.Const(" "),
                    ],
                    full_str="{a}{b} {c}\n{d} "
                )),
            ]),
        ]
    ],
    [
        """def main() -> void {
            s := "\\" \\\\ \\a \\b \\f \\n \\r \\t \\v \\x \\0 \\\\\\\\";
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("s", type=None, value=ast.StrLiteral(
                    parts=[
                        ast.Const(
                            "\\\" \\\\ \\a \\b \\f \\n \\r \\t \\v \\x \\0 "
                            "\\\\\\\\"
                        ),
                    ],
                    full_str='\\" \\\\ \\a \\b \\f \\n \\r \\t \\v \\x \\0 \\\\\\\\',
                )),
            ]),
        ]
    ],
])
def test_parse_string_literals(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            empty := [];
            arr := [2.718, 3.14];
            uninitialized : int[10];
            m: int[2, 2] = [[1, 2], [3, 4]];
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("empty", type=None, value=ast.ArrayLit(
                    elems=[]
                )),
                ast.VarDecl("arr", type=None, value=ast.ArrayLit(
                    elems=[ast.Const(2.718), ast.Const(3.14)]
                )),
                ast.VarDecl("uninitialized", varying=True, type=ast.ArrayType(
                    base=ast.Id("int"),
                    dims=[ast.Const(10)]
                )),
                ast.VarDecl("m", type=ast.ArrayType(
                        base=ast.Id("int"),
                        dims=[ast.Const(2), ast.Const(2)]
                    ), value=ast.ArrayLit(
                        [
                            ast.ArrayLit([ast.Const(1), ast.Const(2)]),
                            ast.ArrayLit([ast.Const(3), ast.Const(4)]),
                        ]
                    )
                )
            ]),
        ]
    ],
    [
        """def main() -> Str {
            m: int[2, 2] = [[0, 1], [2, 3]];
            letters := ["a", "b", "c", "d"];
            return letters[m[1, 0]];
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("Str"), body=[
                ast.VarDecl("m", type=ast.ArrayType(
                    base=ast.Id("int"),
                    dims=[ast.Const(2), ast.Const(2)]
                ), value=ast.ArrayLit(elems=[
                    ast.ArrayLit([ast.Const(0), ast.Const(1)]),
                    ast.ArrayLit([ast.Const(2), ast.Const(3)]),
                ]
                )),
                ast.VarDecl("letters", type=None, value=ast.ArrayLit(
                    elems=[
                        ast.SimpleStr("a"), ast.SimpleStr("b"),
                        ast.SimpleStr("c"), ast.SimpleStr("d")
                    ]
                )),
                ast.Return(value=ast.Select(
                    base=ast.Id("letters"),
                    args=ast.Args([
                        ast.Select(
                            base=ast.Id("m"),
                            args=ast.Args([
                                ast.Const(1), ast.Const(0)
                            ])
                        )
                    ])
                )),
            ]),
        ]
    ],
    [
        """def sum(nums: int[2]) -> int {
            return nums[0] + nums[1];
        }
        """,
        [
            ast.FuncDef(ast.Id("sum"), returns=ast.SimpleRType("int"), params=[
                ast.param(
                    "nums", type=ast.ArrayType(
                        base=ast.Id("int"),
                        dims=[ast.Const(2)],
                    )
                )
                ], body=[
                ast.Return(ast.BinExpr(
                    ast.Select(ast.Id('nums'), ast.Args([ast.Const(0)])),
                    ast.Select(ast.Id('nums'), ast.Args([ast.Const(1)])),
                    '+'
                ))
            ]),
        ]
    ],
    [
        """def mkArray() -> int[2] {
            return [0, 1];
        }
        """,
        [
            ast.FuncDef(
                ast.Id("mkArray"),
                returns=[
                    ast.VarDecl(
                        type=ast.ArrayType(ast.Id("int"), dims=[ast.Const(2)])
                    ),
                ],
                body=[
                    ast.Return(ast.ArrayLit(elems=[
                        ast.Const(0),
                        ast.Const(1),
                    ]))
                ]
            ),
        ]
    ],
])
def test_arrays(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            if (cond) {
                expr;
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.IfExpr(
                    cond=ast.Id("cond"),
                    block=ast.Block(body=[ast.Id("expr")]),
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            if (cond) {
                expr1;
            } else {
                expr2;
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.IfExpr(
                    cond=ast.Id("cond"),
                    block=ast.Block(body=[ast.Id("expr1")]),
                    else_node=ast.Block(body=[ast.Id("expr2")]),
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            if (cond1) {
                expr1;
            } elif(cond2) {
                expr2;
            } else {
                expr3;
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.IfExpr(
                    cond=ast.Id("cond1"),
                    block=ast.Block(body=[ast.Id("expr1")]),
                    else_node=ast.IfExpr(
                        cond=ast.Id("cond2"),
                        block=ast.Block(body=[ast.Id("expr2")]),
                        else_node=ast.Block(body=[ast.Id("expr3")]),
                    ),
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            a := if (cond1) 5 elif (cond2) 6 else 7;
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl(name="a", value=ast.IfExpr(
                    cond=ast.Id("cond1"),
                    block=ast.Block(body=ast.Const(5)),
                    else_node=ast.IfExpr(
                        cond=ast.Id("cond2"),
                        block=ast.Block(body=ast.Const(6)),
                        else_node=ast.Block(body=ast.Const(7)),
                    ),
                ))
            ]),
        ]
    ],
    [
        """def main() -> void {
            a := if (cond) {
                func1();
                func2();
            } else {
                func3();
            };
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl(name="a", value=ast.IfExpr(
                    cond=ast.Id("cond"),
                    block=ast.Block(body=[
                        ast.FuncCall(name=ast.Id("func1")),
                        ast.FuncCall(name=ast.Id("func2")),
                    ]),
                    else_node=ast.Block(body=[
                        ast.FuncCall(name=ast.Id("func3")),
                    ]),
                ))
            ]),
        ]
    ],
    [
        """def main() -> void {
            a := if ifname(cond) -> (res: int) {
                res = func1();
                func2();
            } else {
                res = func3();
            };
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl(name="a", value=ast.IfExpr(
                    name=ast.Id("ifname"),
                    cond=ast.Id("cond"),
                    block=ast.Block(body=[
                        ast.BinExpr(
                            op="=",
                            arg1=ast.Id("res"),
                            arg2=ast.FuncCall(name=ast.Id("func1")),
                        ),
                        ast.FuncCall(name=ast.Id("func2")),
                    ], returns=[
                        ast.VarDecl(name="res", type=ast.Id("int"), varying=True)
                    ]),
                    else_node=ast.Block(body=[
                        ast.BinExpr(
                            op="=",
                            arg1=ast.Id("res"),
                            arg2=ast.FuncCall(name=ast.Id("func3")),
                        )
                    ]),
                ))
            ]),
        ]
    ],
])
def test_if(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            while (a < b) {
                a += b;
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.WhileExpr(
                    cond=ast.BinExpr(op="<", arg1=ast.Id("a"), arg2=ast.Id("b")),
                    block=ast.Block(body=[
                        ast.BinExpr(op='+=', arg1=ast.Id("a"), arg2=ast.Id("b")),
                    ])
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            while (a < b) {
                a += b;
            } else {
                b += a;
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.WhileExpr(
                    cond=ast.BinExpr(op="<", arg1=ast.Id("a"), arg2=ast.Id("b")),
                    block=ast.Block(body=[
                        ast.BinExpr(op='+=', arg1=ast.Id("a"), arg2=ast.Id("b")),
                    ]),
                    else_node=ast.Block(body=[
                         ast.BinExpr(op='+=', arg1=ast.Id("b"), arg2=ast.Id("a")),
                    ])
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            return while res(a < b) -> int {
                res += a;
                a += b;
            };
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.Return(
                    ast.WhileExpr(
                        name=ast.Id("res"),
                        cond=ast.BinExpr(op="<", arg1=ast.Id("a"), arg2=ast.Id("b")),
                        block=ast.Block(body=[
                            ast.BinExpr(op='+=', arg1=ast.Id("res"), arg2=ast.Id("a")),
                            ast.BinExpr(op='+=', arg1=ast.Id("a"), arg2=ast.Id("b")),
                        ], returns=ast.SimpleRType("int")),
                    )
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            return while (i < arr'len) -> (sum: int) sum += arr[i];
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.Return(
                    ast.WhileExpr(
                        cond=ast.BinExpr(
                            op="<", arg1=ast.Id("i"),
                            arg2=ast.FuncCall(ast.Id("len"), [ast.Id("arr")])),
                        block=ast.Block(body=ast.BinExpr(
                            op='+=',
                            arg1=ast.Id("sum"),
                            arg2=ast.Select(ast.Id("arr"), ast.Args([ast.Id("i")]))),
                        returns=[ast.VarDecl("sum", ast.Id("int"), varying=True)])
                    )
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            while (a < b) {
                a += b;
                if (a > 10) break;
            };
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.WhileExpr(
                    cond=ast.BinExpr(
                        op="<", arg1=ast.Id("a"),
                        arg2=ast.Id("b")
                    ),
                    block=ast.Block(body=[
                        ast.BinExpr(op='+=', arg1=ast.Id("a"), arg2=ast.Id("b")),
                        ast.IfExpr(
                            cond=ast.BinExpr(op=">", arg1=ast.Id("a"), arg2=ast.Const(10)),
                            block=ast.Block(body=ast.Break())
                        ),
                    ])
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            while outer(a < b) {
                while inner(b < c) {
                    if (c < d) {
                        break outer;
                    }
                }
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.WhileExpr(
                    name=ast.Id("outer"),
                    cond=ast.BinExpr(op="<", arg1=ast.Id("a"), arg2=ast.Id("b")),
                    block=ast.Block(body=[
                        ast.WhileExpr(
                            name=ast.Id("inner"),
                            cond=ast.BinExpr(op="<", arg1=ast.Id("b"), arg2=ast.Id("c")),
                            block=ast.Block(body=[
                                ast.IfExpr(
                                    cond=ast.BinExpr(op="<", arg1=ast.Id("c"), arg2=ast.Id("d")),
                                    block=ast.Block(body=[
                                        ast.Break(ast.Id("outer"))
                                    ])
                                )
                            ])
                        )
                    ])
                )
            ]),
        ]
    ],
])
def test_while(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            return do -> (res: int) {
                a += 10;
                res += a;
            } while name(a > b);
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.Return(ast.DoWhileExpr(
                    name=ast.Id("name"),
                    cond=ast.BinExpr(op=">", arg1=ast.Id("a"), arg2=ast.Id("b")),
                    block=ast.Block(body=[
                        ast.BinExpr(op="+=", arg1=ast.Id("a"), arg2=ast.Const(10)),
                        ast.BinExpr(op="+=", arg1=ast.Id("res"), arg2=ast.Id("a")),
                    ],returns=[ast.VarDecl("res", ast.Id("int"), varying=True)])
                ))
            ]),
        ]
    ],
])
def test_do_while(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def main() -> void {
            for (elem in arr) {
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.ForExpr(
                    over=[
                        ast.BinExpr(op="in", arg1=ast.Id("elem"), arg2=ast.Id("arr"))
                    ],
                    block=ast.Block()
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            for (e1 in arr1, e2 in arr2) {
            } else {
                x = b;
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.ForExpr(
                    over=[
                        ast.BinExpr(op="in", arg1=ast.Id("e1"), arg2=ast.Id("arr1")),
                        ast.BinExpr(op="in", arg1=ast.Id("e2"), arg2=ast.Id("arr2"))
                    ],
                    block=ast.Block(),
                    else_node=ast.Block(body=[
                        ast.BinExpr(op="=", arg1=ast.Id("x"), arg2=ast.Id("b"))
                    ])
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            for (i in :, e in arr, i'isPrime) {
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.ForExpr(
                    over=[
                        ast.BinExpr(
                            op="in",
                            arg1=ast.Id("i"),
                            arg2=ast.SliceExpr()
                        ),
                        ast.BinExpr(
                            op="in",
                            arg1=ast.Id("e"),
                            arg2=ast.Id("arr")
                        ),
                        ast.FuncCall(ast.Id("isPrime"), args=[ast.Id("i")])
                    ],
                    block=ast.Block()
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            for (e in arr) -> (or: bool = true) or |= e;
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.ForExpr(
                    over=[
                        ast.BinExpr(
                            op="in",
                            arg1=ast.Id("e"),
                            arg2=ast.Id("arr")
                        ),
                    ],
                    block=ast.Block(body=ast.BinExpr(
                        op="|=", arg1=ast.Id("or"), arg2=ast.Id("e")
                    ),
                    returns=[
                        ast.VarDecl("or", ast.Id("bool"), varying=True,
                                    value=ast.Const(True, "true", "bool"))
                    ]),
                )
            ]),
        ]
    ],
])
def test_for(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        pi := 3.14;
        c := 299792458~mps;
        """,
        [
            ast.VarDecl("pi", value=ast.Const(3.14)),
            ast.VarDecl("c", value=ast.AttachTags(
                ast.Const(299792458), tags=ast.TagList(
                    [ast.Id("mps")]
                )
            ))
        ]
    ],
])
def test_global_constants(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast