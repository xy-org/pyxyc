import pytest
from xyc.parser import parse_code, ParsingError


@pytest.mark.parametrize("code, err_msg", [
    (
        "func double(x: int) x*2",
        "Macro functions require a terminating semicolon."
    ),
    (
        """func double(x: int) {
            return x*2;
        } ;""",
        "Function definitions don't require a terminating semicolon."
    ),
    (
        """
        func double(x: int) x*2;
        ;
        func zero(x: int) 0;
        """,
        "Empty statements are not allowed. Please remove the semicolon."
    ),
    (
        """
        func fun() -> int {
            retrn 0;
        }
        """,
        "Malformed expression. Maybe missing operator or semicolon."
    ),
    (
        """
        func fun() -> int | Error {
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
        """func double(x: int) -> int | Error {
            error;
        }""",
        "Missing value for \"error\" statement"
    ),
    (
        """func double(x: int) -> int | Error {
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
        """func fun() {
            for (x in :) for (y in :) for (z in :) -> (res: int) { res *= x + y - z }
        }""",
        "Malformed expression. Maybe missing operator or semicolon"
    ),
    (
        """func fun() {
            for (x in :) func2(x)
        }""",
        "Missing ';' at end of expression"
    ),
    (
        """func fun() {
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
        """func main() {
            a := a +: b -: -c;
        }""",
        "Operator slices make sense only between the start and end expressions of a slice"
    ),
    (
        """func main() {
            f := a : b +: c;
        }""",
        "Operator slices make sense only between the start and end expressions of a slice"
    ),
    (
        """func main() {
            a := a +: ;
        }""",
        "Unexpected end of expression"
    ),
    (
        """func main() {
            a := *: b;
        }""",
        "Operator slices require a start"
    ),
    (
        """func main() {
            a := a fun: b;
        }""",
        "Malformed expression."
    ),
])
def test_invalid_slices(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)

@pytest.mark.parametrize("code, err_msg", [
    (
        """func main() {
            b := a + ;
        }""",
        "Unexpected end of expression"
    ),
    (
        """func main() {
            a := ;
        }""",
        "Unexpected end of expression"
    ),
    (
        """func funct(a: int, b: int) {
            a = a + *b;
        }""",
        "Expected operand found operator"
    ),
    (
        """func funct(a: int, b: int) {
            a => b;
        }""",
        "Malformed expression"
    ),
    (
        """func main() -> void {
            a'bits := 0;
        }
        """,
        "Variable name must be an identifier"
    ),
    (
        """func main() -> void {
            ((fun)) a;
        }
        """,
        "Malformed expression"
    ),
    (
        """func main() -> void {
            ()func;
        }
        """,
        "No expression in brackets"
    ),
    (
        """func main() -> void {
            a + ();
        }
        """,
        "No expression in brackets"
    ),
    (
        """func main() -> void {
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
        """func fun(
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
        """func fun() {
            a := ....;
        }""",
        "... is not allowed in expressions"
    ),
    (
        """func fun() {
            a := 0.5.0;
        }""",
        "Malformed expression."
    ),
    (
        """func fun() {
            a := .5.;
        }""",
        "Invalid floating point literal"
    ),
    (
        """func fun() {
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
        """func main() {
            fun(..., a=5);
        }""",
        "Cannot have any arguments after ..."
    ),
    (
        """func main() {
            fun(a=5, ..., b=4);
        }""",
        "Cannot have any arguments after ..."
    ),
    (
        """func main() {
            fun(5+...);
        }""",
        "... is not allowed in expressions"
    ),
])
def test_auto_inject_syntax(code, err_msg):
    with pytest.raises(ParsingError, match=err_msg):
        parse_code(code)


@pytest.mark.parametrize("code, err_msg", [
    (
        """func main() {
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
        """func main~Tag{}() {
            cb := $(int)->int;
        }""",
        "Syntax ambiguity"
    ),
    (
        """func get(ptr: Ptr, idx: int) -> ptr[ Ptr~[<< ptr..to] ] {
        }""",
        "Guards are allowed only on new lines"
    ),
    (
        """func get(^num: int = 0) {
        }""",
        "Caller context parameters cannot have default values"
    ),
    (
        "func get(ptr: Ptr, idx: int) -> ptr[ Ptr~[^ptr..to] ] ptr",
        "Blocks must have their body in curly brackets"
    ),
    (
        "func *fun() {}",
        "Visibility marker goes before 'def'"
    ),
    (
        "*\ndef fun() {}",
        "Visibility marker cannot stand on its own"
    ),
    (
        "struct *Struct() {}",
        "Visibility marker goes before 'struct'"
    ),
    (
        """
        func x(a: Array) -> ref(a) Int {}
        """,
        "Blocks must have their body in curly brackets"
    ),
    (
        """
        func x(a: Array) -> in(a) Int {}
        """,
        "Expected operand found operator"
    ),
    (
        """
        func x(start: Size := 0) {}
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
        """func test() {
            if(false) {
            }
            elif;
        }
        """,
        "Missing conditional expression"
    ),
    (
        """func test() {
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
        """func test() {
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
