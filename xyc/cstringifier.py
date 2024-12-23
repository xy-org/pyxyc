from xyc.cast import *

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

    for struct in ast.struct_decls:
        frags.append("typedef struct ")
        frags.extend([struct.name, " ", struct.name, ";\n"])
    if len(ast.struct_decls) > 0:
        frags.append("\n")

    ident = 1
    for struct in ast.structs:
        frags.extend(["struct ", struct.name, " {\n"])
        for field in struct.fields:
            frags.extend([" " * ident * 4, field.type, " ", field.name, ";\n"])
        frags.append("};\n")
    if len(ast.structs) > 0:
        frags.append("\n")

    for func in ast.funcs:
        frags.extend((func.rtype, " ", func.name, "("))
        for i, param in enumerate(func.params):
            frags.extend((param.type, " ", param.name))
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
            frags.extend([stmt.type, " ", stmt.name])
            if stmt.is_array:
                for dim in stmt.dims:
                    frags.extend(["[", str(dim), "]"])
            if stmt.value is not None:
                frags.append(" = ")
                stringify_expr(stmt.value, frags)
            frags.append(";\n")
        else:
            raise CGenerationError(f"Unknown statement {type(stmt).__name__}")

def stringify_expr(expr, frags):
    if isinstance(expr, Const):
        frags.append(str(expr.value))
    elif isinstance(expr, Id):
        frags.append(expr.name)
    elif isinstance(expr, Expr):
        stringify_expr(expr.arg1, frags)
        if expr.op != ".":
            frags.extend((" ", expr.op, " "))
        else:
            frags.append(expr.op)
        stringify_expr(expr.arg2, frags)
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
    else:
        raise CGenerationError(f"Unknown expression {type(expr).__name__}")

class CGenerationError(Exception):
    def __init__(self, msg):
        self.msg = msg + "\nPlease should at the developers at: TBA"

    def __str__(self):
        return self.msg
