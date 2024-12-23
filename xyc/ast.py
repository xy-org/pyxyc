from dataclasses import dataclass, field

@dataclass
class Source:
    filename: str
    code: str

@dataclass
class TagList:
    args: list['Node'] = field(default_factory=list)
    kwargs: dict[str, 'Node'] = field(default_factory=dict)

@dataclass
class Node:
    tags: TagList = field(default_factory=TagList, kw_only=True)
    comment: str = field(default_factory=str, kw_only=True)

    src: Source | None = field(
        init=True, compare=False, repr=False, kw_only=True, default=None
    )

    coords : int = field(
        init=True, kw_only=True, compare=False, repr=False, default=(-1, -1)
    )

Ast = list[Node]

@dataclass
class Import(Node):
    lib: str
    in_name: str = None
    symbols: list[str] = field(default_factory=list)


@dataclass
class Comment(Node):
    def __init__(self, comment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comment = comment

@dataclass
class FuncType(Node):
    params: list['VarDecl'] = field(default_factory=list)
    returns: list['VarDecl'] = field(default_factory=list)
    etype: Node | None = None

@dataclass
class FuncSelect(Node):
    name: Node
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)
    multiple: bool = False

ModuleVisibility = "module"
PackageVisibility = "package"
PublicVisibility = "public"
visibilityMap = {"+": PackageVisibility, "-": ModuleVisibility, "*": PublicVisibility}

@dataclass
class FuncDef(Node):
    name: Node
    visibility: str = PackageVisibility
    params: list['VarDecl'] = field(default_factory=list)
    returns: list['VarDecl'] = field(default_factory=list)
    etype: Node | None = None
    in_guards: list[Node] = field(default_factory=list)
    out_guards: list[Node] = field(default_factory=list)
    body: list[Node] | Node | None = field(default_factory=list)

@dataclass
class Block(Node):
    returns: list['VarDecl'] = field(default_factory=list)
    etype: Node | None = None
    in_guards: list[Node] = field(default_factory=list)
    out_guards: list[Node] = field(default_factory=list)
    body: list[Node] | Node = field(default_factory=list)

    @property
    def is_embedded(self):
        return not isinstance(self.body, list)

@dataclass
class FuncCall(Node):
    name: Node
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)
    inject_args: 'ScopeArgsInject' = None

@dataclass
class Args(Node):
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)
    is_introspective: bool = False

@dataclass
class ScopeArgsInject(Node):
    pass  # Used only to store the coordinates of ...

@dataclass
class Select(Node):
    base: Node
    args: Args = field(default_factory=Args)

@dataclass
class StructLiteral(Node):
    name: Node | None
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)

@dataclass
class StrLiteral(Node):
    prefix: str = ""
    parts: list[Node] = field(default_factory=list)
    full_str: str = ""

def SimpleStr(value):
    return StrLiteral(parts=[Const(value)], full_str=value)

def SimpleRType(name):
    return [VarDecl(type=Id(name))]

@dataclass
class ArrayLit(Node):
    elems: list[Node] = field(default_factory=list)

@dataclass
class ArrayType(Node):
    base: Node
    dims: list[Node] = field(default_factory=list)

@dataclass
class Id(Node):
    name: str

@dataclass
class Const(Node):
    value: str | int | float
    value_str: str = ""
    type: str | None = None

    def __init__(self, value, value_str=None, type=None, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.value_str = value_str if value_str is not None else str(value)
        if type is None:
            if isinstance(value, bool):
                type = "bool"
                self.value_str = self.value_str.lower()
            elif isinstance(value, int):
                type = "int"
            elif isinstance(value, float):
                type = "double"
        if self.value_str == "True":
            import pdb; pdb.set_trace()
        self.type = type

@dataclass
class BinExpr(Node):
    arg1: Node
    arg2: Node
    op: str

@dataclass
class UnaryExpr(Node):
    arg: Node
    op: str

@dataclass
class IfExpr(Node):
    cond: Node | None = None
    name: Node | None = None
    block: Block | None = None
    else_node: Node | list | None = None

@dataclass
class ForExpr(Node):
    over: list[Node] = field(default_factory=list)
    name: Node | None = None
    block: Block | None = None
    else_node: Node | list | None = None

@dataclass
class ListComprehension(Node):
    list_type : Node | None = None
    loop: ForExpr | None = None

@dataclass
class WhileExpr(Node):
    cond: Node | None = None
    name: Node | None = None
    block: Block | Node | None = None
    else_node: Node | list | None = None

@dataclass
class DoWhileExpr(Node):
    cond: Node | None = None
    name: Node | None = None
    block: Block | Node | None = None
    else_node: Node | list | None = None

@dataclass
class Break(Node):
    loop_name: Node | None = None

@dataclass
class Continue(Node):
    loop_name: Node | None = None

@dataclass
class AttachTags(Node):
    arg: Node | None = None

    def __init__(self, arg, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arg = arg
        if tags is not None:
            self.tags = tags

@dataclass
class CallerContextExpr(Node):
    arg: Node | None = None

@dataclass
class Return(Node):
    value: Node

@dataclass
class Error(Node):
    value: Node

@dataclass
class VarDecl(Node):
    name: str | None = None
    type: Node | None = None
    value: Node | None = None
    mutable: bool = False
    is_param: bool = False
    is_in: bool = False
    is_out: bool = False
    is_inout: bool = False
    is_outin: bool = False
    is_pseudo: bool = False
    is_callerContext: bool = False
    index_in: Node | None = None

    @property
    def is_index(self):
        return self.index_in is not None
    
    @property
    def is_based(self):
        return self.index_in is not nobase
    
nobase = Id("")

def param(*args, **kwargs):
    res = VarDecl(*args, **kwargs)
    res.is_param = True
    if not (res.is_in or res.is_inout or res.is_outin or res.is_out):
        res.is_in = True
    return res

@dataclass
class SliceExpr(Node):
    start: Node | None = None
    end: Node | None = None
    step: Node | None = None
    op: str = None  # calculate end as start \op end

@dataclass
class StructDef(Node):
    name: str
    visibility: str = PackageVisibility
    fields: list[VarDecl] = field(default_factory=list)
