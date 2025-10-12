import re
from difflib import SequenceMatcher as SM
from xyc.tokenizer import split_tokens
from xyc.ast import *


class TokenIter:
    def __init__(self, tokens, token_pos, src):
        self.tokens = tokens
        self.tokens.extend(("", ""))  # XXX, Yes, I know we are modifying the argument
        self.token_pos = token_pos
        self.token_pos.extend([0, 0])
        self.num_tokens = len(self.tokens) - 2
        self.i = 0
        self.src = src

    def has_more(self):
        return self.i < self.num_tokens

    def peak(self):
        return self.tokens[self.i]

    def peakn(self, n: int):
        if self.i + n >= len(self.tokens):
            raise ParsingError("Unexpected end of file", self)
        return self.tokens[self.i:self.i+n]

    def peak_coords(self, offset = 0):
        if self.i + offset < self.num_tokens:
            return (
                self.token_pos[self.i + offset  ],
                self.token_pos[self.i + offset  ] + len(self.peak())
            )
        else:
            return (len(self.src.code), len(self.src.code))

    def consume(self, n=1):
        if not self.has_more():
            raise ParsingError("Unexpected end of file", self)
        res = self.tokens[self.i] if n==1 else self.tokens[self.i:self.i+n]
        self.i += n
        return res

    def expect(self, token, msg=None):
        if self.peak() != token:
            if msg:
                raise ParsingError(msg, self)
            raise ParsingError(f"Unexpected token (expected '{token}')", self)
        self.i += 1

    def expect_semicolon(self, msg=None):
        if not self.has_more():
            raise ParsingError(msg, self)
        if not self.check_semicolon():
            if msg:
                raise ParsingError(msg, self)
            raise ParsingError(f"Unexpected token (expected semicolon)", self)

    def expect_eol(self):
        if not self.peak_eol():
            raise ParsingError(f"Unexpected token (expected EoL)", self)
        self.i += 1

    def peak_eol(self):
        return not self.has_more() or self.peak() == "\n"

    def check(self, exp):
        if self.has_more() and self.peak() == exp:
            self.i += 1
            return True
        return False

    def check_semicolon(self):
        return self.check(";") or self.peak() == ";;"

    def skip_until(self, delim):
        while self.has_more() and self.consume() != delim:
            pass

    def skip_empty_lines(self):
        i = 0
        while self.has_more():
            if self.check("#"):
                while self.has_more() and self.peak() != "\n":
                    self.consume()
                self.check("\n")
            elif self.check("\n"):
                pass
            else:
                break
            i += 1
        return i


class ParsingError(Exception):
    def __init__(self, msg, itoken, notes=None):
        fn = itoken.src.filename
        highlight, line_num, char_num = self.highlight_src_line(itoken, itoken.i)
        self.fmt_msg = f"{fn}:{line_num}:{char_num}: error: {msg}\n"
        self.fmt_msg += highlight

        for note in (notes or []):
            self.fmt_msg += "note: " + note[0] + "\n"
            if note[1] is not None:
                highlight, _, _ = self.highlight_src_line(itoken, note[1])
                self.fmt_msg += highlight

    def highlight_src_line(self, itoken: TokenIter, token_idx):
        if token_idx < len(itoken.tokens):
            loc = itoken.token_pos[token_idx]
            token_len = len(itoken.tokens[token_idx])
        else:
            loc = itoken.token_pos[-1] + len(itoken.tokens[-1]) - 1
            token_len = 1
            token_idx = len(itoken.token_pos) - 1

        line_num = 1
        line_loc = 0
        for i in range(token_idx):
            token = itoken.tokens[i]
            if token == "\n":
                line_num += 1
                line_loc = itoken.token_pos[i]+1
        line_end = len(itoken.src.code)
        for i in range(token_idx, len(itoken.tokens)):
            token = itoken.tokens[i]
            if token == "\n":
                line_end = itoken.token_pos[i]
                break

        src_line = itoken.src.code[line_loc:line_end].replace("\t", " ")
        res = f"| {src_line}\n"
        res += "  " + (" " * (loc-line_loc)) + ("^" * token_len) + "\n"
        return res, line_num, loc - line_loc + 1

    def __str__(self):
        return self.fmt_msg


def parse_code(src) -> Ast:
    if isinstance(src, str):
        src = Source("<unknown>", src)
    tokens, token_pos = split_tokens(src.code)
    itoken = TokenIter(tokens, token_pos, src)

    ast = parse_stmt_list(itoken)

    if itoken.has_more():
        raise ParsingError("Unexpected token", itoken)

    return ast

semicolon_error_explanation = "All statements or expressions not using a '{}' block require a terminating ';'"
def parse_import(itoken):
    coords = itoken.peak_coords()
    itoken.consume()  # "import"
    lib = itoken.consume()
    multi = []
    while not itoken.peak_eol() and itoken.check("."):
        if itoken.check("("):
            multi = parse_expr_list(itoken, is_toplevel=False)
            itoken.expect(")")
            break
        else:
            lib += "." + itoken.consume()

    tags = TagList()
    if itoken.check("~"):
        tags = parse_tags(itoken)
    if itoken.has_more() and itoken.peak() == "{":
        raise ParsingError(
            "Ambiguous brackets. Please be explicit and seprate the tags in square brackets.",
            itoken
        )

    in_name = None
    if itoken.check("in"):
        in_name = itoken.consume()

    coords = (coords[0], itoken.peak_coords()[1] - 1)

    if itoken.peak() == ",":
        raise ParsingError("Importing more than one module at a time is NYI.", itoken)
    itoken.expect_semicolon(msg=f"Missing ';' at end of import. {semicolon_error_explanation}")

    res = []
    if len(multi) == 0:
        res.append(
            Import(
                lib=lib, in_name=in_name, tags=tags, src=itoken.src, coords=coords
            )
        )
    else:
        for sub_expr in multi:
            sub_lib = lib + "." + sub_expr.src.code[sub_expr.coords[0]:sub_expr.coords[1]]
            res.append(
                Import(
                    lib=sub_lib, in_name=in_name, tags=tags, src=itoken.src, coords=coords
                )
            )
    return res

def parse_sl_comment(itoken):
    comment_start = itoken.token_pos[itoken.i-1]+1
    itoken.skip_until("\n")
    comment_end = itoken.token_pos[itoken.i-1]

    comment = itoken.src.code[comment_start:comment_end]
    return Comment(
        comment=comment,
        src=itoken.src, coords=[comment_start-1, comment_start]
    )

def parse_ml_comment(itoken, until_eol=False):
    comment_start = itoken.token_pos[itoken.i-1]
    itoken.skip_until("\n")
    while not until_eol and itoken.check(";;"):
        itoken.skip_until("\n")
    comment_end = itoken.token_pos[itoken.i-1]

    comment = itoken.src.code[comment_start:comment_end]
    return Comment(comment=comment, src=itoken.src,
                   coords=[comment_start, comment_start+2])

