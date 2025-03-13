import re
from difflib import SequenceMatcher as SM
from xyc.tokenizer import split_tokens
from xyc.ast import *


class TokenIter:
    def __init__(self, tokens, token_pos, src):
        self.tokens = tokens
        self.token_pos = token_pos
        self.i = 0
        self.src = src

    def has_more(self):
        return self.i < len(self.tokens)
    
    def peak(self):
        if not self.has_more():
            return ""
        return self.tokens[self.i]
    
    def peakn(self, n: int):
        if self.i + n >= len(self.tokens):
            raise ParsingError("Unexpected end of file", self)
        return self.tokens[self.i:self.i+n]
    
    def peak_coords(self):
        if not self.has_more():
            return (len(self.src.code), len(self.src.code))
        return (
            self.token_pos[self.i],
            self.token_pos[self.i] + len(self.peak())
        )
    
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
    while not itoken.peak_eol() and itoken.peak() == ".":
        itoken.consume()
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

    return Import(
        lib=lib, in_name=in_name, tags=tags, src=itoken.src, coords=coords
    )

def parse_sl_comment(itoken):
    comment_start = itoken.token_pos[itoken.i-1]+1
    itoken.skip_until("\n")
    comment_end = itoken.token_pos[itoken.i-1]

    comment = itoken.src.code[comment_start:comment_end]
    return Comment(
        comment=comment,
        src=itoken.src, coords=[comment_start-1, comment_start]
    )

def parse_ml_comment(itoken):
    comment_start = itoken.token_pos[itoken.i-1]
    itoken.skip_until("\n")
    while itoken.check(";;"):
        itoken.skip_until("\n")
    comment_end = itoken.token_pos[itoken.i-1]

    comment = itoken.src.code[comment_start:comment_end]
    return Comment(comment=comment, src=itoken.src,
                   coords=[comment_start, comment_start+2])

def parse_def(itoken: TokenIter):
    visibility = PackageVisibility
    if itoken.peak() in {"-", "+", "*"}:
        visibility = visibilityMap[itoken.consume()]
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

    itoken.check("=")
    value = parse_block(itoken)
    node.returns = value.returns
    node.etype = value.etype
    node.in_guards = value.in_guards
    node.out_guards = value.out_guards
    node.body = value.body

    if isinstance(node.body, list):
        if itoken.has_more() and itoken.peak() == ";":
            raise ParsingError(
                "Function definitions don't require a terminating semicolon.",
                itoken
            )
    else:
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

def parse_block(itoken):
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

        if itoken.check("||"):
            block.etype = parse_toplevel_type_expr(itoken)

    for expr in args:
        expr = expr_to_type(expr)
        if isinstance(expr, VarDecl):
            expr.mutable = True
            block.returns.append(expr)
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
    elif itoken.peak() != "{":
        block.body = parse_expression(itoken)
    else:
        block.body = parse_body(itoken)

    return block

def parse_params(itoken):
    res = []
    itoken.expect("(", msg="Missing param list")
    itoken.skip_empty_lines()
    while itoken.peak() not in {")", "]", "}", ";"}:
        param = parse_expression(itoken)
        if not isinstance(param, VarDecl):
            raise ParsingError("Invalid parameter. Proper syntax is 'name : Type = value'", itoken)
        
        if not itoken.check(","):
            # no , - better be the last param
            itoken.skip_empty_lines()
            if itoken.peak() != ")":
                raise ParsingError("Missing comma at end of parameter", itoken)

        if param.name is None:
            param.is_pseudo = True

        if not param.explicit_mutable:
            param.mutable = False
        param.is_param = True
        res.append(param)

        itoken.skip_empty_lines()

    itoken.skip_empty_lines()
    itoken.expect(")")
    return res
    
