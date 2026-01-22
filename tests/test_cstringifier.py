import pytest
from xyc.cstringifier import stringify, stringify_expr
from xyc.cast import *

@pytest.mark.parametrize("expr, exp_code", [
    (
        Expr(Id("a"), Id("b"), "+"),
        "a + b"
    ),
    (
        Expr(Id("a"), Expr(Id("b"), Id("c"), "+"), "-"),
        "a - (b + c)"
    ),
    (
        Expr(Id("a"), Expr(Id("b"), Id("c"), "<<"), "<<"),
        "a << (b << c)"
    ),
    (
        Expr(Expr(Id("b"), Id("c"), "<<"), Id("a"), "<<"),
        "b << c << a"
    ),
    (
        Expr(Expr(Id("a"), Id("b"), "||"), Expr(Id("c"), Id("d"), "||"), "&&"),
        "(a || b) && (c || d)"
    ),
    (
        Expr(Expr(Id("a"), Id("b"), "&&"), Expr(Id("c"), Id("d"), "&&"), "||"),
        "(a && b) || (c && d)"  # always put brakets around logical or bitwise expressions
    ),
    (
        Expr(Expr(Id("a"), Id("b"), "&"), Expr(Id("c"), Id("d"), "&"), "|"),
        "(a & b) | (c & d)"  # always put brakets around logical or bitwise expressions
    ),
    (
        Expr(
            Expr(Id("a"), Expr(Id("b"), Id("c"), "&"), "|"),
            Id("d"),
            "|"
        ),
        "a | (b & c) | d"
    ),
    (
        Expr(
            Expr(Id("a"), Expr(Id("b"), Id("c"), "*"), "|"),
            Id("d"),
            "|"
        ),
        "a | b * c | d"
    ),
    (
        Expr(Expr(Id("a"), Id("b"), "&"), Expr(Id("c"), Id("d"), "^"), "||"),
        "a & b || c ^ d"
    ),
    (
        Expr(Expr(Id("a"), Id("b"), "&"), Expr(Id("c"), Id("d"), "^"), "|"),
        "(a & b) | (c ^ d)"
    ),
    (
        Cast(Cast(Expr(Id("a"), Id("b"), "-"), to="int"), to="float"),
        "(float)(int)(a - b)"
    ),
    (
        Cast(CompoundLiteral(Id("type"), args=[Expr(Id("a"), Id("b"), "-")]), to="float"),
        "(float)(type){a - b}"
    ),
    (
        UnaryExpr(
            Expr(
                Expr(
                    Expr(Id("a"), Id("b"), "->"),
                    Id("c"), "->"
                ),
                Id("d"), "."
            ),
            op="++"
        ),
        "a->b->c.d++"
    ),
    (
        UnaryExpr(
            Expr(
                Expr(
                    UnaryExpr(Expr(Id("a"), Id("b"), "->"), op="++"),
                    Id("c"), "->"
                ),
                Id("d"), "."
            ),
            op="++"
        ),
        "a->b++->c.d++"
    ),
])
def test_op_precedence(expr, exp_code):
    frags = []
    stringify_expr(expr, frags)
    code = "".join(frags)
    assert code == exp_code