def parse_def(itoken: TokenIter, check_semicolon=True):
    visibility = PackageVisibility
    if itoken.peak() in {"-", "+", "*"}:
        visibility = visibilityMap[itoken.consume()]
    itoken.expect("def")
    if itoken.peak() in {"-", "+", "*"}:
        raise ParsingError("Visibility marker goes before 'def'", itoken)
    name_coords = itoken.peak_coords()
    name = itoken.consume()
    node = FuncDef(
        name=Id(name, src=itoken.src, coords=name_coords),
        src=itoken.src, coords=name_coords,
        visibility=visibility,
    )
    if itoken.check("~"):
        node.tags = parse_tags(itoken)
        if itoken.peak() == "{":
            raise ParsingError("Syntax ambiguity. Please be specific and use square brackets to separate tags.", itoken)
    node.params = parse_params(itoken)

    if itoken.check("="):
        value = parse_block(itoken)
        if not isinstance(value.body, list):
            node.body = value.body
        else:
            node.body = value
    else:
        value = parse_block(itoken)
        node.returns = value.returns
        node.etype = value.etype
        node.in_guards = value.in_guards
        node.out_guards = value.out_guards
        node.body = value.body

    if check_semicolon and isinstance(node.body, list):
        if itoken.has_more() and itoken.peak() == ";":
            raise ParsingError(
                "Function definitions don't require a terminating semicolon.",
                itoken
            )
    elif check_semicolon:
        # macro
        if not itoken.check(";"):
            raise ParsingError(
                "Macro functions require a terminating semicolon.",
                itoken
            )

    return node

def parse_func_select(itoken: TokenIter):
    node = FuncSelect(
        name=None,
        src=itoken.src, coords=itoken.peak_coords()
    )
    assert itoken.check("$")

    if itoken.check("*"):
        node.multiple = True

    if itoken.peak() not in {"(", "~"}:
        name_coords = itoken.peak_coords()
        name = itoken.consume()
        node.name = Id(name, src=itoken.src, coords=name_coords)

    if itoken.check("~"):
        node.tags = parse_tags(itoken)
    itoken.expect("(")
    node.args, node.kwargs = parse_args_kwargs(itoken)
    itoken.expect(")")

    if itoken.check("->"):
        raise ParsingError("Cannot select based on return types", itoken)

    return node

def parse_block(itoken, accept_early_return=False):
    block = Block(src=itoken.src)
    explicit_block = False

    args = []
    if itoken.check("->"):
        explicit_block = True
        if itoken.check("("):
            args = parse_expr_list(itoken)
            itoken.expect(")")
        else:
            args = [parse_toplevel_type_expr(itoken)]

        if itoken.check("|"):
            block.etype = parse_toplevel_type_expr(itoken)

    for expr in args:
        expr = expr_to_type(expr)
        if isinstance(expr, VarDecl):
            expr.mutable = True
            block.returns.append(expr)
        elif isinstance(expr, Select):
            assert len(expr.args.args) <= 1
            assert len(expr.args.kwargs) == 0
            index_in = expr.base if expr.base is not None else nobase
            block.returns.append(
                VarDecl(type=expr.args.args[0], index_in=index_in, mutable=True, src=expr.src, coords=expr.coords)
            )
        else:
            block.returns.append(
                VarDecl(type=expr, src=expr.src, coords=expr.coords)
            )

    num_empty = itoken.skip_empty_lines()
    while itoken.peak() in {">>", "<<"}:
        guard_token = itoken.consume()
        if num_empty <= 0:
            raise ParsingError("Guards should be on new lines", itoken)
        guard_expr = parse_expression(itoken)
        if guard_token == "<<":
            block.out_guards.append(guard_expr)
        else:
            block.in_guards.append(guard_expr)
        # itoken.expect_semicolon()
        num_empty = itoken.skip_empty_lines()

    block.coords = itoken.peak_coords()

    if explicit_block:
        itoken.expect("{", "Blocks must have their body in curly brackets '{body}'")
        itoken.consume(-1)
        block.body = parse_body(itoken)
    elif itoken.peak() in {"return", "error"}:
        if not accept_early_return:
            raise ParsingError(f"'{itoken.peak()}' is not allowed here", itoken)

        if itoken.peak() == "return":
            block.body = [parse_return(itoken)]
        else:
            block.body = [parse_error(itoken)]
    elif itoken.peak() != "{":
        block.body = parse_expression(itoken)
    else:
        block.body = parse_body(itoken)

    return block

def parse_params(itoken, is_error_block=False):
    res = []
    itoken.expect("||" if is_error_block else "(", msg="Missing param list")
    term_bracket = "||" if is_error_block else ")"
    itoken.skip_empty_lines()
    comment = ""
    while itoken.peak() not in {")", "]", "}", ";", "||"}:
        if itoken.check(";;"):
            comment = parse_ml_comment(itoken).comment
        if not is_error_block:
            param = parse_expression(itoken)
        else:
            # needs some special handling for the terminating |
            toplevel_precedence_map = {**operator_precedence}
            del toplevel_precedence_map["||"]
            param = parse_expression(itoken, op_prec=toplevel_precedence_map)
        if not isinstance(param, VarDecl):
            raise ParsingError("Invalid parameter. Proper syntax is 'name : Type = value'", itoken)

        if not itoken.check(","):
            # no , - better be the last param
            itoken.skip_empty_lines()
            if itoken.peak() != term_bracket:
                raise ParsingError("Missing comma at end of parameter", itoken)

        if param.name is None:
            param.is_pseudo = True

        if not param.explicit_mutable:
            param.mutable = False
        param.is_param = True
        res.append(param)

        param.comment = comment
        comment = ""
        if itoken.check(";;"):
            param.comment += parse_ml_comment(itoken, until_eol=True).comment

        itoken.skip_empty_lines()

    itoken.skip_empty_lines()
    itoken.expect(term_bracket)
    return res

def parse_toplevel_type_expr(itoken):
    # this new map is here purely to provide better error messages in cases like
    # def func() -> MyType{} {...}
    # or
    # def func() -> Type1 || Type2 || Type3 {...}
    toplevel_precedence_map = {**operator_precedence}
    del toplevel_precedence_map["|"]
    del toplevel_precedence_map["||"]
    del toplevel_precedence_map["{"]
    del toplevel_precedence_map["="]

    return parse_expression(itoken, op_prec=toplevel_precedence_map)

# ref is a reserved keyword
var_qualifiers = {"mut", "in", "out", "inout", "outin", "pseudo"}

operator_precedence = {
    "unary^": 12, "unary[": 12, "unary'": 12,
    "~": 11, "++" : 11, "--": 11, ".": 11, "(": 11, "[": 11, "{": 11, "'": 11, "..": 11,
    "unary+": 10, "unary-": 10, "!": 10, "&": 10, '%': 10,
    "\\": 9, "@": 9, "^": 9,
    "*": 8, "/": 8,
    "+": 7, "-": 7,
    "<": 6, "<=": 6, ">=": 6, ">": 6, ":": 6, "+:": 6, "*:": 6, "-:": 6,
    "==": 5, "!=": 5, "in": 5,
    "&&": 4,
    "||": 3, "|": 3,
    "=": 2, '+=': 2, '-=': 2, "|=": 2, "&=": 2, '*=': 2, '/=': 2, ".=": 2, "=<": 2, "=>": 2, "@=": 2, # right assoc
}
MIN_PRECEDENCE=2
UNARY_PRECEDENCE=10

