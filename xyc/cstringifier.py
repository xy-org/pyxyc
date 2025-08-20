from xyc.cast import *

op_precedence = {
    'post++': 12, 'post--': 12, '.': 12, 'pre.': 12, '->': 12,
    'pre*': 11, 'pre&': 11, 'pre!': 11, 'pre~': 11, 'pre++': 11, 'pre--': 11, 'pre+': 11, 'pre-': 11,
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
    '?:': 0.5,
    '=': 0, '+=': 0, '-=': 0, '*=': 0, '/=': 0, '%=': 0, '<<=': 0, '>>=': 0,
    '&=': 0, '^=': 0, '|=': 0,
    ',': -1
}
cast_precedence = 11

def stringify(ast: Ast):
    frags = []

    for node in ast.defines:
        stringify_def(node, frags)

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

    for func in ast.func_decls:
        stringify_func_decl(func, frags)
        frags.append(";\n")
    if len(ast.func_decls) > 0:
        frags.append("\n")

    for node in ast.consts:
        if isinstance(node, Define):
            stringify_def(node, frags)
        elif isinstance(node, Excerpt):
            frags.append(node.excerpt)
            frags.append("\n")
        else:
            assert isinstance(node, VarDecl)
            stringify_var_decl(node, frags)
            frags.append(";\n")
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

    for node in ast.globals:
        if isinstance(node, Define):
            stringify_def(node, frags)
        elif isinstance(node, Excerpt):
            frags.append(node.excerpt)
            frags.append("\n")
        else:
            assert isinstance(node, VarDecl)
            stringify_var_decl(node, frags)
            frags.append(";\n")
    if len(ast.globals) > 0:
        frags.append("\n")

    for func in ast.funcs:
        stringify_func_decl(func, frags)
        frags.append(" {\n")
        stringify_body(func.body, frags)
        frags.append("}\n")
        frags.append("\n")
    if len(ast.funcs) > 0:
        frags.pop()  # Remove double new line at end of file

    return "".join(frags)

def stringify_def(node, frags):
    frags.extend(("#define ", node.name))
    if len(node.params) > 0:
        frags.append("(")
        frags.append(", ".join([p.name for p in node.params]))
        frags.append(")")
    if node.value is not None:
        frags.append(' ')
        stringify_expr(node.value, frags)
    frags.append("\n")

def stringify_func_decl(func, frags):
    frags.extend((func.rtype, " ", func.name, "("))
    for i, param in enumerate(func.params):
        frags.extend((param.qtype.type.name, " ", param.name))
        if i < len(func.params)-1:
            frags.append(", ")
    if len(func.params) == 0:
        frags.append("void")
    frags.append(")")

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
                elif isinstance(else_body, Block):
                    frags.append(" else {\n")
                    stringify_body(else_body.body, frags, ident=ident+1)
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
        elif isinstance(stmt, Empty):
            pass
        elif isinstance(stmt, Label):
            frags.extend((" " * (ident-1) * 4, stmt.name, ":\n"))
        elif isinstance(stmt, Goto):
            frags.append(" " * ident * 4)
            frags.append("goto ")
            stringify_expr(stmt.label, frags)
            frags.append(";\n")
        else:
            frags.append(" " * (ident*4))
            if isinstance(stmt, InlineCode):
                frags.append(f";\n{' ' * ident * 4}")
            stringify_expr(stmt, frags, ident=ident)
            if isinstance(stmt, InlineCode):
                frags.append(f"\n{' ' * ident * 4};\n")
            else:
                frags.append(";\n")

def stringify_field(field, frags, ident):
    frags.extend((" " * ident * 4, field.qtype.type.name, " ", field.name))
    if len(field.qtype.type.dims) > 0:
        frags.extend(('[', ','.join(str(d) for d in field.qtype.type.dims), ']'))
    frags.append(";\n")