def parse_toplevel_type_expr(itoken):
    # this new map is here purely to provide better error messages in cases like
    # def func() -> MyType{} {...}
    # or
    # def func() -> Type1 || Type2 || Type3 {...}
    toplevel_precedence_map = {**operator_precedence}
    del toplevel_precedence_map["||"]
    del toplevel_precedence_map["{"]
    del toplevel_precedence_map["="]

    return parse_expression(itoken, op_prec=toplevel_precedence_map)

# ref is a reserved keyword
var_qualifiers = {"mut", "in", "out", "inout", "outin", "pseudo", "ref"}

operator_precedence = {
    "^": 12, "unary[": 12, "unary'": 12,
    "~": 11, "++" : 11, "--": 11, ".": 11, "(": 11, "[": 11, "{": 11, "'": 11, "..": 11, "@": 11,
    "unary+": 10, "unary-": 10, "!": 10, "&": 10, '%': 10,
    "\\": 9,
    "*": 8, "/": 8,
    "+": 7, "-": 7,
    "<": 6, "<=": 6, ">=": 6, ">": 6, ":": 6, "+:": 6, "*:": 6, "-:": 6,
    "==": 5, "!=": 5, "in": 5,
    "&": 4,
    "|": 3, "||": 3,
    "=": 2, '+=': 2, '-=': 2, "|=": 2, '*=': 2, '/=': 2, ".=": 2, "=<": 2, "=>": 2,
}
MIN_PRECEDENCE=2
UNARY_PRECEDENCE=10
MAX_PRECEDENCE=12

@dataclass
class Empty(Node):
    pass