@dataclass
class Empty(Node):
    pass

def parse_expression(
        itoken, precedence=MIN_PRECEDENCE, is_struct=False,
        op_prec=operator_precedence, is_toplevel=True
):
    arg1 = parse_operand(itoken, precedence, op_prec)

    arg1 = do_parse_expression(arg1, itoken, precedence, op_prec)

    if (precedence == MIN_PRECEDENCE and isinstance(arg1, SliceExpr)
        and arg1.step is None and arg1.end is not None
        and not isinstance(arg1.end, Const)
        and is_toplevel):
        # it's actually a var decl
        decl = VarDecl(mutable=not is_struct, src=arg1.src, coords=arg1.coords)
        if arg1.start is not None:
            if isinstance(arg1.start, CallerContextExpr):
                decl.name = arg1.start.arg.name
                decl.is_callerContext = decl.is_pseudo = True
            elif isinstance(arg1.start, Id):
                decl.name = arg1.start.name
        decl.type = expr_to_type(arg1.end)
        arg1 = decl
    elif (precedence == MIN_PRECEDENCE and isinstance(arg1, BinExpr)
        and arg1.op in {"=", "=<"}
        and isinstance(arg1.arg1, SliceExpr)
        and arg1.arg1.step is None
        and is_toplevel):
        # it's actually a var decl
        decl = VarDecl(mutable=not is_struct, src=arg1.src, coords=arg1.coords)
        decl.is_move = arg1.op == "=<"
        if arg1.arg1.start is not None:
            decl.coords = arg1.arg1.start.coords
            if isinstance(arg1.arg1.start, CallerContextExpr):
                decl.name = arg1.arg1.start.arg.name
                decl.is_callerContext = decl.is_pseudo = True
            elif isinstance(arg1.arg1.start, Id):
                decl.name = arg1.arg1.start.name
            else:
                raise ParsingError("Variable name must be an identifier", itoken)
        decl.type = expr_to_type(arg1.arg1.end) if arg1.arg1.end is not None else None
        decl.value = arg1.arg2
        if not is_struct:
            decl.mutable = decl.value is None
        arg1 = decl

    return arg1

def do_parse_expression(
        arg1,
        itoken, precedence=MIN_PRECEDENCE,
        op_prec=operator_precedence,
):
    lookahead = itoken.peak()
    my_slice = False
    while op_prec.get(lookahead, -1) >= precedence:
        if lookahead in {"(", "'", "\\", "{", "["}:
            arg1 = parse_operator(arg1, itoken, op_prec[lookahead], op_prec)
            lookahead = itoken.peak()
        elif lookahead == "~" and itoken.peakn(2)[1] == "[":
            arg1 = parse_operator(arg1, itoken, op_prec[lookahead], op_prec)
            lookahead = itoken.peak()
        else:
            op = itoken.consume() # the operator

            # check for postfix operator
            if op == "=>":
                arg1 = UnaryExpr(arg1, op=op, src=itoken.src, coords=itoken.peak_coords(-1))
                return arg1
            elif op in {"++", "--"}:
                arg1 = UnaryExpr(arg1, op=op, src=itoken.src, coords=itoken.peak_coords(-1))
                lookahead = itoken.peak()
                continue

            # check for postfix :
            if itoken.peak() in op_prec:
                if op == ":" and op_prec[op] > op_prec[itoken.peak()]:
                    if my_slice:
                        if itoken.peak() == "=":
                            raise ParsingError("Extra ':' in variable declaration", itoken)
                        else:
                            raise ParsingError("If a second ':' is present the step is mandatory", itoken)
                    arg1 = SliceExpr(arg1, None, None, src=itoken.src, coords=itoken.peak_coords())
                    lookahead = itoken.peak()
                    continue

            if op == ":" and is_end_of_expr(itoken):
                arg1 = SliceExpr(arg1, None, None, src=itoken.src, coords=itoken.peak_coords())
                return arg1

            if itoken.peak() in var_qualifiers and op == ":":
                arg1 = parse_var_decl(itoken, arg1, precedence, op_prec)
                lookahead = itoken.peak()
                continue

            rhs = parse_operand(itoken, precedence, op_prec)
            lookahead = itoken.peak()
            while op_prec.get(lookahead, -1) > (op_prec[op] - int(is_right_assoc(lookahead))):
                if is_right_assoc(lookahead) and op_prec[lookahead] == op_prec[op] and not is_right_assoc(op):
                    # horrible if to allow for expressions like a.b~Tag
                    break
                plus_one = int(op_prec[lookahead] > op_prec[op])
                rhs = do_parse_expression(rhs, itoken, op_prec[op] + plus_one, op_prec)
                lookahead = itoken.peak()

            arg1, my_slice = combine_op(op, arg1, rhs, my_slice, itoken)
    return arg1

def combine_op(op, arg1, rhs, my_slice, itoken):
    coords = [0, 0]
    if arg1 is not None:
        coords[0] = arg1.coords[0]
    if rhs is not None:
        coords[1] = rhs.coords[1]

    if op in {":", "+:", "-:", "*:"}:
        if my_slice:
            if op != ":":
                raise ParsingError("Operator slices make sense only between the start and end expressions of a slice", itoken)
            arg1.step = rhs
        else:
            arg1 = SliceExpr(arg1, rhs)
            if len(op) > 1:
                arg1.op = op[0]
        my_slice = True
    elif op in {"=", "=<"} and isinstance(arg1, SliceExpr) and my_slice:
        coords = arg1.start.coords if arg1.start else arg1.coords
        decl = VarDecl(None, arg1.end, rhs)
        if isinstance(arg1.start, CallerContextExpr):
            raise ParsingError("Caller context parameters cannot have default values", itoken)
        elif isinstance(arg1.start, Id):
            decl.name = arg1.start.name
        decl.is_move = op == "=<"
        arg1 = decl
    elif op == '~':
        arg1 = AttachTags(arg1, TagList([rhs]))
    elif op == "@" and isinstance(rhs, ForExpr):
        arg1 = ListComprehension(arg1, rhs)
    else:
        arg1 = BinExpr(arg1, rhs, op=op)

    arg1.src = itoken.src
    arg1.coords = coords

    return arg1, my_slice

def is_right_assoc(op):
    return op in {"=", "+=", "-=", "*=", "/=", "&=", "|=", "=<", "@=", "~"}

