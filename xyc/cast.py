from dataclasses import dataclass, field


@dataclass
class Include:
    path: str
    internal: bool = False

@dataclass
class Type:
    """ Unqaulified types """
    name: str = None
    dims: list[int] = field(default_factory=list)

    @property
    def is_array(self):
        return len(self.dims) > 0
    
    @property
    def is_ptr(self):
        return self.name is not None and len(self.name) > 0 and self.name[-1] == "*"

@dataclass
class QualType:
    type: 'Type' = field(default_factory=Type)
    is_const: bool = True
    is_volatile: bool = False
    is_restricted: bool = False

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = Type(self.type) 

@dataclass
class VarDecl:
    name: str
    qtype: QualType = None
    value: any = None

@dataclass
class Struct:
    name: str
    fields: list[VarDecl] = field(default_factory=list)

@dataclass
class CompoundLiteral:
    name: any = None
    args: list = field(default_factory=list)

@dataclass
class Expr:
    arg1: any = None
    arg2: any = None
    op: str = ""

@dataclass
class Label:
    name: str = ""

@dataclass
class Empty:
    pass

@dataclass
class UnaryExpr:
    arg: any = None
    op: str = ""
    prefix: bool = False

@dataclass
class Id:
    name: str

@dataclass
class Goto:
    label: any = None

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
class Block:
    body: list = field(default_factory=list)

@dataclass
class Break:
    pass

@dataclass
class Continue:
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
class Typedef:
    typename: str = None
    name: str = None

@dataclass
class Excerpt:
    excerpt: str = None

@dataclass
class Ast:
    includes: list[Include] = field(default_factory=list)
    type_decls: list[Struct] = field(default_factory=list)
    func_decls: list[Func] = field(default_factory=list)
    consts: list[VarDecl | Define | Excerpt] = field(default_factory=list)
    structs: list[Struct] = field(default_factory=list)
    funcs: list[Struct] = field(default_factory=list)

    def merge(self, other: 'Ast'):
        already_included = {inc.path for inc in self.includes}
        for ink in other.includes:
            if ink.path not in already_included:
                self.includes.append(ink)
                already_included.add(ink.path)

        self.type_decls.extend(other.type_decls)
        self.func_decls.extend(other.func_decls)
        self.consts.extend(other.consts)
        self.structs.extend(other.structs)
        self.funcs.extend(other.funcs)

