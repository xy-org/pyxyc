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
        return self.tokens[self.i]
    
    def peak_coords(self):
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
    
    def skip_until(self, delim):
        while self.has_more() and self.consume() != delim:
            pass

    def skip_empty_lines(self):
        i = 0
        while self.has_more() and self.check("\n"):
            i += 1
        return i


class ParsingError(Exception):
    def __init__(self, msg, itoken):
        if itoken.has_more():
            token_idx = itoken.i
            loc = itoken.token_pos[itoken.i]
            token_len = len(itoken.tokens[token_idx])
        else:
            loc = itoken.token_pos[-1] + len(itoken.tokens[-1]) - 1
            token_idx = len(itoken.token_pos) - 1
            token_len = 1

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

        fn = itoken.src.filename
        self.error_message = msg
        self.fmt_msg = f"{fn}:{line_num}:{loc - line_loc + 1}: error: {msg}\n"
        self.fmt_msg += f"| {itoken.src.code[line_loc:line_end]}\n"
        self.fmt_msg += "  " + (" " * (loc-line_loc)) + ("^" * token_len) + "\n"

    def __str__(self):
        return self.fmt_msg


def parse_code(src):
    if isinstance(src, str):
        src = Source("<unknown>", src)
    ast = []
    tokens, token_pos = split_tokens(src.code)
    itoken = TokenIter(tokens, token_pos, src)
    while itoken.check("\n"):
        pass
    while itoken.has_more():
        tok = itoken.peak()
        if tok == "import":
            itoken.consume()
            node = parse_import(itoken)
            ast.append(node)
        elif tok == "#":
            itoken.consume()
            node = parse_sl_comment(itoken)
            ast.append(node)
        elif tok == ";;":
            itoken.consume()
            node = parse_ml_comment(itoken)
            ast.append(node)
        elif tok == "def":
            itoken.consume()
            node = parse_def(itoken)
            ast.append(node)
        elif tok == "struct":
            itoken.consume()
            node = parse_struct(itoken)
            ast.append(node)
        elif tok == "from":
            raise ParsingError(
                "The correct syntax to import a library is 'import <libname>'",
                itoken
            )
        else:
            raise ParsingError("Unknown token", itoken)
        while itoken.check("\n"):
            pass
    return ast
        
def parse_import(itoken):
    lib = itoken.consume()
    while not itoken.peak_eol() and itoken.peak() == ".":
        itoken.consume()
        lib += "." + itoken.consume()
    in_name = None
    if itoken.check("in"):
        in_name = itoken.consume()
    itoken.expect_eol()
    return Import(lib=lib, in_name=in_name)

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

def parse_def(itoken):
    name = itoken.consume()
    node = FuncDef(name=name, src=itoken.src)
    if itoken.check("~"):
        node.tags = parse_tags(itoken)
    node.params = parse_params(itoken)
    itoken.expect("->", "Missing -> in func def."
                  " Please put '-> void' if the func doesn't return anything.")
    node.rtype = parse_type(itoken)
    if itoken.check("|"):
        node.etype = parse_type(itoken)
    num_empty = itoken.skip_empty_lines()
    while itoken.peak() in {">>", "<<"}:
        guard_token = itoken.consume()
        if num_empty <= 0:
            raise ParsingError("Guards should be on new lines", itoken)
        guard_expr = parse_expression(itoken)
        if guard_token == "<<":
            node.out_guards.append(guard_expr)
        else:
            node.in_guards.append(guard_expr)
        itoken.expect(";")
        num_empty = itoken.skip_empty_lines()  
    node.body = parse_body(itoken)
    return node

def parse_params(itoken):
    res = []
    itoken.expect("(")
    while itoken.peak() != ")":
        pname = itoken.consume()
        param = Param(pname, src=itoken.src)
        itoken.expect(":")
        param.type = parse_type(itoken)
        res.append(param)
        if itoken.peak() != ")":
            itoken.expect(",")
    itoken.expect(")")
    return res

def parse_type(itoken):
    name = itoken.consume()
    res = Type(name=name, src=itoken.src)
    if itoken.check("~"):
        res.tags = parse_tags(itoken)
    return res

operator_precedence = {
    "~": 11,
    "++" : 10, "--": 10, ".": 10, "(": 10, "[": 10, "{": 10, "'": 10, "\\": 10,
    "^": 9,
    "*": 8, "/": 8,
    "+": 7, "-": 7,
    "<": 6, "<=": 6, ">=": 6, ">": 6,
    "==": 5, "!=": 5,
    "&": 4,
    "|": 3,
    "=": 2, ":": 2,
}
MIN_PRECEDENCE=2
MAX_PRECEDENCE=11