def parse_operand(itoken, precedence, op_prec):
    itoken.skip_empty_lines()
    if itoken.peak() == "if":
        return parse_if(itoken)
    elif itoken.peak() in {"else", "elif"}:
        raise ParsingError("Missing corresponding if", itoken)
    elif itoken.peak() == "while":
        return parse_while(itoken)
    elif itoken.peak() == "do":
        return parse_do_while(itoken)
    elif itoken.peak() in {"break", "continue"}:
        return parse_break_continue(itoken)
    elif itoken.peak() == "for":
        return parse_for(itoken)
    elif itoken.peak() == ";":
        raise ParsingError("Unexpected end of expression.", itoken)
    elif itoken.peak() == "...":
        raise ParsingError("... is not allowed in expressions", itoken)

    if itoken.check("("):
        # bracketed expression, func type, or reverse calling notation
        next_token = itoken.peak()
        bracketed_exprs = parse_expr_list(itoken, is_toplevel=False)
        itoken.expect(")", msg="Missing closing bracket")
        if len(bracketed_exprs) == 1 and isinstance(bracketed_exprs[0], Id) and not is_end_of_expr(itoken) and next_token[0].isalpha():
            # reverse function call notation
            coords = itoken.peak_coords()
            ret_args, kwargs, inject_args = parse_args_kwargs(itoken, accept_inject=True, is_toplevel=False, accept_ml_comments=False)
            arg1 = FuncCall(bracketed_exprs[0], ret_args, kwargs, inject_args,
                            src=itoken.src, coords=coords)
        elif itoken.peak() != "->":
            # bracketed expression
            if len(bracketed_exprs) == 0:
                raise ParsingError("No expression in brackets", itoken)
            elif len(bracketed_exprs) > 1:
                arg1 = Enumeration(bracketed_exprs, src=itoken.src, coords=(bracketed_exprs[0].coords[0], bracketed_exprs[-1].coords[1]))
            else:
                arg1 = bracketed_exprs[0]
        else:
            # Func type
            coords = itoken.peak_coords()
            itoken.consume()
            params = [
                expr_to_param(expr, itoken)
                for expr in bracketed_exprs
            ]
            arg1 = FuncType(params=params, src=itoken.src, coords=coords)
            ret_args = []
            if itoken.check("("):
                ret_args = parse_expr_list(itoken)
                itoken.expect(")")
            else:
                ret_args = [parse_toplevel_type_expr(itoken)]

            if itoken.check("|"):
                arg1.etype = parse_toplevel_type_expr(itoken)

            for expr in ret_args:
                expr = expr_to_type(expr)
                if isinstance(expr, VarDecl):
                    expr.mutable = True
                    arg1.returns.append(expr)
                else:
                    arg1.returns.append(
                        VarDecl(type=expr, src=expr.src, coords=expr.coords)
                    )
    elif itoken.peak() == "@":
        coords = itoken.peak_coords()
        assert itoken.check('@')
        if itoken.peak() == "for":
            # list comprehension
            for_expr = parse_for(itoken)
            arg1 = ListComprehension(loop=for_expr, src=itoken.src, coords=coords)
        else:
            # array type or literal
            coords = itoken.peak_coords()
            if itoken.peak() != "{":
                type_name = parse_expression(itoken, op_prec["["]+1, op_prec=op_prec)
                itoken.expect("[", "Missing dimension of array. Syntax is @Type[dimension]")
                dims = parse_expr_list(itoken)
                arg1 = ArrayType(type_name, dims, src=itoken.src, coords=(coords[0], itoken.peak_coords()[1]))
                itoken.expect("]")
            else:
                itoken.expect("{")
                itoken.skip_empty_lines()
                ret_args = parse_expr_list(itoken)
                itoken.expect("}", msg="Missing closing bracket")
                arg1 = ArrayLit(ret_args, src=itoken.src, coords=coords)
    elif itoken.peak() == "[":
        # Indexing without a base i.e. derefing
        coords = itoken.peak_coords()
        itoken.consume() # [
        itoken.skip_empty_lines()
        ret_args, kwargs = parse_args_kwargs(itoken, is_toplevel=False)
        itoken.expect("]", msg="Missing closing bracket")
        arg1 = Select(base=None, args=Args(ret_args, kwargs), src=itoken.src, coords=coords)
    elif itoken.peak() == "'":
        itoken.consume()
        f_coords = itoken.peak_coords()
        fname = parse_expression(itoken, op_prec["'"]+1, op_prec=op_prec)
        fcall = FuncCall(
            fname, src=itoken.src, coords=f_coords,
            inject_context=True
        )
        if itoken.check("("):
            ret_args, kwargs, inject_args = parse_args_kwargs(itoken, accept_inject=True, is_toplevel=False)
            fcall.args.extend(ret_args)
            fcall.kwargs = kwargs
            fcall.inject_args = inject_args
            itoken.expect(")")
        arg1 = fcall
    elif itoken.peak() == "{":
        # announomous struct literal
        itoken.consume()
        arg1 = parse_struct_literal(itoken, None)
    elif itoken.peak() == "|":
        # catch expression
        arg1 = CatchExpr(src=itoken.src, coords=itoken.peak_coords())
        itoken.consume()
        toplevel_precedence_map = {**operator_precedence}
        del toplevel_precedence_map["|"]
        expr = parse_expression(itoken, op_prec=toplevel_precedence_map)
        arg1.expr = expr
        arg1.coords = (arg1.coords[0], itoken.peak_coords()[1])
        itoken.expect("|")
    elif itoken.peak() == "||":
        # inline error block
        arg1 = parse_error_block(itoken)
    elif itoken.peak() == "$":
        arg1 = parse_func_select(itoken)
    elif itoken.peak() == "^":
        coords = itoken.peak_coords()
        itoken.consume()
        arg1 = parse_expression(itoken, op_prec["unary^"]+1, op_prec=op_prec)
        arg1 = CallerContextExpr(arg1, src=itoken.src, coords=coords)
    elif itoken.peak() == "->":
        return parse_block(itoken)
    elif itoken.peak() in {"++", "--"}:
        raise ParsingError("Prefix increment and decrement are not supported. "
                        "More infor at TBD", itoken)
    elif itoken.peak() in {"+", "-", "!", "&", "%", "."}:
        coords = itoken.peak_coords()
        op = itoken.consume()
        switch_off = op == "!" and itoken.check(".")
        # NOTE no precedence + 1 in order to allow for chaining unary operators
        arg1 = parse_expression(itoken, UNARY_PRECEDENCE, op_prec=op_prec)
        if switch_off or op == ".":
            # unary '.' aka. toggle
            arg1 = BinExpr(arg1, Const(not switch_off, src=arg1.src, coords=arg1.coords), op="=")
        elif op in {'-', '+'} and isinstance(arg1, Const) and arg1.type != "str":
            if op == '-':
                arg1.value = -arg1.value
                arg1.value_str = f'-{arg1.value_str}'
        else:
            arg1 = UnaryExpr(arg=arg1, op=op, src=itoken.src, coords=coords)
    elif itoken.peak() == ":":
        coords = itoken.peak_coords()
        itoken.consume()
        if is_end_of_expr(itoken):
            arg1 = SliceExpr(src=itoken.src, coords=coords)
        else:
            itoken.i -= 1
            arg1 = None
    elif itoken.peak() == "def":
        arg1 = parse_def(itoken, check_semicolon=False)
    else:
        arg1 = None

    if arg1 is None:
        tk_coords = itoken.peak_coords()
        token = itoken.consume()
        if token in {"true", "false"}:
            arg1 = Const(token == "true", token, "Bool", src=itoken.src, coords=tk_coords)
        elif "." in token or (token[0] >= '0' and token[0] <= '9'):
            arg1 = parse_num_const(token, tk_coords, itoken)
        elif token in {'"', '"""'}:
            arg1 = parse_str_literal("", tk_coords[0], itoken, token == '"""')
        elif token == '`':
            arg1 = parse_char_literal(token, tk_coords, itoken)
        elif itoken.peak() in {'"', '"""'} and tk_coords[1] == itoken.peak_coords()[0]:
            multiline = itoken.consume() == '"""'
            if not re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
                raise ParsingError(f"Invalid prefix name '{token}'", itoken)
            arg1 = parse_str_literal(token, tk_coords[0], itoken, multiline)
        elif token == ":":
            arg1 = None
            itoken.i -= 1
        elif token[-1] == ":":
            raise ParsingError("Operator slices require a start.", itoken)
        elif token in operator_precedence:
            itoken.consume(-1)
            raise ParsingError("Expected operand found operator", itoken)
        else:
            arg1 = Id(token, src=itoken.src, coords=tk_coords)

    return arg1