def parse_expression(
        itoken, precedence=MIN_PRECEDENCE, is_struct=False,
        op_prec=operator_precedence, is_toplevel=True
):
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

    if precedence >= MAX_PRECEDENCE and itoken.check("("):
        # bracketed expression or func type
        bracketed_exprs = parse_expr_list(itoken, is_toplevel=False)
        itoken.expect(")", msg="Missing closing bracket")
        if itoken.peak() != "->":
            # bracketed expression
            if len(bracketed_exprs) > 1:
                raise ParsingError("',' is used only to separate arguments or params not as operator", itoken)
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

            if itoken.check("||"):
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
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "@":
        coords = itoken.peak_coords()
        assert itoken.check('@')
        if itoken.peak() == "for":
            # list comprehension
            for_expr = parse_for(itoken)
            arg1 = ListComprehension(loop=for_expr, src=itoken.src, coords=coords)
        else:
            # array literal
            itoken.expect('{', "Array literals are constructed using the @{elems,...} syntax")
            itoken.skip_empty_lines()
            ret_args = parse_expr_list(itoken)
            itoken.expect("}", msg="Missing closing bracket")
            arg1 = ArrayLit(ret_args, src=itoken.src, coords=coords)
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "[":
        # Indexing without a base i.e. derefing
        coords = itoken.peak_coords()
        itoken.consume() # [
        itoken.skip_empty_lines()
        ret_args, kwargs = parse_args_kwargs(itoken, is_toplevel=False)
        itoken.expect("]", msg="Missing closing bracket")
        arg1 = Select(base=None, args=Args(ret_args, kwargs), src=itoken.src, coords=coords)
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "'":
        itoken.consume()
        f_coords = itoken.peak_coords()
        fname = parse_expression(itoken, precedence+1, op_prec=op_prec)
        fcall = FuncCall(
            fname, src=itoken.src, coords=f_coords,
            inject_context=True
        )
        if itoken.check("("):
            ret_args, kwargs, inject_args = parse_args_kwargs(itoken, accept_inject=True)
            fcall.args.extend(ret_args)
            fcall.kwargs = kwargs
            fcall.inject_args = inject_args
            itoken.expect(")")
        arg1 = fcall
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "{":
        # announomous struct literal
        itoken.consume()
        arg1 = parse_struct_literal(itoken, None)
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "in":
        arg1 = parse_var_decl(itoken, Empty(), MIN_PRECEDENCE, op_prec)
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "$":
        arg1 = parse_func_select(itoken)
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "^":
        coords = itoken.peak_coords()
        itoken.consume()
        arg1 = parse_expression(itoken, precedence+1, op_prec=op_prec)
        arg1 = CallerContextExpr(arg1, src=itoken.src, coords=coords)
    elif precedence >= MAX_PRECEDENCE:
        tk_coords = itoken.peak_coords()
        token = itoken.consume()
        if token in {"true", "false"}:
            arg1 = Const(token == "true", token, "Bool")
        elif "." in token or (token[0] >= '0' and token[0] <= '9'):
            arg1 = parse_num_const(token, tk_coords, itoken)
        elif token == '"':
            arg1 = parse_str_literal("", tk_coords[0], itoken)
        elif itoken.peak() == '"' and tk_coords[1] == itoken.peak_coords()[0]:
            if not re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
                raise ParsingError(f"Invalid prefix Name", itoken)
            itoken.expect('"')
            arg1 = parse_str_literal(token, tk_coords[0], itoken)
        elif token == ":":
            arg1 = Empty(src=itoken.src, coords=tk_coords)
            itoken.i -= 1
        elif token[-1] == ":":
            raise ParsingError("Operator slices require a start.", itoken)
        elif token in operator_precedence:
            itoken.consume(-1)
            raise ParsingError("Expected operand found operator", itoken)
        else:
            arg1 = Id(token, src=itoken.src, coords=tk_coords)
    elif precedence == UNARY_PRECEDENCE and itoken.peak() in {"+", "-", "!", "&", "%"}:
        coords = itoken.peak_coords()
        op = itoken.consume()
        arg1 = parse_expression(itoken, precedence+1, op_prec=op_prec)
        if op != '!' and isinstance(arg1, Const) and arg1.type != "str":
            if op == '-':
                arg1.value = -arg1.value
                arg1.value_str = f'-{arg1.value_str}'
        else:
            arg1 = UnaryExpr(arg=arg1, op=op, src=itoken.src, coords=coords)
        return arg1
    elif precedence == UNARY_PRECEDENCE and itoken.peak() in {"++", "--"}:
            raise ParsingError("Prefix increment and decrement are not supported. "
                            "More infor at TBD", itoken)
    elif itoken.peak() == "." and precedence == op_prec["."]:
        arg1 = None  # unary "."
    else:
        if is_end_of_expr(itoken):
            raise ParsingError("Unexpected end of expression.", itoken)
        arg1 = parse_expression(itoken, precedence+1, op_prec=op_prec)

    converted_to_slice = False
    op = itoken.peak()
    op_coords = itoken.peak_coords()
    while op in op_prec and op_prec[op] == precedence:
        itoken.consume()  # operator
        if op == "(":
            ret_args, kwargs, inject_args = parse_args_kwargs(itoken, accept_inject=True)
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
                ret_args, kwargs, inject_args = parse_args_kwargs(itoken, accept_inject=True)
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
        elif op == "@":
            if itoken.peak() == "for":
                # list comprehension
                for_expr = parse_for(itoken)
                arg1 = ListComprehension(list_type=arg1, loop=for_expr, src=itoken.src, coords=op_coords)
            else:
                # array literal
                itoken.expect('{', "Array literals are constructed using the @{elems,...} syntax")
                itoken.skip_empty_lines()
                ret_args = parse_expr_list(itoken)
                itoken.expect("}", msg="Missing closing bracket")
                arg1 = ArrayLit(ret_args, base=expr_to_type(arg1), src=itoken.src, coords=op_coords)
        elif op[-1] == ":":
            if op == ":" and itoken.peak() in var_qualifiers:
                # it's a var decl
                arg1 = parse_var_decl(itoken, arg1, precedence, op_prec)
            elif converted_to_slice:
                if arg1.step is not None:
                    raise ParsingError(
                        "Slices can have only 3 components - start:end:step",
                        itoken
                    )
                if not is_end_of_expr(itoken):
                    if op != ":":
                        raise ParsingError(
                            "Operator slices make sense only between the "
                            "start and end expressions of a slice", itoken)
                    arg1.step = parse_expression(itoken, precedence+1, op_prec=op_prec)
            else:
                converted_to_slice = True
                arg2 = Empty()
                if not is_end_of_expr(itoken):
                    arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
                sliceop = SliceExpr(src=itoken.src, coords=arg1.coords)
                if op != ":":
                    sliceop.op = op[:-1]

                if not isinstance(arg1, Empty):
                    sliceop.start = arg1
                elif sliceop.op is not None:
                    raise ParsingError("Operator slices require both start and end expressions", itoken)

                if not isinstance(arg2, Empty):
                    sliceop.end = arg2
                elif sliceop.op is not None:
                    raise ParsingError("Operator slices require both start and end expressions", itoken)

                arg1 = sliceop
        elif op in {"=", "=<"} and isinstance(arg1, SliceExpr):
            if isinstance(arg1.start, CallerContextExpr):
                raise ParsingError("Caller context parameters cannot have default values", itoken)
            decl = VarDecl(name=arg1.start.name, src=itoken.src, coords=op_coords, is_move=(op=="=<"))
            if not isinstance(arg1.start, Id):
                raise ParsingError("Variable name must be an identifier", itoken)
            decl.type = expr_to_type(arg1.end)
            decl.value = parse_expression(itoken, precedence+1, op_prec=op_prec)
            arg1 = decl
        elif op == "[":
            itoken.skip_empty_lines()
            maybe_list_comp = itoken.peak() == "for"
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
        elif op in {"++", "--"}:
            arg1 = UnaryExpr(arg=arg1, op=op, src=itoken.src, coords=op_coords)
        elif op == "=>":
            arg1 = UnaryExpr(arg=arg1, op=op, src=itoken.src, coords=op_coords)
        elif op == "." and arg1 is None:
            # unary . aka toggle => expand to arg = True
            arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
            end_coord = arg2.coords[1] if arg2 is not None else op_coords[1]
            arg1 = BinExpr(
                arg2, Const(True), op="=", src=itoken.src, coords=[op_coords[0], end_coord]
            )
        else:
            arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
            end_coord = arg2.coords[1] if arg2 is not None else arg1.coords[0] + len(op)
            binop = BinExpr(
                arg1, arg2, op, src=itoken.src,
                coords=[arg1.coords[0], end_coord]
            )
            arg1 = binop
        op = itoken.peak()

    if (precedence == MIN_PRECEDENCE and isinstance(arg1, SliceExpr)
        and arg1.step is None and arg1.end is not None
        and is_toplevel):
        # it's actually a var decl
        decl = VarDecl(mutable=not is_struct, src=arg1.src, coords=arg1.coords)
        if arg1.start is not None:
            if isinstance(arg1.start, CallerContextExpr):
                decl.name = arg1.start.arg.name
                decl.is_callerContext = decl.is_pseudo = True
            elif isinstance(arg1.start, Id):
                decl.name = arg1.start.name
            else:
                raise ParsingError("Variable name must be an identifier", itoken)
        decl.type = expr_to_type(arg1.end)
        arg1 = decl

    return arg1

