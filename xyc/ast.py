from dataclasses import dataclass, field

@dataclass
class Source:
    filename: str
    code: str

@dataclass
class Node:
    src: Source | None = field(
        init=True, compare=False, repr=False, kw_only=True, default=None
    )

    coords : int = field(
        init=True, kw_only=True, compare=False, repr=False, default=(-1, -1)
    )

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
class TagList(Node):
    positional: list[Node] = field(default_factory=list)
    named: dict[str, Node] = field(default_factory=dict)

@dataclass
class Type(Node):
    name: str
    tags: TagList = field(default_factory=TagList)

@dataclass
class Param(Node):
    name: str
    type: Type | None = None
    value: Node | None = None
    outin: bool = False

@dataclass
class FuncDef(Node):
    name: str
    tags: TagList = field(default_factory=TagList)
    params: list[Param] = field(default_factory=list)
    rtype: Type | None = None
    etype: Type | None = None
    in_guards: list[Node] = field(default_factory=list)
    out_guards: list[Node] = field(default_factory=list)
    body: list[Node] = field(default_factory=list)

@dataclass
class FuncCall(Node):
    name: str
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)

@dataclass
class StructLiteral(Node):
    name: Node | None
    args: list[Node] = field(default_factory=list)
    kwargs: dict[str, Node] = field(default_factory=dict)

@dataclass
class Var(Node):
    name: str

@dataclass
class Const(Node):
    value: str | int | float
    value_str: str = ""
    type: str | None = None

    def __init__(self, value, value_str=None, type=None):
        self.value = value
        self.value_str = value_str if value_str is not None else str(value)
        if type is None:
            if isinstance(value, int):
                type = "int"
            elif isinstance(value, float):
                type = "float"
        self.type = type

@dataclass
class BinExpr(Node):
    arg1: Node
    arg2: Node
    op: str

@dataclass
class AttachTags(Node):
    arg: Node | None = None
    tags: TagList = field(default_factory=TagList)

@dataclass
class Return(Node):
    value: Node

@dataclass
class VarDecl(Node):
    name: str
    type: Type | None = None
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
    tags: TagList = field(default_factory=TagList)
    fields: list[VarDecl] = field(default_factory=list)