def parentheses_required(op, parent_op_precedence):
    # the check for the binary &(&) and |(|) is needed just to keep -Wall happy
    # but also generate more readable code
    return (
        parent_op_precedence > op_precedence[op] or
        op == "&" and parent_op_precedence == op_precedence["|"] or
        op == "&&" and parent_op_precedence == op_precedence["||"]
    )

def stringify_expr(expr, frags, parent_op_precedence=-10, ident=0):
    if isinstance(expr, Const):
        frags.append(expr.value_str if expr.value_str else str(expr.value))
    elif isinstance(expr, Id):
        frags.append(expr.name)
    elif isinstance(expr, Expr):
        op_prec = op_precedence[expr.op]
        parentheses = parentheses_required(expr.op, parent_op_precedence)
        if parentheses:
            frags.append("(")
        stringify_expr(expr.arg1, frags, op_prec)
        if expr.op not in {".", "->"}:
            frags.extend((" ", expr.op, " "))
        else:
            frags.append(expr.op)
        stringify_expr(expr.arg2, frags, op_prec)
        if parentheses:
            frags.append(")")
    elif isinstance(expr, UnaryExpr):
        op_prec = op_precedence[("pre" if expr.prefix else "post") + expr.op]
        if parent_op_precedence > op_prec:
            frags.append("(")
        if expr.prefix:
            frags.append(expr.op)
        operand_idx = len(frags)
        stringify_expr(expr.arg, frags, op_prec)
        if expr.op in {"-", "+"} and frags[operand_idx].startswith(expr.op):
            # guard against a unary - and a constant
            frags[operand_idx] = " " + frags[operand_idx]
        if parent_op_precedence > op_prec:
            frags.append(")")
        if not expr.prefix:
            frags.append(expr.op)
    elif isinstance(expr, TernaryExpr):
        parentheses = parentheses_required("?:", parent_op_precedence)
        if parentheses:
            frags.append("(")
        stringify_expr(expr.cond, frags, op_precedence["?:"])
        frags.append(" ? ")
        stringify_expr(expr.arg1, frags, op_precedence["?:"])
        frags.append(" : ")
        stringify_expr(expr.arg2, frags, op_precedence["?:"])
        if parentheses:
            frags.append(")")
    elif isinstance(expr, FuncCall):
        if isinstance(expr.name, str):
            frags.extend((expr.name, "("))
        else:
            stringify_expr(expr.name, frags, cast_precedence + 1)
            frags.append('(')
        for i, arg in enumerate(expr.args):
            if i != 0:
                frags.append(", ")
            stringify_expr(arg, frags)
        frags.append(")")
    elif isinstance(expr, CompoundLiteral):
        if isinstance(expr.name, str):
            frags.extend(["(", expr.name, "){"])
        elif expr.name is not None:
            frags.append("(")
            stringify_expr(expr.name, frags)
            frags.append("){")
        else:
            frags.append("{")

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
        if expr.index is not None:
            stringify_expr(expr.index, frags)
        frags.append("]")
    elif isinstance(expr, Break):
        frags.append("break")
    elif isinstance(expr, Continue):
        frags.append("continue")
    elif isinstance(expr, Cast):
        if parent_op_precedence > cast_precedence:
            frags.append("(")
        frags.extend(("(", expr.to, ")"))
        stringify_expr(expr.what, frags, cast_precedence)
        if parent_op_precedence > cast_precedence:
            frags.append(")")
    elif isinstance(expr, InlineCode):
        src = ("\n" + " " * (ident * 4)).join(expr.src.splitlines())
        frags.append(src)
    else:
        raise CGenerationError(f"Unknown expression {type(expr).__name__}")

def stringify_var_decl(stmt, frags):
    if stmt.qtype.is_threadLocal:
        frags.append("__thread ")
    if stmt.qtype.is_const and not stmt.qtype.type.is_ptr:
        frags.append("const ")
    frags.extend([stmt.qtype.type.name, " "])
    if stmt.qtype.is_const and stmt.qtype.type.is_ptr:
        frags.append("const ")
    frags.append(stmt.name)
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