def parse_num_const(token: str, tk_coords, itoken):
    suffix_map = {
        "f": "Float", "d": "Double", 
        "l": "Long", "ul": "Ulong", "i": "Int", "u": "Uint", "ui": "Uint",
        "s": "Short", "us": "Ushort", "b": "Byte", "ub": "Ubyte", "z": "Size"
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
        explicit_base = False
        if token.startswith("0"):
            bracket_idx = token.find('(')
            if bracket_idx > 0:
                explicit_base = True
                num_str = token[1:bracket_idx]
                closing_idx = token.find(')', bracket_idx)
                if closing_idx < 0:
                    raise ParsingError("Ill-formatted number literal", itoken)
                base = int(token[bracket_idx+1:closing_idx])
                suffix = token[closing_idx+1:]
            else:
                base = 16 if token.startswith("0x") else 8
                for i_suffix in suffix_map.keys():
                    if token.lower().endswith(i_suffix):
                        suffix = i_suffix if len(suffix) < len(i_suffix) else suffix
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

        res = Const(int(num_str, base=base), token[:len(token)-len(suffix)], "Int",
                    src=itoken.src, coords=tk_coords)
        if base not in {10, 16, 8}:
            res.value_str = str(res.value)
        elif explicit_base:
            if base == 16: res.value_str = "0x" + num_str
            elif base == 8: res.value_str = "0" + num_str
            else: res.value_str = num_str
        if res.value not in {0, 1}:
            if suffix == "l": res.value_str += "ll"
            if suffix == "ul": res.value_str += "ull"
        if suffix in suffix_map:
            res.type = suffix_map[suffix]
        elif suffix != "":
            raise ParsingError("Unknown number suffix", itoken)
        
    return res

def parse_var_decl(itoken, name_token, precedence, op_prec):
    decl = VarDecl(src=itoken.src, coords=name_token.coords)
    if not isinstance(name_token, Empty):
        decl.name = name_token.name
    else:
        decl.coords = itoken.peak_coords()

    if itoken.check("mut"):
        decl.mutable = True
        decl.explicit_mutable = True
    elif itoken.peak() in {"out", "inout", "outin", "ref"}:
        raise ParsingError(f"'{itoken.peak()}' is a reserved keyword", itoken)
    elif itoken.check("pseudo"):
        decl.is_pseudo = True
    elif itoken.check("in"):
        itoken.expect("(")
        itoken.skip_empty_lines()
        if itoken.peak() != ")":
            decl.index_in = parse_expression(itoken, is_toplevel=False)
            itoken.skip_empty_lines()
        else:
            decl.index_in = nobase
        if itoken.peak() == ",":
            raise ParsingError("Indecies require only one base", itoken)
        itoken.expect(")")

    if itoken.peak() in var_qualifiers:
        raise ParsingError("Only one variable qualifier is allowed.", itoken)
    
    if not is_end_of_expr(itoken):
        decl.type = expr_to_type(
            parse_expression(itoken, precedence+1, op_prec=op_prec)
        )
    if "=" in op_prec and itoken.check("="):
        decl.value = parse_expression(itoken, precedence+1, op_prec=op_prec)

    return decl

def is_end_of_expr(itoken):
    return itoken.peak() in {";", ")", "]", "}", "=", ",", "=<", "=>"}

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
    if_expr.block = parse_block(itoken)

    if isinstance(if_expr.block.body, list) and itoken.peak() == "if":
        raise ParsingError(
            "Cannot put an if on the same line as another if. Did you mean `elif`?",
            itoken
        )

    itoken.skip_empty_lines()
    if itoken.check("else"):
        if_expr.else_node = parse_block(itoken)
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
        res.loop_name = parse_expression(itoken)
    return res


def expr_to_type(expr):
    if isinstance(expr, Select):
        return ArrayType(expr.base, expr.args.args, src=expr.src, coords=expr.coords)
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
    args, kwargs = parse_args_kwargs(itoken)
    itoken.expect("}")
    end_coords = itoken.peak_coords()
    return StructLiteral(
        struct_expr, args, kwargs, src=itoken.src, coords=[start_coords[0], end_coords[1]]
    )

def parse_str_literal(prefix, prefix_start, itoken):
    res = StrLiteral(prefix=prefix, src=itoken.src)
    itoken.i -= 1 # move back in order to get the " coords
    part_start = itoken.peak_coords()[1]
    itoken.i += 1
    part_end = part_start
    while itoken.peak() != '"':
        part_end = itoken.peak_coords()[0]

        if itoken.check("{"):
            if part_start < part_end:
                lit = itoken.src.code[part_start:part_end]
                res.parts.append(Const(lit))

            is_introspective = itoken.check("=")
            args_coords_start = itoken.peak_coords()[0]
            args, kwargs = parse_args_kwargs(itoken)
            args_coords_end = itoken.peak_coords()[0]
            res.parts.append(Args(args, kwargs, is_introspective=is_introspective,
                                  src=itoken.src,
                                  coords=(args_coords_start, args_coords_end)))

            part_start = itoken.peak_coords()[0] + 1
            itoken.expect("}")
        else:
            itoken.check("\\")
            itoken.consume()

    part_end = itoken.peak_coords()[0]
    itoken.expect('"')

    if part_start < part_end:
        lit = itoken.src.code[part_start:part_end]
        res.parts.append(Const(lit))
    
    res.coords = (prefix_start, part_end+1)
    res.full_str = itoken.src.code[prefix_start+len(prefix)+1:part_end]
    return res

def parse_args_kwargs(itoken, is_toplevel=True, is_taglist=False, accept_inject=False):
    positional, named = [], {}
    args = parse_expr_list(itoken, ignore_eols=True, is_toplevel=is_toplevel, is_taglist=is_taglist, accept_inject=accept_inject)
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
    

def parse_expr_list(itoken, ignore_eols=True, is_toplevel=True, is_taglist=False, accept_inject=False):
    res = []
    inject = None
    if ignore_eols: itoken.skip_empty_lines()
    while itoken.peak() not in {")", "]", "}", ";"}:
        if inject is not None:
            raise ParsingError("Cannot have any arguments after ...", itoken)
        calltime_coords = itoken.peak_coords()
        if itoken.peak() != "...":
            if itoken.peak() == "<<":
                raise ParsingError("Guards are allowed only on new lines", itoken)
            expr = parse_expression(itoken, is_toplevel=is_toplevel)

            res.append(expr)
        else:
            if accept_inject:
                inject = ScopeArgsInject(src=itoken.src, coords=itoken.peak_coords())
                itoken.consume()
            else:
                raise ParsingError("... Can appear only at the end of an argument list", itoken)
        if ignore_eols: itoken.skip_empty_lines()
        if itoken.peak() not in {")", "]", "}", ";"}:
            itoken.expect(",")
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
        coords = itoken.peak_coords()

        if itoken.peak() == "import":
            node = parse_import(itoken)
        elif itoken.check("#"):
            node = parse_sl_comment(itoken)
        elif itoken.check(";;"):
            node = parse_ml_comment(itoken)
        elif itoken.check("def"):
            node = parse_def(itoken)
        elif itoken.check("struct"):
            node = parse_struct(itoken)
        elif itoken.check("from"):
            raise ParsingError(
                "The correct syntax to import a library is 'import <libname>'",
                itoken
            )
        elif itoken.check("return"):
            expr = parse_expr_list(itoken)
            if len(expr) == 1:
                expr = expr[0]
            node = Return(expr, src=itoken.src, coords=coords)
            itoken.expect_semicolon()
        elif itoken.check("error"):
            exprs = parse_expr_list(itoken)
            if len(exprs) == 0:
                raise ParsingError("Missing value for \"error\" statement", itoken)
            if len(exprs) > 1:
                raise ParsingError("Only one error can be issued", itoken)
            node = Error(exprs[0], src=itoken.src, coords=coords)
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

def fuzzy_cmp(str1, str2):
    return SM(None, str1, str2).ratio()

def should_have_semicolon_after_expr(node):
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
        field = parse_expression(itoken, is_struct=True)
        if isinstance(field, Id):
            # Id's are VarDecls in the context of enums and flags
            field = VarDecl(field.name, tags=field.tags, 
                            src=field.src, coords=field.coords)
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
