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
    varying: bool = False
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
    rtype: str
    params: list[VarDecl] = field(default_factory=list)
    body: list = field(default_factory=list)

@dataclass
class Return:
    value: any = None

@dataclass
class Ast:
    includes: list[Include] = field(default_factory=list)
    struct_decls: list[Struct] = field(default_factory=list)
    func_decls: list[Func] = field(default_factory=list)
    structs: list[Struct] = field(default_factory=list)
    funcs: list[Struct] = field(default_factory=list)