def parse_operator(arg1, itoken, precedence, op_prec):
    op_coords = itoken.peak_coords()
    op = itoken.consume()  # assumes valid operator
    if op == "(":
        ret_args, kwargs, inject_args = parse_args_kwargs(itoken, accept_inject=True, is_toplevel=False)
        itoken.expect(")")
        fcall = FuncCall(arg1, ret_args, src=itoken.src, coords=arg1.coords)
        fcall.kwargs = kwargs
        fcall.inject_args = inject_args
        arg1 = fcall
    elif op == "'":
        f_coords = itoken.peak_coords()
        fname_node = parse_expression(itoken, precedence+1, op_prec=op_prec)
        fcall = FuncCall(
            fname_node,
            [arg1], src=itoken.src, coords=f_coords)
        if itoken.check("("):
            ret_args, kwargs, inject_args = parse_args_kwargs(itoken, accept_inject=True, is_toplevel=False)
            fcall.args.extend(ret_args)
            fcall.kwargs = kwargs
            fcall.inject_args = inject_args
            itoken.expect(")")
        arg1 = fcall
    elif op == "\\":
        f_coords = itoken.peak_coords()
        fname = itoken.consume()
        fcall = FuncCall(
            Id(fname, src=itoken.src, coords=f_coords),
            [arg1], src=itoken.src, coords=f_coords
        )
        arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
        fcall.args.append(arg2)
        arg1 = fcall
    elif op == "[":
        itoken.skip_empty_lines()
        ret_args, kwargs = parse_args_kwargs(itoken, is_toplevel=False)
        itoken.expect("]")
        if len(ret_args) == 1 and len(kwargs) == 0 and isinstance(ret_args[0], ForExpr):
            # list comprehension with an explicit type
            arg1 = ListComprehension(
                list_type=arg1,
                loop=ret_args[0], src=itoken.src, coords=op_coords
            )
        else:
            arg1 = Select(
                arg1, Args(ret_args, kwargs), src=itoken.src, coords=op_coords
            )
    elif op == "~":
        if isinstance(arg1, AttachTags):
            # parse right to left
            arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
            arg1.tags.args[0] = AttachTags(
                arg1.tags.args[0],
                TagList([arg2]),
                src=itoken.src, coords=op_coords
            )
        elif itoken.check("["):
            ret_args, kwargs = parse_args_kwargs(itoken, is_taglist=True)
            itoken.expect("]")
            attach_tags = AttachTags(
                arg1, TagList(ret_args, kwargs), src=itoken.src, coords=op_coords
            )
            arg1 = attach_tags
        else:
            arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
            attach_tags = AttachTags(
                arg1, TagList([arg2]), src=itoken.src, coords=op_coords
            )
            arg1 = attach_tags
    elif op == "{":
        arg1 = parse_struct_literal(itoken, arg1)
        if itoken.peak() == "~":
            raise ParsingError(
                "Only simple positional tags can be chained. "
                "Please be explicit and put the tags in square brackets.",
                itoken
            )
    return arg1

def parse_num_const(token: str, tk_coords, itoken):
    itoken.i -= 1  # for better error messages
    suffix_map = {
        "f": "Float", "d": "Double",
        "l": "Long", "ul": "Ulong", "u": "Uint",
        "s": "Short", "us": "Ushort",
        "b": "Byte", "ub": "Ubyte",
        "z": "Size"
    }

    if "." in token:
        suffix = ""
        while token[-1].isalpha():
            suffix = token[-1] + suffix
            token = token[:-1]

        type = "Float"
        value_str = token + 'f'
        if suffix == 'd':
            value_str = token
            type = "Double"
        elif suffix not in {'', 'f'}:
            raise ParsingError(f"Invalid suffix for floating point num '{suffix}'", itoken)
        try:
            val = float(token)
        except:
            raise ParsingError("Invalid floating point literal", itoken)
        res = Const(val, value_str, type, src=itoken.src, coords=tk_coords)
    else:
        base = 10
        num_str = ""
        suffix = ""
        bracket_idx = None
        if token.startswith("0"):
            bracket_idx = token.find('(')
            if bracket_idx > 0:
                num_str = token[1:bracket_idx]
                closing_idx = token.find(')', bracket_idx)
                if closing_idx < 0:
                    raise ParsingError("Ill-formatted number literal", itoken)
                if closing_idx - bracket_idx > 1:
                    base = parse_int(token[bracket_idx+1:closing_idx], 10, itoken)
                else:
                    base = 16 if token.startswith("0x") else 8
                    if base == 16:
                        num_str = num_str[1:]
                suffix = token[closing_idx+1:]
            else:
                base = 16 if token.startswith("0x") else 8
                for i_suffix in suffix_map.keys():
                    if token.lower().endswith(i_suffix):
                        suffix = i_suffix if len(suffix) < len(i_suffix) else suffix
                if suffix in {'f', 'd', 'b'} and base == 16:
                    suffix = ""
                prefix_len = 2 if token.startswith("0x") else 1
                num_str = token[prefix_len:len(token)-len(suffix)]
                if len(num_str) == 0:
                    num_str = "0"
                    base = 10
        else:
            base = 10
            for i_suffix in suffix_map.keys():
                if token.lower().endswith(i_suffix):
                    suffix = i_suffix if len(suffix) < len(i_suffix) else suffix
            num_str = token[:len(token)-len(suffix)]

        res = Const(
            parse_int(num_str, base, itoken),
            num_str,
            "Int", src=itoken.src, coords=tk_coords
        )
        res.value_str = res.value_str.replace("_", "")

        if base not in {10, 16, 8}:
            res.value_str = str(res.value)
        elif base == 16: res.value_str = "0x" + res.value_str
        elif base == 8: res.value_str = "0" + res.value_str

        if res.value not in {0, 1}:
            if suffix == "l": res.value_str += "ll"
            elif suffix == "ul": res.value_str += "ull"
            elif suffix == "u" and base != 10: res.value_str += "u"
        if suffix in suffix_map:
            res.type = suffix_map[suffix]
        elif suffix != "":
            raise ParsingError("Unknown number suffix", itoken)

    itoken.i += 1
    return res

