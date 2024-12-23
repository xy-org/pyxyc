import pytest
from xyc.parser import parse_code, ParsingError
from xyc import ast


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
                    ast.StrLiteral(parts=[ast.Const("abc")])
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
                tags=ast.TagList(args=[ast.Id("EntryPoint")]),
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
                tags=ast.TagList(args=[ast.Id("EntryPoint")]),
                params=[
                    ast.Param("a", type=ast.Type("int")),
                    ast.Param("b", type=ast.Type("long"))
                ],
                rtype=ast.Type("int"),
                etype=ast.Type("Error"),
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
        """def main() -> void {
            func(a);
            a'func;
            a'func(b);
            a \\func b;
        }
        """,
        [
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.FuncCall("func", args=[ast.Id("a")]),
                ast.FuncCall("func", args=[ast.Id("a")]),
                ast.FuncCall("func", args=[ast.Id("a"), ast.Id("b")]),
                ast.FuncCall("func", args=[ast.Id("a"), ast.Id("b")]),
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
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
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
                    value=ast.FuncCall("addr", args=[ast.Id("ptr")]),
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
                    "func2",
                    [
                        ast.FuncCall("func1", [ast.Id("a")]),
                        ast.FuncCall("func2", [ast.Id("b")]),
                    ]
                )),
                ast.VarDecl("g", type=None, value=ast.FuncCall(
                    "func3",
                    [
                        ast.FuncCall("func2", [ast.FuncCall("func1", [
                            ast.BinExpr(ast.Id("a"), ast.Id("b"), "+")
                        ])]),
                        ast.FuncCall("func4", [ast.Id("c")])
                    ]
                )),
                ast.FuncCall("func", [
                    ast.Id("a"),
                    ast.FuncCall("func", [ast.Id("b")]),
                    ast.FuncCall("add", [ast.Id("d"), ast.Id("c")]),
                ])
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
                    name=ast.Id("int"), args=[ast.Const(1)]
                )),
                ast.VarDecl("p", type=None, value=ast.StructLiteral(
                    name=ast.Id("Pair"), args=[ast.Const(1), ast.Id("a")]
                )),
                ast.FuncCall("func2", args=[
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
                name="func", rtype=ast.Type("void"), body=[],
                tags=ast.TagList(args=[
                    ast.Id("Tag")
                ])
            ),
            ast.FuncDef(
                name="func", rtype=ast.Type("void"), body=[],
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
                name="func", rtype=ast.Type("void"), body=[],
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
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.VarDecl("empty", type=None, value=ast.StrLiteral(
                    parts=[]
                )),
                ast.VarDecl("str", type=None, value=ast.StrLiteral(
                    parts=[ast.Const("abc")]
                )),
                ast.VarDecl("prefixed", type=None, value=ast.StrLiteral(
                    prefix="prefix",
                    parts=[ast.Const("String with prefix")]
                )),
            ]),
        ]
    ],
    [
        """def main() -> void {
            f := f"before{a + b}after";
            g := f"complex {a + b, 2, arg=3}";
            h := f"literal {arg=MyStruct{field=10}}";
        }
        """,
        [
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.VarDecl("f", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Const("before"),
                        ast.BinExpr(ast.Id("a"), ast.Id("b"), "+"),
                        ast.Const("after"),
                    ]
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
                    ]
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
                    ]
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
            ast.FuncDef(name="main", rtype=ast.Type("void"), body=[
                ast.VarDecl("empty", type=None, value=ast.ArrLit(
                    elems=[]
                )),
                ast.VarDecl("arr", type=None, value=ast.ArrLit(
                    elems=[ast.Const(2.718), ast.Const(3.14)]
                )),
                ast.VarDecl("uninitialized", varying=True, type=ast.ArrType(
                    base=ast.Id("int"),
                    dims=[ast.Const(10)]
                )),
                ast.VarDecl("m", type=ast.ArrType(
                        base=ast.Id("int"),
                        dims=[ast.Const(2), ast.Const(2)]
                    ), value=ast.ArrLit(
                        [
                            ast.ArrLit([ast.Const(1), ast.Const(2)]),
                            ast.ArrLit([ast.Const(3), ast.Const(4)]),
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
            ast.FuncDef(name="main", rtype=ast.Type("Str"), body=[
                ast.VarDecl("m", type=ast.ArrType(
                    base=ast.Id("int"),
                    dims=[ast.Const(2), ast.Const(2)]
                ), value=ast.ArrLit(elems=[
                    ast.ArrLit([ast.Const(0), ast.Const(1)]),
                    ast.ArrLit([ast.Const(2), ast.Const(3)]),
                ]
                )),
                ast.VarDecl("letters", type=None, value=ast.ArrLit(
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
            ast.FuncDef(name="sum", rtype=ast.Type("int"), params=[
                ast.Param(
                    "nums", type=ast.ArrType(
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
])
def test_arrays(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast
