from dataclasses import dataclass, field


@dataclass
class Include:
    path: str
    internal: bool = False

@dataclass
class VarDecl:
    name: str
    type: str
    varying: bool = False
    value = None

@dataclass
class Struct:
    name: str
    fields: list[VarDecl]

@dataclass
class Expr:
    arg1: any = None
    arg2: any = None
    op: str = ""

@dataclass
class Name:
    name: str

@dataclass
class Const:
    value: str | int | float

@dataclass
class FuncCall:
    name: str
    args: list = field(default_factory=list)

@dataclass
class Func:
    name: str
    rtype: str
    params: list[VarDecl] = field(default_factory=list)
    body: list = field(default_factory=list)

@dataclass
class Return:
    value = None

@dataclass
class Ast:
    includes: list[Include] = field(default_factory=list)
    struct_decls: list[Struct] = field(default_factory=list)
    func_decls: list[Func] = field(default_factory=list)
    structs: list[Struct] = field(default_factory=list)
    funcs: list[Struct] = field(default_factory=list)

def stringify(ast: Ast):
    frags = []
    for inc in ast.includes:
        frags.append("#include ")
        if inc.internal:
            frags.extend(("\"", inc.path, "\""))
        else:
            frags.extend(("<", inc.path, ">"))
        frags.append("\n")

    for func in ast.funcs:
        frags.append("\n")
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
    return "".join(frags)

def stringify_body(body, frags, ident=1):
    for stmt in body:
        if isinstance(stmt, Return):
            frags.append(" " * (ident*4) + "return ")
            stringify_expr(stmt.value, frags)
            frags.append(";\n")
        else:
            raise CGenerationError(f"Unknown statement {type(stmt).__name__}")

def stringify_expr(expr, frags):
    if isinstance(expr, Const):
        frags.append(str(expr.value))
    elif isinstance(expr, Name):
        frags.append(expr.name)
    elif isinstance(expr, Expr):
        stringify_expr(expr.arg1, frags)
        frags.extend((" ", expr.op, " "))
        stringify_expr(expr.arg2, frags)
    elif isinstance(expr, FuncCall):
        frags.extend((expr.name, "("))
        for arg in expr.args:
            stringify_expr(arg, frags)
        frags.append(")")
    else:
        raise CGenerationError(f"Unknown statement {type(expr).__name__}")

class CGenerationError(Exception):
    def __init__(self, msg):
        self.msg = msg + "\nPlease should at the developers at: TBA"

    def __str__(self):
        return self.msg