def parse_int(str: str, base, token):
    if base < 2 or base > 36:
        raise ParsingError("Invalid base", token)
    try:
        return int(str, base)
    except ValueError:
        raise ParsingError(f"Invalid character in base-{base} number", token)

def parse_var_decl(itoken, name_token, precedence, op_prec):
    decl = VarDecl(src=itoken.src, coords=name_token.coords if name_token else itoken.peak_coords())
    if isinstance(name_token, CallerContextExpr):
        decl.name = name_token.arg.name
        decl.is_callerContext = True
    elif not isinstance(name_token, Empty) and name_token is not None:
        decl.name = name_token.name
    else:
        decl.coords = itoken.peak_coords()

    if itoken.check("mut"):
        decl.mutable = True
        decl.explicit_mutable = True
    elif itoken.peak() in {"out", "inout", "outin"}:
        raise ParsingError(f"'{itoken.peak()}' is a reserved keyword", itoken)
    elif itoken.check("pseudo"):
        decl.is_pseudo = True

    if itoken.peak() in var_qualifiers:
        raise ParsingError("Only one variable qualifier is allowed.", itoken)

    if not is_end_of_expr(itoken) and itoken.peak() != "=":
        decl.type = expr_to_type(
            parse_expression(itoken, precedence+1, op_prec=op_prec)
        )
    if "=" in op_prec and itoken.check("="):
        decl.value = parse_expression(itoken, precedence+1, op_prec=op_prec)

    return decl

def is_end_of_expr(itoken):
    return itoken.peak() in {";", ")", "]", "}", ","}

def parse_if(itoken):
    if_coords = itoken.peak_coords()
    token_name = itoken.consume()  # "if"/"elif" token
    if_expr = IfExpr(src=itoken.src, coords=if_coords)
    if itoken.peak() != "(":
        name_coords = itoken.peak_coords()
        if_expr.name = Id(
            itoken.consume(), src=itoken.src, coords=name_coords
        )
    itoken.expect("(", msg=f"Missing conditional expression for '{token_name}'")
    if_expr.cond = parse_expression(itoken)
    itoken.expect(")", msg="Missing closing bracket")
    if_expr.block = parse_block(itoken, accept_early_return=True)

    if isinstance(if_expr.block.body, list) and itoken.peak() == "if":
        raise ParsingError(
            "Cannot put an if on the same line as another if. Did you mean `elif`?",
            itoken
        )

    itoken.skip_empty_lines()
    if itoken.check("else"):
        if_expr.else_node = parse_block(itoken, accept_early_return=True)
    elif itoken.peak() == "elif":
        if_expr.else_node = parse_if(itoken)

    return if_expr


def parse_while(itoken):
    while_coords = itoken.peak_coords()
    itoken.consume()  # "while" token
    while_expr = WhileExpr(src=itoken.src, coords=while_coords)
    if itoken.peak() != "(":
        name_coords = itoken.peak_coords()
        while_expr.name = Id(
            itoken.consume(), src=itoken.src, coords=name_coords
        )
    itoken.expect("(")
    while_expr.cond = parse_expression(itoken)
    itoken.expect(")", msg="Missing closing bracket")

    while_expr.block = parse_block(itoken)

    if itoken.check("else"):
        while_expr.else_node = parse_block(itoken)

    return while_expr

def parse_do_while(itoken):
    while_coords = itoken.peak_coords()
    itoken.consume()  # "do" token
    dowhile_expr = DoWhileExpr(src=itoken.src, coords=while_coords)

    dowhile_expr.block = parse_block(itoken)

    itoken.expect("while")
    if itoken.peak() != "(":
        name_coords = itoken.peak_coords()
        dowhile_expr.name = Id(
            itoken.consume(), src=itoken.src, coords=name_coords
        )
    itoken.expect("(")
    dowhile_expr.cond = parse_expression(itoken)
    itoken.expect(")", msg="Missing closing bracket")

    if itoken.check("else"):
        dowhile_expr.else_node = parse_block(itoken)
    return dowhile_expr


def parse_for(itoken):
    for_coords = itoken.peak_coords()
    itoken.consume()  # "for" token
    for_expr = ForExpr(src=itoken.src, coords=for_coords)
    if itoken.peak() != "(":
        name_coords = itoken.peak_coords()
        for_expr.name = Id(
            itoken.consume(), src=itoken.src, coords=name_coords
        )
    itoken.expect("(")
    for_expr.over = parse_expr_list(itoken)
    itoken.expect(")", msg="Missing closing bracket")

    for_expr.block = parse_block(itoken)

    if itoken.check("else"):
        for_expr.else_node = parse_block(itoken)
    return for_expr


def parse_break_continue(itoken):
    node_coords = itoken.peak_coords()
    if itoken.check("break"):
        res = Break(src=itoken.src, coords=node_coords)
    else:
        assert itoken.check("continue")
        res = Continue(src=itoken.src, coords=node_coords)
    if not is_end_of_expr(itoken):
        res.loop_name = parse_expression(itoken, is_toplevel=False)
    return res


def expr_to_type(expr):
    return expr

def expr_to_param(expr, itoken):
    if isinstance(expr, VarDecl):
        return expr
    if (isinstance(expr, SliceExpr) and expr.step is None and expr.end is not None):
        decl = VarDecl(src=expr.src, coords=expr.coords, is_param=True)
        if expr.start is not None:
            if not isinstance(expr.start, Id):
                raise ParsingError("Variable name must be an identifier", itoken)
            decl.name = expr.start.name
        decl.type = expr_to_type(expr.end)
        return decl
    else:
        raise ParsingError("Invalid parameter", itoken)

def parse_struct_literal(itoken, struct_expr):
    start_coords = itoken.peak_coords()
    args = parse_expr_list(itoken, ignore_eols=True, accept_inject=False)
    itoken.expect("}")
    end_coords = itoken.peak_coords()
    if isinstance(struct_expr, ArrayType):
        return ArrayLit(elems=args, base=struct_expr, src=itoken.src, coords=[start_coords[0], end_coords[1]])
    else:
        return StructLiteral(
            struct_expr, args, src=itoken.src, coords=[start_coords[0], end_coords[1]]
        )

