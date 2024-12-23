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
            raise ParsingError("Unexpected end of file", self)
        return self.tokens[self.i]
    
    def peakn(self, n: int):
        if self.i + n >= len(self.tokens):
            raise ParsingError("Unexpected end of file", self)
        return self.tokens[self.i:self.i+n]
    
    def peak_coords(self):
        if not self.has_more():
            raise ParsingError("Unexpected end of file", self)
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
            raise ParsingError("Unexpected end of file", self)
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
    itoken.expect_eol()

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
    return Comment(comment=comment, is_doc=True, src=itoken.src,
                   coords=[comment_start, comment_start+2])

def parse_def(itoken: TokenIter):
    name_coords = itoken.peak_coords()
    name = itoken.consume()
    node = FuncDef(
        name=Id(name, src=itoken.src, coords=name_coords), src=itoken.src
    )
    if itoken.check("~"):
        node.tags = parse_tags(itoken)
    node.params = parse_params(itoken)

    itoken.check("=")
    value = parse_block(itoken)
    node.returns = value.returns
    node.etype = value.etype
    node.in_guards = value.in_guards
    node.out_guards = value.out_guards
    node.body = value.body

    if itoken.has_more() and itoken.peak() == ";":
        raise ParsingError(
            "Function definitions don't require a terminating semicolon.",
            itoken
        )

    return node

def parse_block(itoken):
    block = Block(src=itoken.src)

    if itoken.check("->"):
        if itoken.check("("):
            args = parse_expr_list(itoken)
            itoken.expect(")")
            # transform expressions
            for expr in args:
                if isinstance(expr, VarDecl):
                    expr.varying = True
                    block.returns.append(expr)
                else:
                    block.returns.append(
                        VarDecl(type=expr)
                    )
        else:
            block.returns = [VarDecl(name=None, type=parse_toplevel_type(itoken))]

        if itoken.check("||"):
            block.etype = parse_toplevel_type(itoken)

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
        itoken.expect_semicolon()
        num_empty = itoken.skip_empty_lines()

    block.coords = itoken.peak_coords()
    if itoken.peak() != "{":
        block.body = parse_expression(itoken)
    else:
        block.body = parse_body(itoken)

    return block

def parse_params(itoken):
    res = []
    itoken.expect("(", msg="Missing param list")
    while itoken.peak() not in {")", "]", "}", ";"}:
        itoken.skip_empty_lines()
        param = parse_expression(itoken)
        
        if not isinstance(param, VarDecl):
            raise ParsingError("Invalid parameter. Proper syntax is 'name : Type = value'", itoken)

        if not (param.is_in or param.is_out or param.is_inout or param.is_outin):
            param.is_in = True

        if param.name is None:
            param.is_pseudo = True

        param.varying = False
        param.is_param = True
        res.append(param)

        itoken.skip_empty_lines()
        if itoken.peak() != ")":
            itoken.expect(",")
        else:
            itoken.check(",")

    itoken.skip_empty_lines()
    itoken.expect(")")
    return res

    # res = []
    # itoken.expect("(", msg="Missing param list")
    # while itoken.peak() != ")":
    #     itoken.skip_empty_lines()
    #     param = VarDecl(src=itoken.src, is_param=True)
    #     if itoken.peak() != ":":
    #         param.name = itoken.consume()
    #     itoken.expect(":")

    #     access_set = False
    #     while True:
    #         if (access_set and itoken.peak() in {"in", "out", "inout"}) or itoken.peak() == "outin":
    #             raise ParsingError("Only one of 'in', 'out', 'inout' is allowed", itoken)
    #         if itoken.check("in"):
    #             param.is_in = access_set = True
    #         elif itoken.check("out"):
    #             param.is_out = access_set = True
    #         elif itoken.check("inout"):
    #             param.is_inout = access_set = True
    #         elif itoken.check("pseudo"):
    #             if param.is_pseudo:
    #                 raise ParsingError("Multiple pseudo qualifiers", itoken)
    #             param.is_pseudo = True
    #         else:
    #             break
    #     if not access_set:
    #         param.is_in = True
    #     if param.name is None:
    #         param.is_pseudo = True

    #     if itoken.peak() not in {"=", ","}:
    #         param.type = parse_type(itoken)

    #     if itoken.check("="):
    #         param.value = parse_expression(itoken)

    #     res.append(param)

    #     itoken.skip_empty_lines()
    #     if itoken.peak() != ")":
    #         itoken.expect(",")

    # itoken.skip_empty_lines()
    # itoken.expect(")")
    # return res

def parse_type(itoken):
    type_expr = parse_expression(itoken)
    return expr_to_type(type_expr)
    
def parse_toplevel_type(itoken):
    # this new map is here purely to provide better error messages in cases like
    # def func() -> MyType{} {...}
    # or
    # def func() -> Type1 || Type2 || Type3 {...}
    toplevel_precedence_map = {**operator_precedence}
    del toplevel_precedence_map["||"]
    del toplevel_precedence_map["{"]

    type_expr = parse_expression(itoken, op_prec=toplevel_precedence_map)
    return expr_to_type(type_expr)

