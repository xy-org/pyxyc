import pytest
from xyc.parser import parse_code, ParsingError
import xyc.ast as ast


code_ast = [
    [
        "import xylib;",
        [
            ast.Import(lib="xylib")
        ],
    ],
    [
        "import xylib.string;",
        [
            ast.Import(lib="xylib.string")
        ],
    ],
    [
        "import xylib in xy;\n",
        [
            ast.Import(lib="xylib", in_name="xy"),
        ],
    ],
    [
        "import libc~[CLib{headers=@{c\"unistd.h\"}}] in c;",
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
    ("import xylib.str, xylib.re", "Importing more than one module at a time is NYI."),
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
        ]
    ],
    [
        """#""",
        [
        ]
    ],
    [
        """#
        """,
        [
        ]
    ],
    [
        """#  comment with leading and trailing spaces  
        """,
        [
        ]
    ],
    [
        """#comment 1
;; comment 2
# comment 3
        """,
        [
            ast.Comment(comment=";; comment 2"),
        ]
    ],
    [
        """
;; comment part 1
;; comment part 2
        """,
        [
            ast.Comment(
                comment=";; comment part 1\n;; comment part 2"
            ),
        ]
    ],
    [
        """
;; function
def main() {}
        """,
        [
            ast.FuncDef(
                name=ast.Id("main"),
                comment=";; function"
            )
        ]
    ],
    [
        """
def main() -> int {
    return i;
}
        """,
        [
            ast.FuncDef(
                name=ast.Id("main"),
                body=[
                    ast.Return(ast.Id("i")),
                ],
                returns=ast.SimpleRType("int"),
            )
        ]
    ],
    [
        """
def main(i: int) -> int {
    i *= i; # first square i
    i *= i; ;; square i
    i *= i ;; square i again
    return i;
}
        """,
        [
            ast.FuncDef(
                name=ast.Id("main"),
                params=[ast.param("i", type=ast.Id("int"))],
                body=[
                    ast.BinExpr(arg1=ast.Id("i"), arg2=ast.Id("i"), op="*="),
                    ast.BinExpr(arg1=ast.Id("i"), arg2=ast.Id("i"), op="*=", comment=";; square i"),
                    ast.BinExpr(arg1=ast.Id("i"), arg2=ast.Id("i"), op="*=", comment=";; square i again"),
                    ast.Return(ast.Id("i")),
                ],
                returns=ast.SimpleRType("int"),
            )
        ]
    ],
    [
        "import xylib;; Used for stuff\n",
        [
            ast.Import(lib="xylib", comment=";; Used for stuff"),
        ],
    ],
    [
        """def func(
            x: Float, ;; x coordinate
            y: Float = 0, ;; y coordinate
            ;; z
            ;; coordinate
            z: Float = 0,
        ) {}""",
        [
            ast.FuncDef(ast.Id("func"), body=[], params=[
                ast.VarDecl("x", ast.Id("Float"), is_param=True, comment=";; x coordinate"),
                ast.VarDecl("y", ast.Id("Float"), value=ast.Const(0), is_param=True, comment=";; y coordinate"),
                ast.VarDecl("z", ast.Id("Float"), value=ast.Const(0), is_param=True,
                            comment=";; z\n            ;; coordinate")
            ])
        ],
    ],
])
def test_parse_comments(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast

@pytest.mark.parametrize("code, exp_ast", [
    [
        """def test() {
            a := 1.5;
            b := 0xCAFE;
            c := 0xCafeUS;
            d := 0644;
            e := 0Coffee(36);
            f := 0ILikeTea(36)ul;
            g := 0Cafe(16)s;
            h := 0d;
        }
        """,
        [
            ast.FuncDef(
                ast.Id("test"),
                body=[
                    ast.VarDecl("a", value=ast.Const(1.5, type="Float", value_str="1.5f")),
                    ast.VarDecl("b", value=ast.Const(0xCAFE, type="Int", value_str="0xCAFE")),
                    ast.VarDecl("c", value=ast.Const(0xCAFE, type="Ushort", value_str="0xCafe")),
                    ast.VarDecl("d", value=ast.Const(420, type="Int", value_str="0644")),
                    ast.VarDecl("e", value=ast.Const(766624694, type="Int", value_str="766624694")),
                    ast.VarDecl("f", value=ast.Const(1457390057554, type="Ulong", value_str="1457390057554ull")),
                    ast.VarDecl("g", value=ast.Const(0xCAFE, type="Short", value_str="0xCafe")),
                    ast.VarDecl("h", value=ast.Const(0, type="Double", value_str="0")),
                ]
            )
        ]
    ],
])
def test_parse_num_literals(code, exp_ast):
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
        import xylib;

        def main() -> int {
        }
        """,
        [
            ast.Import(lib="xylib"),
            ast.FuncDef(
                ast.Id("main"),
                returns=[ast.VarDecl(type=ast.Id("int"))],
            ),
        ]
    ],
    [
        """# multi word comment
        import xylib;

        def main~EntryPoint() -> int {
            return 0;
        }
        """,
        [
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
        >> a > b
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
    [
        """
        def add3(
            a: int,
            b: int,
            c: int,
        ) -> int {
            return a + b + c;
        }
        """,
        [
            ast.FuncDef(
                ast.Id("add3"),
                params=[
                    ast.param("a", type=ast.Id("int")),
                    ast.param("b", type=ast.Id("int")),
                    ast.param("c", type=ast.Id("int")),
                ],
                returns=[ast.VarDecl(type=ast.Id("int"))],
                body=[
                    ast.Return(
                        ast.BinExpr(
                            ast.BinExpr(ast.Id("a"), ast.Id("b"), op="+"),
                            ast.Id("c"),
                            op="+"
                        )
                    )
                ]
            )
        ]
    ],
    [
        """
        def add3(
            a: int,
            # comment before last param
            b: int,
        ) -> void {}
        """,
        [
            ast.FuncDef(
                ast.Id("add3"),
                params=[
                    ast.param("a", type=ast.Id("int")),
                    ast.param("b", type=ast.Id("int")),
                ],
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[]
            )
        ]
    ],
    [
        """
        def add3(
            a: int,
            b: int,
            # comment after last param
        ) -> void {}
        """,
        [
            ast.FuncDef(
                ast.Id("add3"),
                params=[
                    ast.param("a", type=ast.Id("int")),
                    ast.param("b", type=ast.Id("int")),
                ],
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[]
            )
        ]
    ],
    [
        """
        def add3(
            a: int,
            b: int # comment at the same line as the last param
        ) -> void {}
        """,
        [
            ast.FuncDef(
                ast.Id("add3"),
                params=[
                    ast.param("a", type=ast.Id("int")),
                    ast.param("b", type=ast.Id("int")),
                ],
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[]
            )
        ]
    ],
])
def test_parse_simple_func(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast

@pytest.mark.parametrize("code, exp_ast", [
    [
        """def test() -> void {
            [a];
            'func(a);
            ''func;  # valid syntax, invalid code
            'f1'f2(a);
            ['func];
            'func[i];
            'f1 + 'f2;
        }
        """,
        [
            ast.FuncDef(ast.Id("test"), params=[],
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[
                    ast.Select(
                        base=None,
                        args=ast.Args(
                            args=[
                                ast.Id("a"),
                            ]
                        )
                    ),
                    ast.FuncCall(
                        name=ast.Id("func"), args=[ast.Id("a")], inject_context=True,
                    ),
                    ast.FuncCall(
                        name=ast.FuncCall(name=ast.Id("func"), inject_context=True),
                        inject_context=True,
                    ),
                    ast.FuncCall(
                        name=ast.Id("f2"),
                        args=[
                            ast.FuncCall(name=ast.Id("f1"), inject_context=True),
                            ast.Id("a")
                        ],
                    ),
                    ast.Select(
                        base=None,
                        args=ast.Args(
                            args=[
                                ast.FuncCall(name=ast.Id("func"), inject_context=True),
                            ]
                        )
                    ),
                    ast.Select(
                        base=ast.FuncCall(
                            name=ast.Id("func"), args=[], inject_context=True,
                        ),
                        args=ast.Args(
                            args=[ast.Id("i")],
                        )
                    ),
                    ast.BinExpr(
                        arg1=ast.FuncCall(
                            name=ast.Id("f1"), args=[], inject_context=True,
                        ),
                        arg2=ast.FuncCall(
                            name=ast.Id("f2"), args=[], inject_context=True,
                        ),
                        op="+",
                    )
                ]
            ),
        ]
    ],
])
def test_parse_implied_context_expr(code, exp_ast):
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
                    ast.VarDecl(name="a", type=ast.Id("int"), mutable=True),
                    ast.VarDecl(name="b", type=ast.Id("int"), mutable=True),
                ],
                body=[
                    ast.Return(value=[ast.Const(0), ast.Const(1)])
                ]
            ),
        ]
    ],
    [
        """
        def double(x: int) x * 2;
        def sqr(x: int) = x * x;
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
        def pseudoParam(x: pseudo int) 0;
        def unnamedParam(:int) 0;
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
    [
        """
        def func(x: int)
            x + 1;
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[
                    ast.param("x", type=ast.Id("int")),
                ],
                body=ast.BinExpr(ast.Id("x"), ast.Const(1), op="+")
            ),
        ]
    ],
    [
        """
        def func(x: int)
        # comment
        # >> comment
        # << comment
        {
        }
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[
                    ast.param("x", type=ast.Id("int")),
                ],
                returns=[
                ],
                body=[
                ]
            ),
        ]
    ],
    [
        """
        def func(x: int) -> Ptr~int {}
        def func(x: pseudo Any) -> Ptr~[^(a'typeof)] {}
        def func(x: pseudo Any) -> Ptr~[^a'typeof] {}
        def func(x: pseudo Any) -> Ptr~[^typeof(a)] {}
        def func(x: pseudo Any) -> Ptr~[^(%a)] {}
        def func(x: pseudo Any) -> Ptr~[%^a] {}
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[ast.param("x", type=ast.Id("int"))],
                returns=[
                    ast.VarDecl(type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                        args=[ast.Id("int")]
                    ))),
                ],
                body=[]
            ),
            ast.FuncDef(ast.Id("func"),
                params=[ast.param("x", type=ast.Id("Any"), is_pseudo=True)],
                returns=[
                    ast.VarDecl(type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                        args=[
                            ast.CallerContextExpr(
                                ast.FuncCall(ast.Id("typeof"), args=[ast.Id("a")]),
                            )
                        ]
                    ))),
                ],
                body=[]
            ),
            ast.FuncDef(ast.Id("func"),
                params=[ast.param("x", type=ast.Id("Any"), is_pseudo=True)],
                returns=[
                    ast.VarDecl(type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                        args=[
                            ast.FuncCall(ast.Id("typeof"), args=[
                                ast.CallerContextExpr(ast.Id("a"))
                            ]),
                        ]
                    ))),
                ],
                body=[]
            ),
            ast.FuncDef(ast.Id("func"),
                params=[ast.param("x", type=ast.Id("Any"), is_pseudo=True)],
                returns=[
                    ast.VarDecl(type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                        args=[
                            ast.FuncCall(
                                ast.CallerContextExpr(ast.Id("typeof")),
                                args=[ast.Id("a")]
                            ),
                        ]
                    ))),
                ],
                body=[]
            ),
            ast.FuncDef(ast.Id("func"),
                params=[ast.param("x", type=ast.Id("Any"), is_pseudo=True)],
                returns=[
                    ast.VarDecl(type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                        args=[
                            ast.CallerContextExpr(
                                arg=ast.UnaryExpr(arg=ast.Id("a"), op="%"),
                            )
                        ]
                    ))),
                ],
                body=[]
            ),
            ast.FuncDef(ast.Id("func"),
                params=[ast.param("x", type=ast.Id("Any"), is_pseudo=True)],
                returns=[
                    ast.VarDecl(type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                        args=[
                            ast.UnaryExpr(
                                arg=ast.CallerContextExpr(arg=ast.Id("a")),
                                 op="%",
                            )
                        ]
                    ))),
                ],
                body=[]
            ),
        ]
    ],
    [
        """
        def func(num: (Int, Float, Byte)) {}
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[ast.param(
                    "num",
                    type=ast.Enumeration([
                        ast.Id("Int"), ast.Id("Float"), ast.Id("Byte")
                    ]),
                )],
                returns=[],
                body=[]
            )
        ]
    ],
])
def test_parse_advanced_funcs(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def func(input: Int) -> Int || Error {
              if (input < 0) return 0;
              return 100;
           }
        """,
        [
            ast.FuncDef(ast.Id("func"), params=[ast.VarDecl("input", ast.Id("Int"), is_param=True)],
                returns=[
                    ast.VarDecl(type=ast.Id("Int")),
                ],
                etype=ast.Id("Error"),
                body=[
                    ast.IfExpr(
                        ast.BinExpr(ast.Id("input"), ast.Const(0), op="<"),
                        block=ast.Block(
                            body=[ast.Return(ast.Const(0))]
                        )
                    ),
                    ast.Return(ast.Const(100)),
                ]
            ),
        ]
    ],
    [
        """def func(input: Int) -> Int || Error {
              if (input < 0) error Error{-1};
              return 100;
           }
        """,
        [
            ast.FuncDef(ast.Id("func"), params=[ast.VarDecl("input", ast.Id("Int"), is_param=True)],
                returns=[
                    ast.VarDecl(type=ast.Id("Int")),
                ],
                etype=ast.Id("Error"),
                body=[
                    ast.IfExpr(
                        ast.BinExpr(ast.Id("input"), ast.Const(0), op="<"),
                        block=ast.Block(
                            body=[ast.Error(
                                ast.StructLiteral(ast.Id("Error"), args=[ast.Const(-1)])
                            )]
                        )
                    ),
                    ast.Return(ast.Const(100)),
                ]
            ),
        ]
    ],
])
def test_early_returns_and_errors(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast

@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        def func(x: pseudo Any, y : Metadata = ^metadata(x)) {}
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[
                    ast.param("x", type=ast.Id("Any"), is_pseudo=True),
                    ast.param("y", type=ast.Id("Metadata"), value=ast.FuncCall(
                        ast.CallerContextExpr(ast.Id("metadata")),
                        args=[ast.Id("x")],
                    ))
                ],
                returns=[], body=[]
            ),
        ]
    ],
    [
        """
        def func(x: Array, y:Tag = ^x..elem) {}
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[
                    ast.param("x", type=ast.Id("Array")),
                    ast.param("y", type=ast.Id("Tag"), value=ast.BinExpr(
                        arg1=ast.CallerContextExpr(ast.Id("x")),
                        arg2=ast.Id("elem"),
                        op=".."
                    ))
                ],
                returns=[], body=[]
            ),
        ]
    ],
    [
        """
        def log(^msg: Str, _ := if (loggingEnalbed) doLog(msg)) {}
        """,
        [
            ast.FuncDef(ast.Id("log"),
                params=[
                    ast.param("msg", type=ast.Id("Str"), is_callerContext=True, is_pseudo=True),
                    ast.param("_", value=ast.IfExpr(
                        cond=ast.Id("loggingEnalbed"),
                        block=ast.Block(body=ast.FuncCall(
                            ast.Id("doLog"),
                            args=[ast.Id("msg")]
                        ))
                    ))
                ],
                returns=[], body=[]
            ),
        ]
    ],
    [
        """
        def test(^msg: pseudo Any) {}
        """,
        [
            ast.FuncDef(ast.Id("test"),
                params=[
                    ast.param("msg", type=ast.Id("Any"), is_callerContext=True, is_pseudo=True),
                ],
                returns=[], body=[]
            ),
        ]
    ],
    [
        """
        def func(x: pseudo Any, val: int = ^(x+1)) {}
        """,
        [
            ast.FuncDef(ast.Id("func"),
                params=[
                    ast.param("x", type=ast.Id("Any"), is_pseudo=True),
                    ast.param("val", type=ast.Id("int"), value=ast.CallerContextExpr(
                        arg=ast.BinExpr(
                            ast.Id("x"),
                            ast.Const(1),
                            op="+"
                        )
                    ))
                ],
                returns=[], body=[]
            ),
        ]
    ],
])
def test_parse_boundary_expressions(code, exp_ast):
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
                        "a", type=ast.Id("int"), is_param=True,
                    ),
                    ast.VarDecl(
                        "b", type=ast.Id("int"), value=ast.Const(0),
                        is_param=True,
                    ),
                    ast.VarDecl(
                        "c", value=ast.BinExpr(ast.Id("a"), ast.Id("b"), op="+"),
                        is_param=True,
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
    [
        """def main() -> void {
            func(
                func1(
                    func11(),
                    func12()
                ),
                func2()
            );
            c'func(
                a,
                b,
            );
        }
        """,
        [
            ast.FuncDef(
                ast.Id("main"),
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[
                    ast.FuncCall(ast.Id("func"), args=[
                        ast.FuncCall(ast.Id("func1"), args=[
                            ast.FuncCall(ast.Id("func11")),
                            ast.FuncCall(ast.Id("func12")),
                        ]),
                        ast.FuncCall(ast.Id("func2")),
                    ]),
                    ast.FuncCall(ast.Id("func"), args=[
                        ast.Id("c"), ast.Id("a"), ast.Id("b"),
                    ])
            ]),
        ]
    ],
    [
        """def main() -> void {
            func(...);
            a'func(...);
            func(a, b=c, ...);
            func(b=a, ...);
        }
        """,
        [
            ast.FuncDef(
                ast.Id("main"),
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[
                    ast.FuncCall(ast.Id("func"),
                                 inject_args=ast.ScopeArgsInject()),
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a")],
                                 inject_args=ast.ScopeArgsInject()),
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a")],
                                 kwargs={"b": ast.Id("c")},
                                 inject_args=ast.ScopeArgsInject()),
                    ast.FuncCall(ast.Id("func"), kwargs={"b": ast.Id("a")},
                                 inject_args=ast.ScopeArgsInject()),
            ]),
        ]
    ],
    [
        """def main() -> void {
            (a);
            (func) a, b;
            (func) a, b=10;
            (func) (func) x, y;
            (func) x, (func) y;
            (func) x + (func) y;
        }
        """,
        [
            ast.FuncDef(
                ast.Id("main"),
                returns=[ast.VarDecl(type=ast.Id("void"))],
                body=[
                    ast.Id("a"),
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a"), ast.Id("b")]),
                    ast.FuncCall(ast.Id("func"), args=[ast.Id("a")],
                                 kwargs={"b": ast.Const(10)}),
                    ast.FuncCall(ast.Id("func"), args=[
                        ast.FuncCall(ast.Id("func"), args=[ast.Id("x"), ast.Id("y")])
                    ]),
                    ast.FuncCall(ast.Id("func"), args=[
                        ast.Id("x"),
                        ast.FuncCall(ast.Id("func"), args=[ast.Id("y")])
                    ]),
                    ast.FuncCall(
                        ast.Id("func"),
                        args=[
                            ast.BinExpr(
                                ast.Id("x"),
                                ast.FuncCall(ast.Id("func"), args=[ast.Id("y")]),
                                op="+",
                            )
                        ]
                    )
                ]
            ),
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
            d : mut = 10;
            pi := 3.14f;
            ptr: Ptr~int;
            pp: Ptr~Ptr~int = ptr'addr;
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("b", type=None, value=ast.Const(0)),
                ast.VarDecl("c", type=ast.Id("int"), value=ast.Const(5)),
                ast.VarDecl("cv", type=ast.Id("int"), mutable=True),
                ast.VarDecl(
                    "a", type=None,
                    value=ast.BinExpr(
                        ast.BinExpr(ast.Id("b"), ast.Const(5), "+"),
                        ast.Id("c"),
                        "-"
                    )
                ),
                ast.VarDecl("d", type=None, value=ast.Const(10), mutable=True),
                ast.VarDecl("pi", type=None, value=ast.Const(3.14, "3.14f", "Float")),
                ast.VarDecl(
                    "ptr",
                    type=ast.AttachTags(
                        ast.Id("Ptr"), tags=ast.TagList([ast.Id("int")])
                    ),
                    value=None, mutable=True
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
            d := a +: b;
            e := a *: c;
            f := a -: b : -1;
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("d", value=ast.SliceExpr(
                    start=ast.Id("a"),
                    end=ast.Id("b"),
                    op="+",
                )),
                ast.VarDecl("e", value=ast.SliceExpr(
                    start=ast.Id("a"),
                    end=ast.Id("c"),
                    op="*",
                )),
                ast.VarDecl("f", value=ast.SliceExpr(
                    start=ast.Id("a"),
                    end=ast.Id("b"),
                    op="-",
                    step=ast.Const(-1)
                )),
            ]),
        ]
    ],
])
def test_parse_operator_slices(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast

@pytest.mark.parametrize("code, exp_ast", [
    [
        """def test() {
            a : mut = 10;
            b : int;
            b =< a;
            c :=< b;
        }
        """,
        [
            ast.FuncDef(ast.Id("test"), body=[
                ast.VarDecl("a", mutable=True, value=ast.Const(10)),
                ast.VarDecl("b", mutable=True, type=ast.Id("int")),
                ast.BinExpr(
                    arg1=ast.Id("b"), arg2=ast.Id("a"), op="=<",
                ),
                ast.VarDecl(name="c", value=ast.Id("b"), is_move=True)
            ]),
        ]
    ],
    [
        """def test() {
            a : mut = 10;
            b : int;
            b =< a;
            c :=< b;
            f(a =>, b);
            a[i] =< b[j];
        }
        """,
        [
            ast.FuncDef(ast.Id("test"), body=[
                ast.VarDecl("a", mutable=True, value=ast.Const(10)),
                ast.VarDecl("b", mutable=True, type=ast.Id("int")),
                ast.BinExpr(
                    arg1=ast.Id("b"), arg2=ast.Id("a"), op="=<",
                ),
                ast.VarDecl(name="c", value=ast.Id("b"), is_move=True),
                ast.FuncCall(
                    name=ast.Id("f"),
                    args=[
                        ast.UnaryExpr(ast.Id("a"), op="=>"),
                        ast.Id("b"),
                    ]
                ),
                ast.BinExpr(
                    arg1=ast.Select(
                        base=ast.Id("a"),
                        args=ast.Args(args=[ast.Id("i")])
                    ),
                    arg2=ast.Select(
                        base=ast.Id("b"),
                        args=ast.Args(args=[ast.Id("j")])
                    ),
                    op="=<"
                )
            ]),
        ]
    ],
    [
        """def test() {
            a : mut = 10;
            f(a =>);
            f(a, a =>);
        }
        """,
        [
            ast.FuncDef(ast.Id("test"), body=[
                ast.VarDecl("a", mutable=True, value=ast.Const(10)),
                ast.FuncCall(
                    name=ast.Id("f"),
                    args=[
                        ast.UnaryExpr(ast.Id("a"), op="=>"),
                    ]
                ),
                ast.FuncCall(
                    name=ast.Id("f"),
                    args=[
                        ast.Id("a"),
                        ast.UnaryExpr(ast.Id("a"), op="=>"),
                    ]
                ),
            ]),
        ]
    ],
])
def test_move_operators(code, exp_ast):
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
            doubleNeg := !!b;
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
                                op='!', arg=ast.Const(True, "true", "Bool")
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
                ast.VarDecl("doubleNeg", value=ast.UnaryExpr(
                    arg=ast.UnaryExpr(
                        arg=ast.Id("b"), op="!"
                    ),
                    op ="!",
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
            a : mut = 1;
            b := a++;
            a++;
            c := b--;
            d := a++ + b;
            f := d---b;
        }""",
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", value=ast.Const(1), mutable=True),
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
    ],
    [
        """def func() -> void {
            a := 0;
            b := &a;
            c := &func(a, b);
            d := func1(&func2(&a + 5, &b));
            e := &a[10][20];
        }""",
        [
            ast.FuncDef(ast.Id("func"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", value=ast.Const(0), mutable=False),
                ast.VarDecl("b", value=ast.UnaryExpr(
                    arg=ast.Id("a"),
                    op="&",
                )),
                ast.VarDecl("c", value=ast.UnaryExpr(
                    arg=ast.FuncCall(
                        ast.Id("func"),
                        args=[ast.Id("a"), ast.Id("b")]
                    ),
                    op="&",
                )),
                ast.VarDecl("d", value=ast.FuncCall(
                    ast.Id("func1"),
                    args=[
                        ast.UnaryExpr(
                            arg=ast.FuncCall(
                                ast.Id("func2"),
                                args=[
                                    ast.BinExpr(
                                        ast.UnaryExpr(ast.Id("a"), op="&"),
                                        ast.Const(5),
                                        op='+'
                                    ),
                                    ast.UnaryExpr(ast.Id("b"), op="&")
                                ]
                            ),
                            op='&'
                        )
                    ]
                )),
                ast.VarDecl("e", value=ast.UnaryExpr(
                    arg=ast.Select(
                        base=ast.Select(
                            base=ast.Id("a"),
                            args=ast.Args(
                                args=[ast.Const(10)]
                            )
                        ),
                        args=ast.Args([ast.Const(20)])
                    ),
                    op="&",
                )),
            ])
        ]
    ],
    [
        """def func() -> void {
            a : Ptr~Ptr~int;
            b : a..to;
            c : a..to..to;
            d : (%a)..to;
            e : %a..to;
            f : %c = a..to'sizeof;
        }""",
        [
            ast.FuncDef(ast.Id("func"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", mutable=True, type=ast.AttachTags(
                    arg=ast.Id("Ptr"),
                    tags=ast.TagList(args=[ast.AttachTags(
                        arg=ast.Id("Ptr"),
                        tags=ast.TagList(args=[ast.Id("int")])
                    )])
                )),
                ast.VarDecl("b", mutable=True, type=ast.BinExpr(
                    ast.Id("a"),
                    ast.Id("to"),
                    op="..",
                )),
                ast.VarDecl("c", mutable=True, type=ast.BinExpr(
                    ast.BinExpr(
                        ast.Id("a"),
                        ast.Id("to"),
                        op="..",
                    ),
                    ast.Id("to"),
                    op="..",
                )),
                ast.VarDecl("d", mutable=True, type=ast.BinExpr(
                    ast.UnaryExpr(
                        ast.Id("a"),
                        op="%",
                    ),
                    ast.Id("to"),
                    op="..",
                )),
                ast.VarDecl("e", mutable=True, type=ast.UnaryExpr(
                    ast.BinExpr(
                        ast.Id("a"),
                        ast.Id("to"),
                        op="..",
                    ),
                    op="%"
                )),
                ast.VarDecl("f", mutable=False, type=ast.UnaryExpr(
                    ast.Id("c"),
                    op="%"
                ), value=ast.FuncCall(
                    name=ast.Id("sizeof"), args=[
                        ast.BinExpr(
                            ast.Id("a"), ast.Id("to"), op=".."
                        )
                    ]
                )),
            ])
        ]
    ],
    [
        """def func() -> void {
            a := 5;
            b := -a;
            c := if(a < 0) -a else a;
        }""",
        [
            ast.FuncDef(ast.Id("func"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", mutable=False, value=ast.Const(5)),
                ast.VarDecl("b", mutable=False, value=ast.UnaryExpr(ast.Id("a"), op="-")),
                ast.VarDecl("c", value=ast.IfExpr(
                    cond=ast.BinExpr(ast.Id("a"), ast.Const(0), op="<"),
                    block=ast.Block(body=ast.UnaryExpr(ast.Id("a"), op="-")),
                    else_node=ast.Block(body=ast.Id("a")),
                ))
            ]),
        ]
    ],
    [
        """def func() -> void {
            a := func()~Tag;
            b := func()~Tag1~Tag2;
        }""",
        [
            ast.FuncDef(ast.Id("func"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("a", mutable=False, value=ast.AttachTags(
                    arg=ast.FuncCall(ast.Id("func")),
                    tags=ast.TagList(
                        args=[ast.Id("Tag")]
                    )
                )),
                ast.VarDecl("b", mutable=False, value=ast.AttachTags(
                    arg=ast.FuncCall(ast.Id("func")),
                    tags=ast.TagList(
                        args=[
                            ast.AttachTags(
                                arg=ast.Id("Tag1"),
                                tags=ast.TagList(
                                    args=[ast.Id("Tag2")]
                                )
                            )
                        ]
                    )
                )),
            ]),
        ]
    ],
    [
        """def test(a: Any) func(%a{0});""",
        [
            ast.FuncDef(ast.Id("test"), body=ast.FuncCall(
                name=ast.Id("func"), args=[
                    ast.UnaryExpr(
                        ast.StructLiteral(
                            name=ast.Id("a"),
                            args=[ast.Const(0)]
                        ),
                        op="%"
                    )
                ]
            ), params=[
                ast.VarDecl("a", type=ast.Id("Any"), is_param=True)
            ]),
        ]
    ],
])
def test_expressions(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def func() {
            return % ! - - + ^ ' a;
        }""",
        [
            ast.FuncDef(ast.Id("func"), body=[
                ast.Return(ast.UnaryExpr(
                    op="%",
                    arg=ast.UnaryExpr(
                        op="!",
                        arg=ast.UnaryExpr(
                            op="-",
                            arg=ast.UnaryExpr(
                                op="-",
                                arg=ast.UnaryExpr(
                                    op="+",
                                    arg=ast.CallerContextExpr(
                                        arg=ast.FuncCall(
                                            name=ast.Id("a"),
                                            inject_context=True
                                        )
                                    )
                                )
                            )
                        )
                    )
                ))
            ]),
        ],
    ],
    [
        """def func() {
            return - - a --;
        }""",
        [
            ast.FuncDef(ast.Id("func"), body=[
                ast.Return(ast.UnaryExpr(
                    op="-",
                    arg=ast.UnaryExpr(
                        op="-",
                        arg=ast.UnaryExpr(
                            op="--",
                            arg=ast.Id("a")
                        )
                    ),
                ))
            ]),
        ],
    ],
])
def test_weird_expressions(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """def test() -> void {
            cb1: (:int)->int;
            cb2: (a:int, b:int)->void||Error;
            cb3: (:mut int)->void;
            cb4: Ptr~[()->Str||Error];
        }
        """,
        [
            ast.FuncDef(ast.Id("test"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("cb1", mutable=True, type=ast.FuncType(
                    params=[
                        ast.VarDecl(type=ast.Id("int"), is_param=True),
                    ],
                    returns=[
                        ast.VarDecl(type=ast.Id("int")),
                    ]
                )),
                ast.VarDecl("cb2", mutable=True, type=ast.FuncType(
                    params=[
                        ast.VarDecl(name="a", type=ast.Id("int"), is_param=True),
                        ast.VarDecl(name="b", type=ast.Id("int"), is_param=True),
                    ],
                    returns=[
                        ast.VarDecl(type=ast.Id("void")),
                    ],
                    etype=ast.Id("Error"),
                )),
                ast.VarDecl("cb3", mutable=True, type=ast.FuncType(
                    params=[
                        ast.VarDecl(type=ast.Id("int"), mutable=True),
                    ],
                    returns=[
                        ast.VarDecl(type=ast.Id("void")),
                    ],
                )),
                ast.VarDecl("cb4", mutable=True, type=ast.AttachTags(
                    arg=ast.Id("Ptr"),
                    tags=ast.TagList(args=[
                        ast.FuncType(
                            params=[
                            ],
                            returns=[
                                ast.VarDecl(type=ast.Id("Str")),
                            ],
                            etype=ast.Id("Error")
                        ),
                    ])
                )),
            ]),
        ]
    ],
    [
        """def test() -> void {
            cb1 := $(int, int);
            cb2 := $ name(int, long);
            cb3 := $* ~Test();
            cb4 := $ name~Tag();
            sum := ($ add(int, int))(1, 2);
        }
        """,
        [
            ast.FuncDef(ast.Id("test"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("cb1", value=ast.FuncSelect(
                    name=None,
                    args=[
                        ast.Id("int"),
                        ast.Id("int"),
                    ],
                )),
                ast.VarDecl("cb2", value=ast.FuncSelect(
                    name=ast.Id("name"),
                    args=[
                        ast.Id("int"),
                        ast.Id("long"),
                    ]
                )),
                ast.VarDecl("cb3", value=ast.FuncSelect(
                    name=None,
                    tags=ast.TagList(
                        args=[
                            ast.Id("Test"),
                        ],
                    ),
                    args=[],
                    multiple=True,
                )),
                ast.VarDecl("cb4", value=ast.FuncSelect(
                    name=ast.Id("name"),
                    tags=ast.TagList(
                        args=[
                            ast.Id("Tag"),
                        ],
                    ),
                    args=[],
                )),
                ast.VarDecl("sum", value=ast.FuncCall(
                    name=ast.FuncSelect(
                        name=ast.Id("add"),
                        args=[
                            ast.Id("int"),
                            ast.Id("int"),
                        ],
                    ),
                    args=[ast.Const(1), ast.Const(2)]
                )),
            ]),
        ]
    ],
])
def test_parse_callbacks(code, exp_ast):
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
                ast.VarDecl("ptr", type=ast.Id("Ptr"), mutable=False),
                ast.VarDecl("len", type=ast.Id("Size"), mutable=False),
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
                ast.VarDecl("name", type=ast.Id("Str"), mutable=False),
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
            ), comment=";; Units of count i.e. 1, 2, 3 of something"),
        ]
    ],
    [
        """struct Point2d{
            x: float;; x coordinate
            y: float;; y coordinate
        }
        """,
        [
            ast.StructDef(name="Point2d", fields=[
                ast.VarDecl("x", type=ast.Id("float"), mutable=False, comment=';; x coordinate',),
                ast.VarDecl("y", type=ast.Id("float"), mutable=False, comment=';; y coordinate',),
            ]),
        ]
    ],
    [
        """
        ;; Point2d comment
        struct Point2d{
            ;; x coordinate
            x: float;
            ;; y coordinate
            y: float;
        }
        """,
        [
            ast.StructDef(
                name="Point2d",
                fields=[
                    ast.VarDecl("x", type=ast.Id("float"), mutable=False, comment=';; x coordinate',),
                    ast.VarDecl("y", type=ast.Id("float"), mutable=False, comment=';; y coordinate',),
                ],
                comment=";; Point2d comment"
            ),
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
                    "c", mutable=True, type=ast.AttachTags(
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
    [
        """
        def func() -> void {
            a .= {1};
        }
        """,
        [
            ast.FuncDef(ast.Id("func"), returns=ast.SimpleRType("void"), body=[
                ast.BinExpr(
                    ast.Id("a"),
                    ast.StructLiteral(name=None, args=[ast.Const(1)]),
                    op=".=",
                ),
            ]),
        ],
    ],
    [
        """
        def func() -> void {
            argStr := Str{
                addr=argv[i],
                len=strlen(argv[i]),
            };
        }
        """,
        [
            ast.FuncDef(ast.Id("func"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl(
                    name="argStr",
                    value=ast.StructLiteral(
                        name=ast.Id("Str"),
                        kwargs={
                            "addr": ast.Select(ast.Id("argv"), ast.Args([ast.Id("i")])),
                            "len": ast.FuncCall(
                                ast.Id("strlen"),
                                args=[
                                    ast.Select(ast.Id("argv"), ast.Args([ast.Id("i")]))
                                ],
                            ),
                        }
                    ),
                )
            ]),
        ],
    ],
    [
        """
        def stringCtor(addr: Ptr, len: Size) Str{=addr, =len};
        """,
        [
            ast.FuncDef(
                ast.Id("stringCtor"),
                params=[
                    ast.VarDecl("addr", ast.Id("Ptr"), is_param=True),
                    ast.VarDecl("len", ast.Id("Size"), is_param=True),
                ],
                body=ast.StructLiteral(
                    ast.Id("Str"),
                    kwargs={
                        "addr": ast.Id("addr"),
                        "len": ast.Id("len"),
                    }
                )
            ),
        ],
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

@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        -def func() -> void {}
        +def func() -> void {}
        *def func() -> void {}
        """,
        [
            ast.FuncDef(
                ast.Id("func"), returns=ast.SimpleRType("void"), body=[],
                visibility=ast.ModuleVisibility,
            ),
            ast.FuncDef(
                ast.Id("func"), returns=ast.SimpleRType("void"), body=[],
                visibility=ast.PackageVisibility,
            ),
            ast.FuncDef(
                ast.Id("func"), returns=ast.SimpleRType("void"), body=[],
                visibility=ast.PublicVisibility,
            ),
        ]
    ],
    [
        """
        -struct Struct {}
        +struct Struct {}
        *struct Struct {}
        """,
        [
            ast.StructDef(
                "Struct", visibility=ast.ModuleVisibility,
            ),
            ast.StructDef(
                "Struct", visibility=ast.PackageVisibility,
            ),
            ast.StructDef(
                "Struct", visibility=ast.PublicVisibility,
            ),
        ]
    ],
])
def test_visibility(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast


@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        struct Array {
        }

        def func(arr: Array) -> arr[ int ] {
            return 0;
        }

        def func(arr: Array) -> (arr[int]) {
            return 0;
        }

        def func(arr: Array, idx: int) -> arr[ Ptr~int ] {
        }

        def func(idx: int) -> [Ptr~int] {
        }
        """,
        [
            ast.StructDef("Array"),
            ast.FuncDef(
                ast.Id("func"),
                returns=[
                    ast.VarDecl(type=ast.Id("int"), index_in=ast.Id("arr"), mutable=True),
                ],
                params=[
                    ast.VarDecl("arr", type=ast.Id("Array"), is_param=True, mutable=False)
                ],
                body=[
                    ast.Return(ast.Const(0)),
                ],
            ),
            ast.FuncDef(
                ast.Id("func"),
                returns=[
                    ast.VarDecl(type=ast.Id("int"), index_in=ast.Id("arr"), mutable=True),
                ],
                params=[
                    ast.VarDecl("arr", type=ast.Id("Array"), is_param=True, mutable=False)
                ],
                body=[
                    ast.Return(ast.Const(0)),
                ],
            ),
            ast.FuncDef(
                ast.Id("func"),
                params=[
                    ast.VarDecl("arr", type=ast.Id("Array"), is_param=True, mutable=False),
                    ast.VarDecl("idx", type=ast.Id("int"), is_param=True, mutable=False),
                ],
                returns=[
                    ast.VarDecl(
                        type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                            args=[ast.Id("int")],
                        )),
                        index_in=ast.Id("arr"),
                        mutable=True
                    ),
                ],
                body=[],
            ),
            ast.FuncDef(
                ast.Id("func"),
                params=[
                    ast.VarDecl("idx", type=ast.Id("int"), is_param=True, mutable=False),
                ],
                returns=[
                    ast.VarDecl(
                        type=ast.AttachTags(ast.Id("Ptr"), tags=ast.TagList(
                            args=[ast.Id("int")],
                        )),
                        index_in=ast.nobase,
                        mutable=True
                    ),
                ],
                body=[],
            ),
        ]
    ],
])
def test_returning_indices(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast

@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        def test() {
            a := [b];
            [a] = 10;
            [[a]];
            [b + [a]];
        }
        """,
        [
            ast.FuncDef(
                ast.Id("test"),
                returns=[],
                params=[],
                body=[
                    ast.VarDecl(
                        "a",
                        value=ast.Select(
                            base=None,
                            args=ast.Args(args=[
                                ast.Id("b"),
                            ])
                        )
                    ),
                    ast.BinExpr(
                        arg1=ast.Select(base=None, args=ast.Args([ast.Id("a")])),
                        arg2=ast.Const(10),
                        op='=',
                    ),
                    ast.Select(base=None, args=ast.Args([
                        ast.Select(base=None, args=ast.Args([ast.Id("a")]))
                    ])),
                    ast.Select(base=None, args=ast.Args([
                        ast.BinExpr(
                            arg1=ast.Id("b"),
                            arg2=ast.Select(base=None, args=ast.Args([ast.Id("a")])),
                            op="+"
                        )
                    ]))
                ],
            ),
        ]
    ],
    [
        """
        def test() {
            [b, 5, [c]] = 10;
            [b + [a]] = [[[d]] + c];
            [callback]();
            a[i][j];
            [a][i][j];
        }
        """,
        [
            ast.FuncDef(
                ast.Id("test"),
                returns=[],
                params=[],
                body=[
                    ast.BinExpr(
                        arg1=ast.Select(base=None, args=ast.Args([
                            ast.Id("b"),
                            ast.Const(5),
                            ast.Select(base=None, args=ast.Args([ast.Id("c")]))
                        ])),
                        arg2=ast.Const(10),
                        op='='
                    ),
                    ast.BinExpr(
                        arg1=ast.Select(base=None, args=ast.Args([
                            ast.BinExpr(
                                arg1=ast.Id("b"),
                                arg2=ast.Select(base=None, args=ast.Args([ast.Id("a")])),
                                op="+"
                            )
                        ])),
                        arg2=ast.Select(base=None, args=ast.Args([
                            ast.BinExpr(
                                arg1=ast.Select(base=None, args=ast.Args([
                                    ast.Select(base=None, args=ast.Args([ast.Id("d")]))
                                ])),
                                arg2=ast.Id("c"),
                                op="+",
                            )
                        ])),
                        op='=',
                    ),
                    ast.FuncCall(
                        name=ast.Select(base=None, args=ast.Args([ast.Id("callback")]))
                    ),
                    ast.Select(
                        base=ast.Select(base=ast.Id('a'), args=ast.Args([ast.Id("i")])),
                        args=ast.Args([ast.Id("j")])
                    ),
                    ast.Select(
                        base=ast.Select(
                            base=ast.Select(base=None, args=ast.Args([ast.Id("a")])),
                            args=ast.Args([ast.Id("i")]),
                        ),
                        args=ast.Args([ast.Id("j")])
                    )
                ],
            ),
        ]
    ],
])
def test_indexing_syntax(code, exp_ast):
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
            j := f"{=a+b}";
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("f", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Const("before"),
                        ast.Args(
                            [ast.BinExpr(ast.Id("a"), ast.Id("b"), "+")]
                        ),
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
                        ast.Args([ast.Id("a")]),
                        ast.Args([ast.Id("b")]),
                        ast.Const(" "),
                        ast.Args([ast.Id("c")]),
                        ast.Const("\n"),
                        ast.Args([ast.Id("d")]),
                        ast.Const(" "),
                    ],
                    full_str="{a}{b} {c}\n{d} "
                )),
                ast.VarDecl("j", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Args(
                            [ast.BinExpr(ast.Id("a"), ast.Id("b"), op="+")],
                            is_introspective=True
                        ),
                    ],
                    full_str="{=a+b}"
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
    [
        """def main() -> void {
            s1 := "    ";
            s2 := "abc    ";
            s3 := "   abc   ";
            s4 := "    abc";
            s5 := f"   {abc}";
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("s1", type=None, value=ast.StrLiteral(
                    parts=[ast.Const("    ")], full_str="    ",
                )),
                ast.VarDecl("s2", type=None, value=ast.StrLiteral(
                    parts=[ast.Const("abc    ")], full_str="abc    ",
                )),
                ast.VarDecl("s3", type=None, value=ast.StrLiteral(
                    parts=[ast.Const("   abc   ")], full_str="   abc   ",
                )),
                ast.VarDecl("s4", type=None, value=ast.StrLiteral(
                    parts=[ast.Const("    abc")], full_str="    abc",
                )),
                ast.VarDecl("s5", type=None, value=ast.StrLiteral(
                    prefix="f",
                    parts=[
                        ast.Const("   "), ast.Args(args=[ast.Id("abc")]),
                    ], full_str="   {abc}",
                )),
            ]),
        ]
    ],
    [
        """def main() -> void {
            s1 := "{#! cat file.txt }";
            s2 := "before {#! command -a -b -c file.txt } after";
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.VarDecl("s1", type=None, value=ast.StrLiteral(
                    parts=[
                        ast.ExternalCommand(["cat", "file.txt"])
                    ],
                    full_str="{#! cat file.txt }",
                )),
                ast.VarDecl("s2", type=None, value=ast.StrLiteral(
                    parts=[
                        ast.Const("before "),
                        ast.ExternalCommand(["command", "-a", "-b", "-c", "file.txt"]),
                        ast.Const(" after"),
                    ],
                    full_str="before {#! command -a -b -c file.txt } after",
                )),
            ]),
        ]
    ],
    [
        """def main() {
            char1 := `a`;
            char2 := `ж`;
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), body=[
                ast.VarDecl("char1", type=None, value=ast.Const("a", type="Char")),
                ast.VarDecl("char2", type=None, value=ast.Const("ж", type="Char")),
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
            empty := @{};
            arr := @{2.718, 3.14};
            uninitialized : @int[10];
            m: @int[2, 2] = @{@{1, 2}, @{3, 4}};
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
                ast.VarDecl("uninitialized", mutable=True, type=ast.ArrayType(
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
            m: @int[2, 2] = @{@{0, 1}, @{2, 3}};
            letters := @{"a", "b", "c", "d"};
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
        """def sum(nums: @int[2]) -> int {
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
        """def mkArray() -> @int[2] {
            return @{0, 1};
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
    [
        """def arrayLiterals() {
            a := @{0, 1};
            b := @int[2]{0, 1};
            c := @int[]{0, 1};
            d := List~int@{0, 1};
            e := list@{0, 1};
        }
        """,
        [
            ast.FuncDef(
                ast.Id("arrayLiterals"),
                body=[
                    ast.VarDecl("a", value=ast.ArrayLit(
                        elems=[ast.Const(0), ast.Const(1)],
                    )),
                    ast.VarDecl("b", value=ast.ArrayLit(
                        elems=[ast.Const(0), ast.Const(1)],
                        base=ast.ArrayType(
                            ast.Id("int"), dims=[ast.Const(2)]
                        )
                    )),
                    ast.VarDecl("c", value=ast.ArrayLit(
                        elems=[ast.Const(0), ast.Const(1)],
                        base=ast.ArrayType(
                            ast.Id("int"), dims=[]
                        )
                    )),
                    ast.VarDecl("d", value=ast.ArrayLit(
                        elems=[ast.Const(0), ast.Const(1)],
                        base=ast.AttachTags(
                            arg=ast.Id("List"),
                            tags=ast.TagList(args=[ast.Id("int")]),
                        )
                    )),
                    ast.VarDecl("e", value=ast.ArrayLit(
                        elems=[ast.Const(0), ast.Const(1)],
                        base=ast.Id("list"),
                    )),
                ]
            ),
        ]
    ],
    [
        """def comprehension() -> void {
            a := @{0, 1};
            b := @for (i in a) i*2;
        }
        """,
        [
            ast.FuncDef(
                ast.Id("comprehension"),
                returns=ast.SimpleRType("void"),
                body=[
                    ast.VarDecl("a", value=ast.ArrayLit(
                        elems=[ast.Const(0), ast.Const(1)],
                    )),
                    ast.VarDecl("b", value=ast.ListComprehension(
                        loop=ast.ForExpr(
                            over=[
                                ast.BinExpr(op="in", arg1=ast.Id("i"), arg2=ast.Id("a"))
                            ],
                            block=ast.Block(
                                body=ast.BinExpr(ast.Id("i"), ast.Const(2), "*"),
                            )
                        ),
                    )),
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
                        ast.VarDecl(name="res", type=ast.Id("int"), mutable=True)
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
            return while (i < arr'len) -> (sum: int) { sum += arr[i]; };
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.Return(
                    ast.WhileExpr(
                        cond=ast.BinExpr(
                            op="<", arg1=ast.Id("i"),
                            arg2=ast.FuncCall(ast.Id("len"), [ast.Id("arr")])),
                        block=ast.Block(
                            body=[ast.BinExpr(
                                op='+=',
                                arg1=ast.Id("sum"),
                                arg2=ast.Select(ast.Id("arr"), ast.Args([ast.Id("i")]))
                            )],
                            returns=[ast.VarDecl("sum", ast.Id("int"), mutable=True)]
                        )
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
                    ],returns=[ast.VarDecl("res", ast.Id("int"), mutable=True)])
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
            for (e in arr) -> (or: Bool = true) {or |= e;};
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
                    block=ast.Block(body=[ast.BinExpr(
                        op="|=", arg1=ast.Id("or"), arg2=ast.Id("e")
                    )],
                    returns=[
                        ast.VarDecl("or", ast.Id("Bool"), mutable=True,
                                    value=ast.Const(True, "true", "Bool"))
                    ]),
                )
            ]),
        ]
    ],
    [
        """def main(limX: int, limY: int, limZ: int) {
            res: mut = 1;
            for (x in :limX) for (y in :limY) for (z in :limZ) {
                res *= 2;
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), params=[
                ast.VarDecl("limX", type=ast.Id("int"), is_param=True),
                ast.VarDecl("limY", type=ast.Id("int"), is_param=True),
                ast.VarDecl("limZ", type=ast.Id("int"), is_param=True),
            ], body=[
                ast.VarDecl("res", value=ast.Const(1), mutable=True),
                ast.ForExpr(
                    over=[
                        ast.BinExpr(
                            arg1=ast.Id("x"),
                            op="in",
                            arg2=ast.SliceExpr(end=ast.Id("limX"))
                        ),
                    ],
                    block=ast.Block(
                        body=ast.ForExpr(
                            over=[
                                ast.BinExpr(
                                    arg1=ast.Id("y"),
                                    op="in",
                                    arg2=ast.SliceExpr(end=ast.Id("limY"))
                                ),
                            ],
                            block=ast.Block(
                                body=ast.ForExpr(
                                    over=[
                                        ast.BinExpr(
                                            arg1=ast.Id("z"),
                                            op="in",
                                            arg2=ast.SliceExpr(end=ast.Id("limZ"))
                                        ),
                                    ],
                                    block=ast.Block(
                                        body=[
                                            ast.BinExpr(
                                                ast.Id("res"),
                                                ast.Const(2),
                                                "*="
                                            )
                                        ]
                                    )
                                ),
                            ),
                        ),
                    ),
                )
            ]),
        ]
    ],
    [
        """def main() -> void {
            for (elem in arr) {
                if (elem > 0) {
                    continue;
                }
            }
        }
        """,
        [
            ast.FuncDef(ast.Id("main"), returns=ast.SimpleRType("void"), body=[
                ast.ForExpr(
                    over=[
                        ast.BinExpr(op="in", arg1=ast.Id("elem"), arg2=ast.Id("arr"))
                    ],
                    block=ast.Block(body=[
                        ast.IfExpr(
                            cond=ast.BinExpr(ast.Id("elem"), ast.Const(0), op=">"),
                            block=ast.Block(body=[
                                ast.Continue(),
                            ])
                        )
                    ])
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


@pytest.mark.parametrize("code, exp_ast", [
    [
        """
        struct TaskStatus~Enum {
            start := 0;
            pending := 1;
            end := 2;
        }

        def test() {
            a : mut = Status.start;
            a =.pending;
            a = .end;
            a = . end;
            b := Status{.end};
        }
        """,
        [
            ast.StructDef(
                "TaskStatus",
                tags=ast.TagList(
                    args=[
                        ast.Id("Enum"),
                    ]
                ),
                fields=[
                    ast.VarDecl("start", value=ast.Const(0)),
                    ast.VarDecl("pending", value=ast.Const(1)),
                    ast.VarDecl("end", value=ast.Const(2)),
                ]
            ),
            ast.FuncDef(
                ast.Id("test"),
                body=[
                    ast.VarDecl(
                        "a", mutable=True, value=ast.BinExpr(
                            arg1=ast.Id("Status"),
                            arg2=ast.Id("start"),
                            op=".",
                        )
                    ),
                    ast.BinExpr(
                        ast.Id("a"),
                        ast.BinExpr(
                            arg1=ast.Id("pending"),
                            arg2=ast.Const(True),
                            op="=",
                        ),
                        op="=",
                    ),
                    ast.BinExpr(
                        ast.Id("a"),
                        ast.BinExpr(
                            arg1=ast.Id("end"),
                            arg2=ast.Const(True),
                            op="=",
                        ),
                        op="=",
                    ),
                    ast.BinExpr(
                        ast.Id("a"),
                        ast.BinExpr(
                            arg1=ast.Id("end"),
                            arg2=ast.Const(True),
                            op="=",
                        ),
                        op="=",
                    ),
                    ast.VarDecl(
                        "b",
                        value=ast.StructLiteral(
                            name=ast.Id("Status"),
                            kwargs={
                                "end": ast.Const(True),
                            }
                        )
                    )
                ]
            )
        ]
    ],
])
def test_toggles(code, exp_ast):
    act_ast = parse_code(code)
    assert act_ast == exp_ast