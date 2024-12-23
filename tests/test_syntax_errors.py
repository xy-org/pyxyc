import pytest
from xyc.parser import parse_code, ParsingError


@pytest.mark.parametrize("code, err_msg", [
    (
        "def double(x: int) x*2;",
        "Function definitions don't require a terminating semicolon."
    ),
    (
        """def double(x: int) {
            return x*2;
        } ;""",
        "Function definitions don't require a terminating semicolon."
    ),
    (
        """
        def double(x: int) x*2
        ;
        def zero(x: int) 0
        """,
        "Empty statements are not allowed. Please remove the semicolon."
    ),
    (
        """
        def fucn() -> int {
            retrn 0;
        }
        """,
        "Malformed expression. Maybe missing operator or semicolon."
    ),
    (
        """
        def func() -> int || Error {
            err Error{0};
        }
        """,
        "Malformed expression. Maybe missing operator or semicolon."
    ),
    (
        """
        struct Struct {
            field: int
        }
        """,
        "Missing ';' at end of field"
    ),
])
def test_misplaced_semicolon(code, err_msg):
    act_error = None
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


@pytest.mark.parametrize("code, err_msg", [
    (
        """def double(x: int) -> int || Error {
            error;
        }""",
        "Missing value for \"error\" statement"
    ),
    (
        """def double(x: int) -> int || Error {
            error Error{code=1}, Error{code=2};
        }""",
        "Only one error can be issued"
    ),
])
def test_error_statement(code, err_msg):
    act_error = None
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def func() {
            for (x in :) for (y in :) for (z in :) -> (res: int) res *= x + y - z
        }""",
        "Missing ';' at end of expression"
    ),
    (
        """def func() {
            for (x in :) func2(x)
        }""",
        "Missing ';' at end of expression"
    ),
    (
        """def func() {
            for (x in :) {
                func2(x);
            };
        }""",
        None
    ),
])
def test_semicolon_and_fors(code, err_msg):
    act_error = None
    if err_msg is not None:
        with pytest.raises(ParsingError, match=err_msg):
            parse_code(code)
    else:
        parse_code(code)