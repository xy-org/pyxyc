import pytest
from xyc.parser import parse_code, ParsingError


@pytest.mark.parametrize("code, err_msg", [
    (
        "def double(x: int) x*2",
        "Macro functions require a terminating semicolon."
    ),
    (
        """def double(x: int) {
            return x*2;
        } ;""",
        "Function definitions don't require a terminating semicolon."
    ),
    (
        """
        def double(x: int) x*2;
        ;
        def zero(x: int) 0;
        """,
        "Empty statements are not allowed. Please remove the semicolon."
    ),
    (
        """
        def func() -> int {
            retrn 0;
        }
        """,
        "Malformed expression. Maybe missing operator or semicolon."
    ),
    (
        """
        def func() -> int | Error {
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
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


@pytest.mark.parametrize("code, err_msg", [
    (
        """def double(x: int) -> int | Error {
            error;
        }""",
        "Missing value for \"error\" statement"
    ),
    (
        """def double(x: int) -> int | Error {
            error Error{code=1}, Error{code=2};
        }""",
        "Only one error can be issued"
    ),
])
def test_error_statement(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """import module""",
        "Missing ';' at end of import. All statements or expressions not using a '{}' block require a terminating ';'"
    ),
])
def test_semicolons(code, err_msg):
    if err_msg is not None:
        with pytest.raises(ParsingError, match=err_msg):
            parse_code(code)
    else:
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def func() {
            for (x in :) for (y in :) for (z in :) -> (res: int) { res *= x + y - z }
        }""",
        "Malformed expression. Maybe missing operator or semicolon"
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
    if err_msg is not None:
        with pytest.raises(ParsingError, match=err_msg):
            parse_code(code)
    else:
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def main() {
            a := a +: b -: -c;
        }""",
        "Operator slices make sense only between the start and end expressions of a slice"
    ),
    (
        """def main() {
            f := a : b +: c;
        }""",
        "Operator slices make sense only between the start and end expressions of a slice"
    ),
    (
        """def main() {
            a := a +: ;
        }""",
        "Unexpected end of expression"
    ),
    (
        """def main() {
            a := *: b;
        }""",
        "Operator slices require a start"
    ),
    (
        """def main() {
            a := a func: b;
        }""",
        "Malformed expression."
    ),
])
def test_invalid_slices(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def main() {
            b := a + ;
        }""",
        "Unexpected end of expression"
    ),
    (
        """def main() {
            a := ;
        }""",
        "Unexpected end of expression"
    ),
    (
        """def funct(a: int, b: int) {
            a = a + *b;
        }""",
        "Expected operand found operator"
    ),
    (
        """def funct(a: int, b: int) {
            a => b;
        }""",
        "Malformed expression"
    ),
    (
        """def main() -> void {
            a'bits := 0;
        }
        """,
        "Variable name must be an identifier"
    ),
    (
        """def main() -> void {
            ((func)) a;
        }
        """,
        "Malformed expression"
    ),
    (
        """def main() -> void {
            ()func;
        }
        """,
        "No expression in brackets"
    ),
    (
        """def main() -> void {
            a + ();
        }
        """,
        "No expression in brackets"
    ),
    (
        """def main() -> void {
            s.a{b=d}~Tag;
        }
        """,
        "Only simple positional tags can be chained"
    ),
])
def test_invalid_expression(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def func(
            a: int
            b: int,
        ) {
        }""",
        "Missing comma at end of parameter"
    ),
])
def test_param_lists(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def func() {
            a := ....;
        }""",
        "... is not allowed in expressions"
    ),
    (
        """def func() {
            a := 0.5.0;
        }""",
        "Malformed expression."
    ),
    (
        """def func() {
            a := .5.;
        }""",
        "Invalid floating point literal"
    ),
    (
        """def func() {
            a := 0xABv;
        }""",
        "Invalid character in base-16 number"
    ),
])
def test_invalid_num_consts(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def main() {
            func(..., a=5);
        }""",
        "Cannot have any arguments after ..."
    ),
    (
        """def main() {
            func(a=5, ..., b=4);
        }""",
        "Cannot have any arguments after ..."
    ),
    (
        """def main() {
            func(5+...);
        }""",
        "... is not allowed in expressions"
    ),
])
def test_auto_inject_syntax(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


@pytest.mark.parametrize("code, err_msg", [
    (
        """def main() {
            cb := $(int)->int;
        }""",
        "Cannot select based on return type"
    ),
])
def test_callbacks_and_fselect(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


@pytest.mark.parametrize("code, err_msg", [
    (
        """def main~Tag{}() {
            cb := $(int)->int;
        }""",
        "Syntax ambiguity"
    ),
    (
        """def get(ptr: Ptr, idx: int) -> ptr[ Ptr~[<< ptr..to] ] {
        }""",
        "Guards are allowed only on new lines"
    ),
    (
        """def get(^num: int = 0) {
        }""",
        "Caller context parameters cannot have default values"
    ),
    (
        "def get(ptr: Ptr, idx: int) -> ptr[ Ptr~[^ptr..to] ] ptr",
        "Blocks must have their body in curly brackets"
    ),
    (
        "def *func() {}",
        "Visibility marker goes before 'def'"
    ),
    (
        "*\ndef func() {}",
        "Visibility marker cannot stand on its own"
    ),
    (
        "struct *Struct() {}",
        "Visibility marker goes before 'struct'"
    ),
    (
        """
        def x(a: Array) -> ref(a) Int {}
        """,
        "Blocks must have their body in curly brackets"
    ),
    (
        """
        def x(a: Array) -> in(a) Int {}
        """,
        "Expected operand found operator"
    ),
    (
        """
        def x(start: Size := 0) {}
        """,
        "Extra ':' in variable declaration"
    ),
])
def test_func_def_errors(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


@pytest.mark.parametrize("code, err_msg", [
    (
        """struct Struct {
            value=10;
        }
        """,
        "Unexpected expression in struct definition"
    ),
    (
        """struct Struct~Tag{value=10} {
            value: int;
        }""",
        "Unexpected expression in struct definition"
    ),
])
def test_struct_errors(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def test() {
            if(false) {
            }
            elif;
        }
        """,
        "Missing conditional expression"
    ),
    (
        """def test() {
            if (cond1) {
            } if (cond2) {
            }
        }
        """,
        "Cannot put an if on the same line as another if. Did you mean `elif`?"
    ),
])
def test_if_errors(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """def test() {
            arr := @{
                "Line 1",
                ;; comment 1
            };
        }
        """,
        "Doc comment is not followed by anything"
    ),
])
def test_doc_comments(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)