operator_precedence = {
    "~": 12,
    "unary+": 11, "unary-": 11, "!": 11,
    "++" : 10, "--": 10, ".": 10, "(": 10, "[": 10, "{": 10, "'": 10,
    "^": 9, "\\": 9,
    "*": 8, "/": 8,
    "+": 7, "-": 7,
    "<": 6, "<=": 6, ">=": 6, ">": 6, ":": 6,
    "==": 5, "!=": 5, "in": 5,
    "&": 4,
    "|": 3, "||": 3,
    "=": 2, '+=': 2, '-=': 2, "|=": 2, '*=': 2, '/=': 2, ".=": 2,
}
MIN_PRECEDENCE=2
UNARY_PRECEDENCE=11
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
    elif itoken.peak() == "break":
        return parse_break(itoken)
    elif itoken.peak() == "for":
        return parse_for(itoken)

    if precedence >= MAX_PRECEDENCE and itoken.check("("):
        # bracketed expression
        arg1 = parse_expression(itoken, is_toplevel=False)
        itoken.expect(")", msg="Missing closing bracket")
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "[":
        # Array literal
        coords = itoken.peak_coords()
        itoken.consume()
        args = parse_expr_list(itoken)
        itoken.expect("]", msg="Missing closing bracket")
        arg1 = ArrayLit(args, src=itoken.src, coords=coords)
    elif precedence >= MAX_PRECEDENCE and itoken.peak() == "{":
        # announomous struct literal
        itoken.consume()
        arg1 = parse_struct_literal(itoken, None)
    elif precedence >= MAX_PRECEDENCE:
        tk_coords = itoken.peak_coords()
        token = itoken.consume()
        if token in {"true", "false"}:
            arg1 = Const(token == "true", token, "bool")
        elif "." in token:
            type = "double"
            value_str = token
            if token[-1] == 'f':
                token = token[:-1]
                type = "float"
            arg1 = Const(float(token), value_str, type)
        elif token[0] >= '0' and token[0] <= '9':
            if token.startswith("0x"):
                arg1 = Const(int(token[2:], base=16), token, "int",
                             src=itoken.src, coords=tk_coords)
            else:
                arg1 = Const(int(token), token, "int",
                             src=itoken.src, coords=tk_coords)
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
        else:
            arg1 = Id(token, src=itoken.src, coords=tk_coords)
    elif precedence == UNARY_PRECEDENCE and itoken.peak() in {"+", "-", "!"}:
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
            args, kwargs = parse_args_kwargs(itoken)
            itoken.expect(")")
            fcall = FuncCall(arg1, args, src=itoken.src, coords=arg1.coords)
            fcall.kwargs = kwargs
            arg1 = fcall
        elif op == "'":
            f_coords = itoken.peak_coords()
            fname = itoken.consume()
            fcall = FuncCall(
                Id(fname, src=itoken.src, coords=f_coords),
                [arg1], src=itoken.src, coords=f_coords)
            if itoken.check("("):
                args, kwargs = parse_args_kwargs(itoken)
                fcall.args.extend(args)
                fcall.kwargs = kwargs
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
        elif op == ":":
            var_qualifiers = {"var", "in", "out", "inout", "outin", "pseudo"}
            if itoken.peak() in var_qualifiers:
                # it's a var decl
                decl = VarDecl(src=itoken.src, coords=arg1.coords)
                if not isinstance(arg1, Empty):
                    decl.name = arg1.name

                if itoken.check("var"):
                    decl.varying = True
                elif itoken.check("in"):
                    decl.is_in = True
                elif itoken.check("out"):
                    decl.is_out = True
                elif itoken.check("inout"):
                    decl.is_inout = True
                elif itoken.check("outin"):
                    decl.is_outin = True
                elif itoken.check("pseudo"):
                    decl.is_pseudo = True

                if itoken.peak() in var_qualifiers:
                    raise ParsingError("Only one variable qualifier is allowed.", itoken)
                
                if not is_end_of_expr(itoken):
                    decl.type = expr_to_type(
                        parse_expression(itoken, precedence+1, op_prec=op_prec)
                    )
                if itoken.check("="):
                    decl.value = parse_expression(itoken, precedence+1, op_prec=op_prec)
                arg1 = decl
            elif converted_to_slice:
                if arg1.step is not None:
                    raise ParsingError(
                        "Slices can have only 3 components - start:end:step",
                        itoken
                    )
                if not is_end_of_expr(itoken):
                    arg1.step = parse_expression(itoken, precedence+1, op_prec=op_prec)
            else:
                converted_to_slice = True
                arg2 = None
                if not is_end_of_expr(itoken):
                    arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
                sliceop = SliceExpr(src=itoken.src, coords=arg1.coords)
                if not isinstance(arg1, Empty):
                    sliceop.start = arg1
                if not isinstance(arg2, Empty):
                    sliceop.end = arg2
                arg1 = sliceop
        elif op == "=" and isinstance(arg1, SliceExpr):
            decl = VarDecl(name=arg1.start.name, src=itoken.src, coords=op_coords)
            decl.type = expr_to_type(arg1.end)
            decl.value = parse_expression(itoken, precedence+1, op_prec=op_prec)
            arg1 = decl
        elif op == "[":
            args, kwargs = parse_args_kwargs(itoken, is_toplevel=False)
            itoken.expect("]")
            select = Select(
                arg1, Args(args, kwargs), src=itoken.src, coords=op_coords
            )
            arg1 = select
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
                args, kwargs = parse_args_kwargs(itoken)
                itoken.expect("]")
                attach_tags = AttachTags(
                    arg1, TagList(args, kwargs), src=itoken.src, coords=op_coords
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
        elif op == "." and arg1 is None:
            # unary . aka toggle
            arg2 = parse_expression(itoken, precedence+1, op_prec=op_prec)
            end_coord = arg2.coords[1] if arg2 is not None else op_coords[1]
            toggle_op = UnaryExpr(
                arg2, op=".", src=itoken.src, coords=[op_coords[0], end_coord]
            )
            arg1 = toggle_op
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
        decl = VarDecl(varying=not is_struct, src=arg1.src, coords=arg1.coords)
        if arg1.start is not None:
            decl.name = arg1.start.name
        decl.type = expr_to_type(arg1.end)
        arg1 = decl

    return arg1

def is_end_of_expr(itoken):
    return itoken.peak() in {";", ")", "]", "}", "=", ","}

def parse_if(itoken):
    if_coords = itoken.peak_coords()
    itoken.consume()  # "if"/"elif" token
    if_expr = IfExpr(src=itoken.src, coords=if_coords)
    if itoken.peak() != "(":
        name_coords = itoken.peak_coords()
        if_expr.name = Id(
            itoken.consume(), src=itoken.src, coords=name_coords
        )
    itoken.expect("(")
    if_expr.cond = parse_expression(itoken)
    itoken.expect(")", msg="Missing closing bracket")
    if_expr.block = parse_block(itoken)

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


def parse_break(itoken):
    break_coords = itoken.peak_coords()
    itoken.consume() # "break" token
    res = Break(src=itoken.src, coords=break_coords)
    if not is_end_of_expr(itoken):
        res.loop_name = parse_expression(itoken)
    return res


def expr_to_type(expr):
    if isinstance(expr, Select):
        return ArrayType(expr.base, expr.args.args, src=expr.src, coords=expr.coords)
    return expr

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
    part_start = itoken.peak_coords()[0]
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

def parse_args_kwargs(itoken, is_toplevel=True):
    positional, named = [], {}
    args = parse_expr_list(itoken, ignore_eols=True, is_toplevel=is_toplevel)
    for expr in args:
        is_named = (
            isinstance(expr, BinExpr) and expr.op == "=" and
            isinstance(expr.arg1, Id)
        )
        if is_named:
            named[expr.arg1.name] = expr.arg2
        else:
            positional.append(expr)
    return positional, named
    

def parse_expr_list(itoken, ignore_eols=True, is_toplevel=True):
    res = []
    if ignore_eols: itoken.skip_empty_lines()
    while itoken.peak() not in {")", "]", "}", ";"}:
        expr = parse_expression(itoken, is_toplevel=is_toplevel)
        res.append(expr)
        if ignore_eols: itoken.skip_empty_lines()
        if itoken.peak() not in {")", "]", "}", ";"}:
            itoken.expect(",")
    return res

def parse_body(itoken):
    itoken.expect("{")
    body = parse_stmt_list(itoken)
    itoken.expect("}")
    return body

def parse_stmt_list(itoken: TokenIter):
    body = []
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
                raise ParsingError(
                    "Malformed expression. Maybe missing operator or semicolon.",
                    itoken, notes=notes
                )

        body.append(node)
        itoken.skip_empty_lines()
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
        tk_coords = itoken.peak_coords()
        token = itoken.consume()
        tag = Id(token, src=itoken.src, coords=tk_coords)
        
        if itoken.peak() == "~":
            raise ParsingError(
                "These long chains of tags get very ambiguous. Please be explicit and seprate the tags in square brackets.",
                itoken
            )
        
        res.args = [tag]
    return res

def parse_struct(itoken: TokenIter):
    coords = itoken.peak_coords()
    name = itoken.consume()
    node = StructDef(name=name, src=itoken.src, coords=coords)
    if itoken.check("~"):
        node.tags = parse_tags(itoken)
    itoken.expect("{")
    # TODO should that be here
    itoken.skip_empty_lines()
    while itoken.peak() != "}":
        field = parse_expression(itoken, is_struct=True)
        if isinstance(field, Id):
            # Id's are VarDecls in the context of enums and flags
            field = VarDecl(field.name, tags=field.tags, 
                            src=field.src, coords=field.coords)
        itoken.expect(";", msg="Missing ';' at end of field")
        node.fields.append(field)
        itoken.skip_empty_lines()
    itoken.expect("}")
    if itoken.peak() == ";":
        raise ParsingError("';' at end of struct def is not needed", itoken)
    return node
