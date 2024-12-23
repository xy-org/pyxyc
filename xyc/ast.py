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
    comment: str
    is_doc : bool = False

@dataclass
class Param(Node):
    name: Node
    type: Node | None = None
    value: Node | None = None
    outin: bool = False

@dataclass
class FuncDef(Node):
    name: Node
    params: list[Param] = field(default_factory=list)
    rtype: Node | None = None
    etype: Node | None = None
    in_guards: list[Node] = field(default_factory=list)
    out_guards: list[Node] = field(default_factory=list)
    body: list[Node] = field(default_factory=list)

@dataclass
class FuncCall(Node):
    name: Node
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)

@dataclass
class Args(Node):
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)

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

def SimpleStr(value):
    return StrLiteral(parts=[Const(value)])

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

    def __init__(self, value, value_str=None, type=None):
        super().__init__()
        self.value = value
        self.value_str = value_str if value_str is not None else str(value)
        if type is None:
            if isinstance(value, int):
                type = "int"
            elif isinstance(value, float):
                type = "double"
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
    type: Node | None = None
    if_block: Node | list | None = None
    else_block: Node | list | None = None

@dataclass
class ForExpr(Node):
    pass

@dataclass
class WhileExpr(Node):
    cond: Node | None = None
    type: Node | Node = None
    name: Node | None = None
    block: Node | list | None = None
    else_block: Node | list | None = None

@dataclass
class Break(Node):
    loop_name: Node | None = None

@dataclass
class AttachTags(Node):
    arg: Node | None = None

    def __init__(self, arg, tags):
        super().__init__()
        self.arg = arg
        if tags is not None:
            self.tags = tags

@dataclass
class Return(Node):
    value: Node

@dataclass
class VarDecl(Node):
    name: str
    type: Node | None = None
    value: Node | None = None
    varying: bool = False

@dataclass
class SliceExpr(Node):
    start: Node | None = None
    end: Node | None = None
    step: Node | None = None

@dataclass
class StructDef(Node):
    name: str
    fields: list[VarDecl] = field(default_factory=list)