def parse_str_literal(prefix, prefix_start, itoken, multiline):
    res = StrLiteral(prefix=prefix, src=itoken.src)
    skip_leading = -1
    itoken.i -= 1 # move back in order to get the " coords
    part_start = itoken.peak_coords()[1]
    itoken.i += 1
    part_end = part_start
    while itoken.peak() != '"':
        part_end = itoken.peak_coords()[0]

        if itoken.check("{"):
            if part_start < part_end:
                lit = itoken.src.code[part_start:part_end]
                lit, skip_leading = check_escaped_newline(lit, multiline, skip_leading)
                res.parts.append(Const(lit))
            else:
                skip_leading = 0

            if not itoken.check("#"):
                is_introspective = itoken.check("=")
                args_coords_start = itoken.peak_coords()[0]
                args, kwargs = parse_args_kwargs(itoken)
                args_coords_end = itoken.peak_coords()[0]
                res.parts.append(Args(args, kwargs, is_introspective=is_introspective,
                                    src=itoken.src,
                                    coords=(args_coords_start, args_coords_end)))
            else:
                # calling an external command probably
                itoken.expect("!")
                cmds = []
                expr_start = itoken.peak_coords()[0]
                cmd_start = 0
                cmd_end = 0
                while itoken.peak() != "}":
                    if cmd_end != itoken.peak_coords()[0]:
                        if cmd_start != cmd_end:
                            cmds.append(itoken.src.code[cmd_start:cmd_end])
                        cmd_start = itoken.peak_coords()[0]
                    cmd_end = itoken.peak_coords()[1]
                    itoken.consume()
                if cmd_start != cmd_end:
                    cmds.append(itoken.src.code[cmd_start:cmd_end])
                if len(cmds) == 0:
                    raise ParsingError("Missing command", itoken)
                res.parts.append(
                    ExternalCommand(
                        cmds,
                        src=itoken.src,
                        coords=(expr_start, itoken.peak_coords()[0])
                    )
                )

            part_start = itoken.peak_coords()[0] + 1
            itoken.expect("}")
        elif itoken.peak() == '"""':
            raise ParsingError("Multiline strings are terminated with one double quotation mark", itoken)
        else:
            itoken.check("\\")
            itoken.consume()

    part_end = itoken.peak_coords()[0]
    itoken.expect('"')

    if part_start < part_end:
        lit = itoken.src.code[part_start:part_end]
        lit, _ = check_escaped_newline(lit, multiline, skip_leading)
        res.parts.append(Const(lit, src=itoken.src, coords=itoken.peak_coords()))

    res.coords = (prefix_start, part_end+1)
    full_str_start = prefix_start + len(prefix) + (1 if not multiline else 3)
    res.full_str = itoken.src.code[full_str_start:part_end]
    return res

def check_escaped_newline(lit, multiline, skip_leading):
    res = []
    i = 0
    if multiline and skip_leading < 0:
        if i < len(lit) and lit[i] == "\n":
            i += 1
        skip_leading = 0
        while i < len(lit) and lit[i] == " ":
            i += 1
            skip_leading += 1
    start = i
    while i < len(lit):
        if i+1 < len(lit) and lit[i] == "\\" and lit[i+1] == "\n":
            res.append(lit[start:i])
            i += 2
            while i < len(lit) and lit[i] == " ":
                i += 1
            start = i
        elif lit[i] == "\n" and multiline and skip_leading > 0:
            i += 1
            j = 0
            while i + j < len(lit) and j < skip_leading and lit[i+j] == " ":
                j += 1
            if j == skip_leading or (i+j) >= len(lit):
                res.append(lit[start:i])
                i += j
                start = i
        else:
            i += 1
    if start < len(lit):
        res.append(lit[start:])
    return "".join(res), skip_leading

def parse_char_literal(token, tk_coords, itoken):
    start = tk_coords[1]
    while itoken.peak() != '`':
        itoken.check("\\")
        itoken.consume()
    end = itoken.peak_coords()[0]
    assert itoken.check("`")

    lit = itoken.src.code[start:end]
    return Const(lit, lit, type="Char", src=itoken.src, coords=tk_coords)

def parse_args_kwargs(itoken, is_toplevel=True, is_taglist=False, accept_inject=False, accept_ml_comments=True):
    positional, named = [], {}
    args = parse_expr_list(itoken, ignore_eols=True, is_toplevel=is_toplevel,
                           is_taglist=is_taglist, accept_inject=accept_inject,
                           accept_ml_comments=accept_ml_comments)
    if accept_inject:
        args, inject_args = args
    for expr in args:
        is_named = (
            isinstance(expr, BinExpr) and expr.op == "=" and
            isinstance(expr.arg1, Id)
        )
        if is_named:
            named[expr.arg1.name] = expr.arg2
        else:
            positional.append(expr)
    if accept_inject:
        return positional, named, inject_args
    else:
        return positional, named


def parse_expr_list(itoken, ignore_eols=True, is_toplevel=True, is_taglist=False, accept_inject=False,
                    accept_ml_comments=True):
    res = []
    inject = None
    if ignore_eols: itoken.skip_empty_lines()
    term_symbols = {")", "]", "}", ";"}
    if not accept_ml_comments: term_symbols.add(";;")
    while itoken.peak() not in term_symbols:
        if inject is not None:
            raise ParsingError("Cannot have any arguments after ...", itoken)
        calltime_coords = itoken.peak_coords()
        if itoken.peak() != "...":
            if itoken.peak() == "<<":
                raise ParsingError("Guards are allowed only on new lines", itoken)
            comment_node = None
            if itoken.check(";;"):
                comment_node = parse_ml_comment(itoken)
                if is_end_of_expr(itoken):
                    raise ParsingError("Doc comment is not followed by anything", itoken)
            introspective = itoken.check("=")
            if ignore_eols: itoken.skip_empty_lines()
            expr = parse_expression(itoken, is_toplevel=is_toplevel)
            if introspective:
                if not isinstance(expr, Id):
                    raise ParsingError("Only simply identifiers can use the leading '=' shortcut")
                expr = BinExpr(
                    expr, expr, op="=", src=expr.src, coords=expr.coords
                )
            if comment_node is not None:
                expr.comment = comment_node.comment
            res.append(expr)
        else:
            if accept_inject:
                inject = ScopeArgsInject(src=itoken.src, coords=itoken.peak_coords())
                itoken.consume()
            else:
                raise ParsingError("... Can appear only at the end of an argument list", itoken)
        if ignore_eols: itoken.skip_empty_lines()
        has_comma = False
        if accept_ml_comments and itoken.check(";;"):
            comment_node = parse_ml_comment(itoken)
            if len(expr.comment) > 0: expr.comment += "\n"
            expr.comment += comment_node.comment
        if itoken.peak() not in term_symbols:
            itoken.expect(",")
            has_comma = True
        if accept_ml_comments and itoken.check(";;"):
            comment_node = parse_ml_comment(itoken)
            if len(expr.comment) > 0: expr.comment += "\n"
            expr.comment += comment_node.comment
        if ignore_eols: itoken.skip_empty_lines()
    if accept_inject:
        return res, inject
    else:
        return res

def parse_body(itoken):
    itoken.expect("{")
    body = parse_stmt_list(itoken)
    itoken.expect("}")
    return body

