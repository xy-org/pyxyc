from xyc.cast import *

op_precedence = {
    '.': 11, '->': 11,
    '*': 10, '/': 10, '%': 10,
    '+': 9, '-': 9,
    '<<': 8, '>>': 8,
    '<': 7, '<=': 7, '>': 7, '>=': 7,
    '==': 6, '!=': 6,
    '&': 5,
    '^': 4,
    '|': 3,
    '&&': 2,
    '||': 1,
    # ?:
    '=': 0, '+=': 0, '-=': 0, '*=': 0, '/=': 0, '%=': 0, '<<=': 0, '>>=': 0,
    '&=': 0, '^=': 0, '|=': 0,
    ',': -1
}

def stringify(ast: Ast):
    frags = []
    for inc in ast.includes:
        frags.append("#include ")
        if inc.internal:
            frags.extend(("\"", inc.path, "\""))
        else:
            frags.extend(("<", inc.path, ">"))
        frags.append("\n")
    if len(ast.includes) > 0:
        frags.append("\n")

    for typedef in ast.type_decls:
        frags.append(f"typedef {typedef.typename} {typedef.name};\n")
    if len(ast.type_decls) > 0:
        frags.append("\n")

    for node in ast.consts:
        assert isinstance(node, Define)
        if isinstance(node, Define):
            frags.extend(("#define ", node.name))
            if len(node.params) > 0:
                frags.append("(")
                frags.append(", ".join([p.name for p in node.params]))
                frags.append(")")
            if node.value is not None:
                frags.append(' ')
                stringify_expr(node.value, frags)
            frags.append("\n")
    if len(ast.consts) > 0:
        frags.append("\n")

    ident = 1
    for struct in ast.structs:
        frags.extend(["struct ", struct.name, " {\n"])
        for field in struct.fields:
            stringify_field(field, frags, ident)
        frags.append("};\n")
    if len(ast.structs) > 0:
        frags.append("\n")

    for func in ast.funcs:
        frags.extend((func.rtype, " ", func.name, "("))
        for i, param in enumerate(func.params):
            frags.extend((param.qtype.type.name, " ", param.name))
            if i < len(func.params)-1:
                frags.append(", ")
        if len(func.params) == 0:
            frags.append("void")
        frags.append(") {\n")
        stringify_body(func.body, frags)
        frags.append("}\n")
        frags.append("\n")
    if len(ast.funcs) > 0:
        frags.pop()  # Remove double new line at end of file
    
    return "".join(frags)

def stringify_body(body, frags, ident=1):
    for stmt in body:
        if isinstance(stmt, Return):
            frags.append(" " * (ident*4) + "return")
            if stmt.value is not None:
                frags.append(" ")
                stringify_expr(stmt.value, frags)
            frags.append(";\n")
        elif isinstance(stmt, VarDecl):
            frags.append(" " * ident * 4)
            stringify_var_decl(stmt, frags)
            frags.append(";\n")
        elif isinstance(stmt, If):
            frags.append(" " * ident * 4)
            frags.append("if (")
            stringify_expr(stmt.cond, frags)
            frags.append(") {\n")
            stringify_body(stmt.body, frags, ident=ident+1)
            frags.extend((" " * ident * 4, "}"))
            else_body = stmt.else_body
            while else_body is not None:
                if isinstance(else_body, list):
                    frags.append(" else {\n")
                    stringify_body(else_body, frags, ident=ident+1)
                    else_body = None
                else:
                    assert isinstance(else_body, If)
                    frags.append(" else if (")
                    stringify_expr(else_body.cond, frags)
                    frags.append(") {\n")
                    stringify_body(else_body.body, frags, ident=ident+1)
                    else_body = else_body.else_body
                frags.extend((" " * ident * 4, "}"))
            frags.append("\n")
        elif isinstance(stmt, DoWhile):
            frags.append(" " * ident * 4)
            frags.append("do {\n")
            stringify_body(stmt.body, frags, ident=ident+1)
            frags.extend((" " * ident * 4, "} while ("))
            stringify_expr(stmt.cond, frags)
            frags.append(");\n")
        elif isinstance(stmt, While):
            frags.append(" " * ident * 4)
            frags.append("while (")
            stringify_expr(stmt.cond, frags)
            frags.append(") {\n")
            stringify_body(stmt.body, frags, ident=ident+1)
            frags.extend((" " * ident * 4, "}\n"))
        elif isinstance(stmt, For):
            frags.append(" "  * ident * 4)
            frags.append("for (")
            for i, iter_decl in enumerate(stmt.inits):
                stringify_var_decl(iter_decl, frags)
                if i < len(stmt.inits) - 1:
                    frags.append(", ")
            frags.append(";")
            if stmt.cond is not None:
                frags.append(" ")
                stringify_expr(stmt.cond, frags)
            frags.append(";")
            if len(stmt.updates) > 0:
                frags.append(" ")
            for i, update_expr in enumerate(stmt.updates):
                stringify_expr(update_expr, frags)
                if i < len(stmt.updates) - 1:
                    frags.append(", ")
            frags.append(") {\n")
            stringify_body(stmt.body, frags, ident=ident+1)
            frags.extend((" " * ident * 4, "}\n"))
        elif isinstance(stmt, Block):
            frags.extend((" " * ident * 4, "{\n"))
            stringify_body(stmt.body, frags, ident=ident+1)
            frags.extend((" " * ident * 4, "}\n"))
        else:
            frags.append(" " * (ident*4))
            stringify_expr(stmt, frags)
            frags.append(";\n")