def parse_expression(itoken, precedence=MIN_PRECEDENCE, is_struct=False):
    # if precedence >= MAX_PRECEDENCE and itoken.peak() == "(":
    if precedence >= MAX_PRECEDENCE:
        if itoken.peak() != '-' and itoken.peak() in operator_precedence.keys():
            return None  # Reach a delimiter
        tk_coords = itoken.peak_coords()
        token = itoken.consume()
        if token in {"true", "false"}:
            arg1 = Const(bool(token), token, "bool")
        elif "." in token:
            type = "double"
            value_str = token
            if token[-1] == 'f':
                token = token[:-1]
                type = "float"
            arg1 = Const(float(token), value_str, type)
        elif token[0] >= '0' and token[0] <= '9':
            if token.startswith("0x"):
                arg1 = Const(int(token[2:], base=16), token, "int")
            else:
                arg1 = Const(int(token), token, "int")
        else:
            arg1 = Id(token, src=itoken.src, coords=tk_coords)
    else:
        arg1 = parse_expression(itoken, precedence+1)

    op = itoken.peak()
    op_coords = itoken.peak_coords()
    while op in operator_precedence and operator_precedence[op] == precedence:
        itoken.consume()  # operator
        if op == "(":
            if not isinstance(arg1, Id):
                itoken.i -= 1
                raise ParsingError("Only functions are callable.", itoken)
            args, kwargs = parse_args(itoken)
            itoken.expect(")")
            fcall = FuncCall(arg1.name, args, src=itoken.src, coords=arg1.coords)
            fcall.kwargs = kwargs
            arg1 = fcall
        elif op == "'":
            f_coords = itoken.peak_coords()
            fname = itoken.consume()
            fcall = FuncCall(fname, [arg1], src=itoken.src, coords=f_coords)
            if itoken.check("("):
                args, kwargs = parse_args(itoken)
                fcall.args.extend(args)
                fcall.kwargs = kwargs
                itoken.expect(")")
            arg1 = fcall
        elif op == "\\":
            f_coords = itoken.peak_coords()
            fname = itoken.consume()
            fcall = FuncCall(fname, [arg1], src=itoken.src, coords=f_coords)
            arg2 = parse_expression(itoken, precedence+1)
            fcall.args.append(arg2)
            arg1 = fcall
        elif op == ":":
            if itoken.check("var"):
                # it's a var decl
                decl = VarDecl(name=arg1.name, varying=True, src=itoken.src)
                decl.type = parse_expression(itoken, precedence+1)
                if itoken.check("="):
                    decl.value = parse_expression(itoken, precedence+1)
                arg1 = decl
            elif isinstance(arg1, SliceExpr):
                if arg1.step is not None:
                    raise ParsingError(
                        "Slices can have only 3 components - start:end:step"
                    )
                arg1.step = parse_expression(itoken, precedence+1)
            else:
                arg2 = parse_expression(itoken, precedence+1)
                sliceop = SliceExpr(start=arg1, end=arg2, src=itoken.src)
                arg1 = sliceop
        elif op == "=" and isinstance(arg1, SliceExpr):
            decl = VarDecl(name=arg1.start.name, src=itoken.src)
            decl.type = arg1.end
            decl.value = parse_expression(itoken)
            arg1 = decl
        elif op == "[":
            itoken.expect("]")
            index = Index(arg1, args, src=itoken.src)
            arg1 = index
        elif op == "~":
            if isinstance(arg1, AttachTags):
                # parse right to left
                arg2 = parse_expression(itoken, precedence+1)
                arg1.tags.args[0] = AttachTags(
                    arg1.tags.args[0],
                    TagList([arg2]),
                )
            elif itoken.check("["):
                args, kwargs = parse_args(itoken)
                itoken.expect("]")
                attach_tags = AttachTags(arg1, TagList(args, kwargs))
                arg1 = attach_tags
            else:
                arg2 = parse_expression(itoken, precedence+1)
                attach_tags = AttachTags(arg1, TagList([arg2]))
                arg1 = attach_tags
        elif op == "{":
            arg1 = parse_struct_literal(itoken, arg1)
            if itoken.peak() == "~":
                raise ParsingError(
                    "Only simple positional tags can be chained. "
                    "Please be explicit and put the tags in square brackets.",
                    itoken
                )
        else:
            arg2 = parse_expression(itoken, precedence+1)
            binop = BinExpr(arg1, arg2, op, src=itoken.src, coords=op_coords)
            arg1 = binop
        op = itoken.peak()

    if (precedence == MIN_PRECEDENCE and isinstance(arg1, SliceExpr)
        and arg1.step is None):
        # it's actually a var decl
        decl = VarDecl(name=arg1.start.name, varying=not is_struct)
        decl.type = arg1.end
        arg1 = decl

    return arg1

def parse_struct_literal(itoken, struct_expr):
    args, kwargs = parse_args(itoken)
    itoken.expect("}")
    return StructLiteral(
        struct_expr, args, kwargs, src=itoken.src, coords=struct_expr.coords
    )


def parse_args(itoken):
    positional, named = [], {}
    while itoken.peak() not in {")", "]", "}"}:
        expr = parse_expression(itoken)
        is_named = (
            isinstance(expr, BinExpr) and expr.op == "=" and
            isinstance(expr.arg1, Id)
        )
        if is_named:
            named[expr.arg1.name] = expr.arg2
        else:
            positional.append(expr)
        if itoken.peak() not in {")", "]", "}"}:
            itoken.expect(",")
    return positional, named

def parse_body(itoken):
    body = []
    itoken.expect("{")
    itoken.skip_empty_lines()
    while itoken.peak() != "}":
        if itoken.check("return"):
            expr = parse_expression(itoken)
            node = Return(expr)
            itoken.expect(";")
        else:
            node = parse_expression(itoken)
            itoken.expect(";")
        body.append(node)
        itoken.skip_empty_lines()
    itoken.expect("}")
    return body

def parse_tags(itoken):
    res = TagList()
    if itoken.check("["):
        args, kwargs = parse_args(itoken)
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

def parse_struct(itoken):
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
        itoken.expect(";")
        node.fields.append(field)
        itoken.skip_empty_lines()
    itoken.expect("}")
    if itoken.peak() == ";":
        raise ParsingError("';' at end of struct def is not needed", itoken)
    return node