def parse_stmt_list(itoken: TokenIter):
    body = []
    attach_comment_to_prev = False
    comment_node = None
    itoken.skip_empty_lines()
    while itoken.has_more() and itoken.peak() != "}":
        visibility = None
        if itoken.peak() in visibilityMap:
            vis_idx = itoken.i
            visibility = visibilityMap[itoken.consume()]
            if itoken.peak() == "\n":
                raise ParsingError("Visibility marker cannot stand on its own", itoken)

        if itoken.peak() == "import":
            imports = parse_import(itoken)
            if len(imports) > 1:
                body.extend(imports[0:-1])
            node = imports[-1]
        elif itoken.check("#"):
            node = parse_sl_comment(itoken)
        elif itoken.check(";;"):
            node = parse_ml_comment(itoken)
        elif itoken.peak() == "def":
            node = parse_def(itoken)
        elif itoken.peak() == "struct":
            node = parse_struct(itoken)
        elif itoken.check("from"):
            raise ParsingError(
                "The correct syntax to import a library is 'import <libname>'",
                itoken
            )
        elif itoken.peak() == "return":
            node = parse_return(itoken)
            itoken.expect_semicolon()
        elif itoken.peak() == "error":
            node = parse_error(itoken)
            itoken.expect_semicolon()
        elif itoken.peak() == "#":
            itoken.consume()
            node = parse_sl_comment(itoken)
        elif itoken.peak() == ";;":
            itoken.consume()
            node = parse_ml_comment(itoken)
        elif itoken.peak() == "def":
            raise ParsingError("Functions in functions are not allowed", itoken)
        elif itoken.peak() == "struct":
            raise ParsingError("Structs in functions are not allowed", itoken)
        elif itoken.peak() == ";":
            raise ParsingError(
                "Empty statements are not allowed. Please remove the semicolon.",
                itoken
            )
        else:
            first_expr_token_idx = itoken.i
            node = parse_expression(itoken)
            if not itoken.check_semicolon() and should_have_semicolon_after_expr(node):
                if itoken.peak() == "\n":
                    raise ParsingError("Missing ';' at end of expression", itoken)
                notes = []
                if fuzzy_cmp(itoken.tokens[first_expr_token_idx], "struct") > .8:
                    notes=[("Did you mean 'struct'?", first_expr_token_idx)]
                if not any(c.isalnum() for c in itoken.peak()) and itoken.peak() not in {"}", ")", "]"}:
                    raise ParsingError(
                        "Malformed expression. Looks like invalid operator.",
                        itoken, notes=notes
                    )
                raise ParsingError(
                    "Malformed expression. Maybe missing operator or semicolon.",
                    itoken, notes=notes
                )

        if visibility is not None and hasattr(node, 'visibility'):
            node.visibility = visibility
        elif visibility is not None:
            itoken.i = vis_idx
            raise ParsingError(
                "Only func defs, structs, and global vars can have visibility", itoken
            )

        if not isinstance(node, Comment):
            if comment_node is not None:
                node.comment = comment_node.comment
            body.append(node)
            comment_node = None
        else:
            if comment_node is not None:
                body.append(comment_node)
                comment_node = None
            if attach_comment_to_prev and len(body) > 0:
                body[-1].comment = node.comment
                comment_node = None
            else:
                comment_node = node
        lines_skipped = itoken.skip_empty_lines()
        attach_comment_to_prev = lines_skipped == 0

    if comment_node is not None:
        body.append(comment_node)

    return body

def parse_return(itoken):
    coords = itoken.peak_coords()
    assert itoken.check("return")
    expr = parse_expr_list(itoken, ignore_eols=True, is_toplevel=False, accept_ml_comments=False)
    if len(expr) == 1:
        expr = expr[0]
    node = Return(expr, src=itoken.src, coords=coords)
    return node

def parse_error(itoken):
    coords = itoken.peak_coords()
    assert itoken.check("error")
    exprs = parse_expr_list(itoken, ignore_eols=True, is_toplevel=False, accept_ml_comments=False)
    if len(exprs) == 0:
        raise ParsingError("Missing value for \"error\" statement", itoken)
    if len(exprs) > 1:
        raise ParsingError("Only one error can be issued", itoken)
    node = Error(exprs[0], src=itoken.src, coords=coords)
    return node

def parse_error_block(itoken):
    res = ErrorBlock(src=itoken.src, coords=itoken.peak_coords())
    assert itoken.peak() == "||"
    params = parse_params(itoken, is_error_block=True)
    if len(params) > 1:
        raise ParsingError("Error blocks can have only one argument", itoken)
    res.param = params[0] if len(params) > 0 else None
    res.coords = (res.coords[0], itoken.peak_coords()[0])

    block = parse_block(itoken)
    res.returns = block.returns
    res.body = block.body
    return res

def fuzzy_cmp(str1, str2):
    return SM(None, str1, str2).ratio()

def should_have_semicolon_after_expr(node):
    if isinstance(node, ErrorBlock):
        return False
    if not isinstance(node, (IfExpr, ForExpr, WhileExpr)):
        return True
    return node.block.is_embedded and should_have_semicolon_after_expr(node.block.body)

def parse_tags(itoken):
    res = TagList()
    if itoken.check("["):
        args, kwargs = parse_args_kwargs(itoken)
        res.args = args
        res.kwargs = kwargs
        itoken.expect("]")
    else:
        # this new map is to limit the parsing to the first opening bracket (
        toplevel_precedence_map = {**operator_precedence}
        del toplevel_precedence_map["("]
        del toplevel_precedence_map["{"]
        del toplevel_precedence_map["~"]

        tag = parse_expression(itoken, op_prec=toplevel_precedence_map)

        if itoken.peak() in "~":
            raise ParsingError(
                "These long chains of tags get very ambiguous. Please be explicit and seprate the tags in square brackets.",
                itoken
            )

        res.args = [tag]
    return res

def parse_struct(itoken: TokenIter):
    visibility = PackageVisibility
    if itoken.peak() in visibilityMap:
        visibility = visibilityMap[itoken.consume()]
    itoken.expect("struct")
    if itoken.peak() in {"-", "+", "*"}:
        raise ParsingError("Visibility marker goes before 'struct'", itoken)
    coords = itoken.peak_coords()
    name = itoken.consume()
    node = StructDef(name=name, src=itoken.src, coords=coords, visibility=visibility)
    if itoken.check("~"):
        node.tags = parse_tags(itoken)
    itoken.expect("{")
    # TODO should that be here
    itoken.skip_empty_lines()
    comment = None
    while itoken.peak() != "}":
        if itoken.check(";;"):
            comment = parse_ml_comment(itoken).comment
            itoken.skip_empty_lines()
        field = parse_expression(itoken, is_struct=True)
        if not isinstance(field, VarDecl):
            raise ParsingError("Unexpected expression in struct definition. Only variable declarations are valid.", itoken)
        node.fields.append(field)
        itoken.expect_semicolon(msg="Missing ';' at end of field")

        if itoken.check(";;"):
            comment = parse_ml_comment(itoken).comment
        if comment:
            field.comment = comment

        comment = None
        itoken.skip_empty_lines()
    itoken.expect("}")
    if itoken.peak() == ";":
        raise ParsingError("';' at end of struct def is not needed", itoken)
    return node