def stringify_field(field, frags, ident):
    frags.extend((" " * ident * 4, field.qtype.type.name, " ", field.name))
    if len(field.qtype.type.dims) > 0:
        frags.extend(('[', ','.join(str(d) for d in field.qtype.type.dims), ']'))
    frags.append(";\n")

def stringify_expr(expr, frags, parent_op_precedence=-10):
    if isinstance(expr, Const):
        frags.append(str(expr.value))
    elif isinstance(expr, Id):
        frags.append(expr.name)
    elif isinstance(expr, Expr):
        op_prec = op_precedence[expr.op]
        if parent_op_precedence > op_prec:
            frags.append("(")
        stringify_expr(expr.arg1, frags, op_prec)
        if expr.op not in {".", "->"}:
            frags.extend((" ", expr.op, " "))
        else:
            frags.append(expr.op)
        stringify_expr(expr.arg2, frags, op_prec)
        if parent_op_precedence > op_prec:
            frags.append(")")
    elif isinstance(expr, UnaryExpr):
        if expr.prefix:
            frags.append(expr.op)
        stringify_expr(expr.arg, frags)
        if not expr.prefix:
            frags.append(expr.op)
    elif isinstance(expr, FuncCall):
        frags.extend((expr.name, "("))
        for i, arg in enumerate(expr.args):
            if i != 0:
                frags.append(", ")
            stringify_expr(arg, frags)
        frags.append(")")
    elif isinstance(expr, StructLiteral):
        frags.extend(["(", expr.name, "){"])
        for arg in expr.args:
            stringify_expr(arg, frags)
            frags.append(", ")
        if len(expr.args) > 0:
            frags.pop()
        frags.append("}")
    elif isinstance(expr, InitList):
        frags.append("{")
        for i, elem in enumerate(expr.elems):
            if i > 0:
                frags.append(", ")
            stringify_expr(elem, frags)
        frags.append("}")
    elif isinstance(expr, Index):
        stringify_expr(expr.expr, frags)
        frags.append("[")
        stringify_expr(expr.index, frags)
        frags.append("]")
    elif isinstance(expr, Break):
        frags.append("break")
    elif isinstance(expr, Cast):
        frags.extend(("(", expr.to, ")"))
        stringify_expr(expr.what, frags)
    else:
        raise CGenerationError(f"Unknown expression {type(expr).__name__}")
    
def stringify_var_decl(stmt, frags):
    if stmt.qtype.is_const:
        frags.append("const ")
    frags.extend([stmt.qtype.type.name, " ", stmt.name])
    if stmt.qtype.type.is_array:
        for dim in stmt.qtype.type.dims:
            frags.extend(["[", str(dim), "]"])
    if stmt.value is not None:
        frags.append(" = ")
        stringify_expr(stmt.value, frags)

class CGenerationError(Exception):
    def __init__(self, msg):
        self.msg = msg + "\nPlease should at the developers at: TBA"

    def __str__(self):
        return self.msg
