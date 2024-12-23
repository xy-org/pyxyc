from dataclasses import dataclass, field


@dataclass
class Include:
    path: str
    internal: bool = False

@dataclass
class VarDecl:
    name: str
    type: str
    dims: list = field(default_factory=list)
    is_const: bool = True
    value: any = None

    @property
    def is_array(self):
        return len(self.dims) > 0

@dataclass
class Struct:
    name: str
    fields: list[VarDecl] = field(default_factory=list)

@dataclass
class StructLiteral:
    name: str
    args: list = field(default_factory=list)

@dataclass
class Expr:
    arg1: any = None
    arg2: any = None
    op: str = ""

@dataclass
class UnaryExpr:
    arg: any = None
    op: str = ""
    prefix: bool = False

@dataclass
class Id:
    name: str

@dataclass
class Const:
    value: str | int | float

@dataclass
class InitList:
    elems: list = field(default_factory=list)

@dataclass
class FuncCall:
    name: str
    args: list = field(default_factory=list)

@dataclass
class Index:
    expr: any
    index: any

@dataclass
class Func:
    name: str
    rtype: str | None = None
    params: list[VarDecl] = field(default_factory=list)
    body: list = field(default_factory=list)

@dataclass
class Return:
    value: any = None

@dataclass
class If:
    cond: any = None
    body: list = field(default_factory=list)
    else_body: any = None

@dataclass
class While:
    cond: any = None
    body: list = field(default_factory=list)

@dataclass
class DoWhile:
    body: list = field(default_factory=list)
    cond: any = None

@dataclass
class For:
    inits: list[VarDecl] = field(default_factory=list)
    cond: any = None
    updates: list = field(default_factory=list)
    body: list = field(default_factory=list)

@dataclass
class Break:
    pass

@dataclass
class Cast:
    what: any = None
    to: str = ""

@dataclass
class Define:
    name: str = None
    params: list[VarDecl] = field(default_factory=list)
    value: any = None

@dataclass
class Ast:
    includes: list[Include] = field(default_factory=list)
    struct_decls: list[Struct] = field(default_factory=list)
    func_decls: list[Func] = field(default_factory=list)
    consts: list[VarDecl | Define] = field(default_factory=list)
    structs: list[Struct] = field(default_factory=list)
    funcs: list[Struct] = field(default_factory=list)

    def merge(self, other: 'Ast'):
        already_included = {inc.path for inc in self.includes}
        for ink in other.includes:
            if ink.path not in already_included:
                self.includes.append(ink)
                already_included.add(ink.path)

        self.struct_decls.extend(other.struct_decls)
        self.func_decls.extend(other.func_decls)
        self.consts.extend(other.consts)
        self.structs.extend(other.structs)
        self.funcs.extend(other.funcs)

