import os
from copy import copy
import xyc.ast as xy
import xyc.cast as c
from dataclasses import dataclass, field

@dataclass
class CompiledObj:
    tags: dict[str, 'CompiledObj'] = field(kw_only=True, default_factory=dict)
    xy_node : any = None
    c_node : any = None

@dataclass
class TypeObj(CompiledObj):
    tag_specs: list['VarObj'] = field(default_factory=list)
    builtin : bool = False
    fields: dict[str, 'VarObj'] = field(default_factory=dict)
    init_value: any = None
    is_init_value_zeros: bool = True
    base_type_obj: 'TypeObj' = None
    is_enum: bool = False
    is_flags: bool = False
    fully_compiled: bool = False

    def get_base_type(self):
        return self if self.base_type_obj is None else self.base_type_obj
    
    @property
    def name(self):
        if self.xy_node is not None:
            return self.xy_node.name
        else:
            return "<Unknown>"

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None
    
@dataclass
class ArrTypeObj(TypeObj):
    dims : list = field(default_factory=list)

    @property
    def c_name(self):
        self.base_type_obj.c_name + "*"

    @property
    def name(self):
        return self.base_type_obj.name + '[' + ']'
    
tag_list_type_obj = TypeObj(builtin=True)
any_type_obj = TypeObj(xy_node=xy.Id("?"), builtin=True)
    
@dataclass
class TypeInferenceError:
    msg: str = ""

@dataclass
class ConstObj(CompiledObj):
    value: int | float | str | None = None
    infered_type: TypeObj = None

@dataclass
class StrObj(CompiledObj):
    prefix: str = ""
    parts: list[CompiledObj] = field(default_factory=list)

    def as_str(self):
        if len(self.prefix) > 0:
            raise CompilationError("Expected unprefixed string", self.xy_node)
        if len(self.parts) > 0:
            assert len(self.parts) == 1
            return self.parts[0].value
        return ""

@dataclass
class ArrayObj(CompiledObj):
    elems: list[CompiledObj] = field(default_factory=list)

@dataclass
class InstanceObj(CompiledObj):
    type_obj: CompiledObj | None = None
    kwargs: dict[str, CompiledObj] = field(default_factory=dict)

    @property
    def infered_type(self):
        return self.type_obj

@dataclass
class FuncObj(CompiledObj):
    rtype_obj: TypeObj = None
    etype_obj: TypeObj = None
    param_objs: list['VarObj'] = field(default_factory=list)
    builtin: bool = False
    move_args_to_temps: bool = False
    module_header: 'ModuleHeader' = None  # None means current module

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None

@dataclass
class VarObj(CompiledObj):
    type_desc: TypeObj | None = None
    passed_by_ref: bool = False # True if the variable is a hidden pointer
    is_pseudo: bool = False
    default_value_obj: CompiledObj = None

    @property
    def infered_type(self):
        return self.type_desc

@dataclass
class ImportObj(CompiledObj):
    name: str | None = None
    is_external: bool = True  # XXX

@dataclass
class ExprObj(CompiledObj):
    infered_type: CompiledObj | str = "Cannot deduce type"
    compiled_obj: CompiledObj | None = None

@dataclass
class RefObj(CompiledObj):
    container: CompiledObj = None
    ref: CompiledObj = None

@dataclass
class FCallObj(ExprObj):
    func_obj: FuncObj | None = None

@dataclass
class ArgList:
    args: list[ExprObj] = field(default_factory=list)
    kwargs: dict[str, ExprObj] = field(default_factory=dict)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.args[key]
        else:
            return self.kwargs[key]
        
    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.args[key] = value
        else:
            self.kwargs[key] = value
        
    def __len__(self):
        return len(self.args) + len(self.kwargs)

class IdTable(dict):
    def merge(self, other: 'IdTable'):
        for key, value in other.items():
            current = self.get(key, None)
            if isinstance(value, ImportObj):
                continue # imports are not sticky
            elif current is None:
                if isinstance(value, FuncSpace):
                    self[key] = FuncSpace()
                    self[key]._funcs.extend(value._funcs)
                else:
                    self[key] = value
            elif isinstance(current, FuncSpace):
                if isinstance(value, FuncSpace):
                    current._funcs.extend(value._funcs)
                else:
                    raise ValueError("NYI")
            else:
                import pdb; pdb.set_trace()
                raise ValueError("NYI")

class FuncSpace:
    def __init__(self):
        self._funcs = []
        self.parent_space = None

    def __len__(self):
        return len(self._funcs)
    
    def append(self, fdesc: FuncObj):
        self._funcs.append(fdesc)

    def __getitem__(self, i):
        return self._funcs[i]
    
    def fmt_func(self, node):
        if isinstance(node, xy.ArrayType):
            return self.fmt_func(node.base) + '[' + ','.join(d.value_str for d in node.dims) + ']'
        else:
            return node.name
        

    def report_multiple_matches(self, candidate_fobjs, node, args_infered_types, ctx):
        fsig = ctx.eval_to_id(node.name) + "(" + \
            ", ".join(self.fmt_func(t.xy_node) for t in args_infered_types) + \
            ", ".join(f"{pname}: {self.fmt_func(t.xy_node)}" for pname, t in args_infered_types.kwargs.items()) + \
            ")"
        err_msg = f"Multiple function matches for '{fsig}'"
        candidates = "\n    ".join((
            func_sig(f) for f in candidate_fobjs
        ))
        raise CompilationError(
            err_msg, node,
            notes=[(f"Candidates are:\n    {candidates}", None)]
        )
    
    def report_no_matches(self, candidate_fobjs, node, args_infered_types, ctx):
        fsig = ctx.eval_to_id(node.name) + "(" + \
            ", ".join(self.fmt_func(t.xy_node) for t in args_infered_types) + \
            ", ".join(f"{pname}: {self.fmt_func(t.xy_node)}" for pname, t in args_infered_types.kwargs.items()) + \
            ")"
        err_msg = f"Cannot find function '{fsig}'"
        candidates = "\n    ".join((
            func_sig(f) for f in candidate_fobjs
        ))
        raise CompilationError(
            err_msg, node,
            notes=[(f"Candidates are:\n    {candidates}", None)]
        )
    
    def find(self, node, args_infered_types, ctx):
        space = self
        while space is not None:
            candidate_fobjs = space.find_candidates(node, args_infered_types, ctx)
            if len(candidate_fobjs) == 1:
                    return candidate_fobjs[0]
            if len(candidate_fobjs) > 1:
                space = space.parent_space
                while space is not None:
                    candidate_fobjs.extend(
                        space.find_candidates(node, args_infered_types, ctx)
                    )
                    space = space.parent_space
                self.report_multiple_matches(candidate_fobjs, node, args_infered_types, ctx)
            space = space.parent_space

        candidate_fobjs = []
        space = self
        while space is not None:
            candidate_fobjs.extend(space._funcs)
            space = space.parent_space
        self.report_no_matches(candidate_fobjs, node, args_infered_types, ctx)

    def find_candidates(self, node, args_infered_types, ctx):
        if isinstance(node, xy.FuncCall):
            candidate_fobjs = []
            for desc in self._funcs:
                if cmp_call_def(args_infered_types, desc, ctx):
                    candidate_fobjs.append(desc)
            
            return candidate_fobjs
        else:
            assert isinstance(node, xy.FuncDef)
            for desc in self._funcs:
                if desc.xy_node == node:
                    return [desc]
            raise "Cannot find func"
        
class ExtSpace(FuncSpace):
    def __init__(self, ext_name: str):
        self.ext_name = ext_name

    def find(self, node, args_infered_types, ctx):
        return FuncObj(c_node=c.Func(name=self.ext_name, rtype=None))


def cmp_call_def(fcall_args_types: ArgList, fobj: FuncObj, ctx):
    if len(fcall_args_types) > len(fobj.param_objs):
        return False
    if fobj.builtin and fobj.xy_node.name in {"typeof", "tagsof", "sizeof", "addrof"}:
        return fobj
    satisfied_params = set()
    # go through positional
    for type_obj, param_obj in zip(fcall_args_types.args, fobj.param_objs):
        # XXX
        if isinstance(type_obj, ArrTypeObj):
            continue
        if param_obj.type_desc is any_type_obj:
            continue
        if type_obj.get_base_type() is not param_obj.type_desc.get_base_type():
            return False
        if param_obj.xy_node is not None and param_obj.xy_node.name is not None:
            satisfied_params.add(param_obj.xy_node.name)

    # go through named
    pobjs_dict = {pobj.xy_node.name: pobj for pobj in fobj.param_objs if pobj.xy_node is not None and pobj.xy_node.name is not None}
    for pname, type_obj in fcall_args_types.kwargs.items():
        param_obj = pobjs_dict.get(pname, None)
        if param_obj is None:
            return False
        # XXX
        if isinstance(type_obj, ArrTypeObj):
            continue
        if type_obj is not param_obj.type_desc:
            return False
        if pname in satisfied_params:
            return False
        satisfied_params.add(pname)

    for p_obj in fobj.param_objs[len(fcall_args_types.args):]:
        if p_obj.xy_node.name not in satisfied_params and p_obj.xy_node.value is None:
            return False

    return True

def func_sig(fobj: FuncObj):
    fdef = fobj.xy_node
    name = fdef.name if isinstance(fdef.name, str) else fdef.name.name
    res = name + "("
    for i, pobj in enumerate(fobj.param_objs):
        if i > 0:
            res += ", "
        if pobj.xy_node is not None and pobj.xy_node.value is not None:
            res += "["
        if pobj.type_desc == any_type_obj:
            res += "?"
        else:
            res += pobj.type_desc.name
        if pobj.xy_node is not None and pobj.xy_node.value is not None:
            res += "]"
    res += ") -> "
    if len(fdef.returns) > 1:
        res += "("
    res += fobj.rtype_obj.xy_node.name
    if len(fdef.returns) > 1:
        res += ")"
    return res

@dataclass
class ModuleHeader:
    namespace: IdTable
    module_name: str = None
    str_prefix_reg: dict[str, any] = field(default_factory=dict)
    ctx: 'CompilerContext' = None

@dataclass
class CompilerContext:
    builder: any
    module_name: str  # TODO maybe module_name should be a list of the module names
    module_ns: IdTable = field(default_factory=IdTable)
    global_ns: IdTable = field(default_factory=IdTable)
    str_prefix_reg: dict[str, any] = field(default_factory=dict)

    current_fobj: FuncObj | None = None
    tmp_var_i: int = 0

    entrypoint_obj: any = None
    void_obj: any = None
    bool_obj: any = None
    ptr_obj: any = None
    size_obj: any = None
    enum_obj: any = None
    flags_obj: any = None

    stdlib_included = False

    def __post_init__(self):
        self.namespaces = [self.global_ns, self.module_ns]

    def is_prim_int(self, type_obj):
        return type_obj in self.prim_int_objs

    def push_ns(self):
        self.namespaces.append(dict())

    @property
    def ns(self):
        return self.namespaces[-1]

    def pop_ns(self):
        self.namespaces.pop()

    def ensure_func_space(self, name: xy.Id):
        if name.name not in self.module_ns:
            fspace = FuncSpace()
            self.module_ns[name.name] = fspace
            parent_space = self.global_ns.get(name.name, None)
            if isinstance(parent_space, FuncSpace):
                fspace.parent_space = parent_space
            return fspace
        candidate = self.module_ns[name.name]
        if isinstance(candidate, FuncSpace):
            return candidate
        # something else already defined with the same name
        raise CompilationError(
            f"Symbol '{name.name}' already defined.", name,
            notes=[
                (f"Previous definition of '{name.name}'", candidate.xy_node)
            ]
        )
    
    def eval_to_fspace(self, name: xy.Node, msg=None):
        space = self.eval(name)
        if space is None:
            msg = msg or f"Cannot find any functions named '{name.name}'"
            raise CompilationError(msg, name)
        if not (isinstance(space, FuncSpace) or isinstance(space, ExtSpace)):
            # TODO add notes here
            raise CompilationError(f"Not a function.", name)
        return space
    
    def eval_to_var(self, name: xy.Node):
        var_obj = self.eval(name)
        if var_obj is None:
            var_name = f" '{name.name}'" if isinstance(name, xy.Id) else ""
            raise CompilationError(f"Cannot find variable{var_name}", name)
        if not isinstance(var_obj, VarObj):
            raise CompilationError(f"Not a variable.", name)
        return var_obj
    
    def eval_to_id(self, name: xy.Node):
        if isinstance(name, xy.Id):
            return name.name
        raise CompilationError("Cannot determine identifier", name)

    def get_compiled_type(self, name: xy.Id | str):
        symbol_name = name.name if isinstance(name, xy.Id) else name
        for ns in reversed(self.namespaces):
            res = ns.get(symbol_name, None)
            if res is not None:
                return res

        raise CompilationError(f"Cannot find type '{name.name}'", name)
    
    def split_and_eval_tags(self, tags: xy.TagList, cast, ast):
        open_tags = []
        after_open = len(tags.args)
        for i in range(len(tags.args)):
            xy_tag = tags.args[i]
            if not isinstance(xy_tag, xy.VarDecl):
                after_open = i
            else:
                if after_open < len(tags.args):
                    raise CompilationError("Cannot mix positional and named tags.", xy_tag)
                open_tags.append(xy_tag)
        tag_specs = [
            VarObj(xy_node=xy_tag, type_desc=find_type(xy_tag.type, self))
            for xy_tag in open_tags
        ]
        remaining_args = tags.args[after_open:]
        return tag_specs, self.eval_tags(xy.TagList(remaining_args, tags.kwargs), cast=cast, ast=ast)

    
    def eval_tags(self, tags: xy.TagList, tag_specs: list[VarObj] = [], cast=None, ast=None):
        res = {}
        for i, xy_tag in enumerate(tags.args):
            tag_obj = self.eval(xy_tag)
            if i < len(tag_specs):
                spec = tag_specs[i]
                label = spec.xy_node.name
            elif isinstance(tag_obj, TypeObj):
                fully_compile_type(tag_obj, cast, ast, self)
                if "xyTag" not in tag_obj.tags:
                    raise CompilationError(
                        f"Missing default label for type '{tag_obj.xy_node.name}'",
                        xy_tag, notes=[("Please associate default label by adding the TagCtor tag: ~[TagCtor{label=\"default-label\"}]", None)])
                label = tag_obj.tags["xyTag"].kwargs["label"].as_str()
            elif isinstance(tag_obj, InstanceObj):
                assert tag_obj.type_obj is not None
                if "xyTag" not in tag_obj.type_obj.tags:
                    raise CompilationError(
                        f"Missing default label for type '{tag_obj.type_obj.xy_node.name}'",
                        xy_tag, notes=[("Please associate default label by adding the TagCtor tag: ~[TagCtor{label=\"default-label\"}]", None)])
                label = tag_obj.type_obj.tags["xyTag"].kwargs["label"].as_str()
            elif tag_obj.primitive:
                raise CompilationError("Primitive types have to have an explicit label", xy_tag)
            else:
                raise CompilationError("Cannot determine label for tag", xy_tag)
            
            if label in res:
                raise CompilationError(f"Label '{label}' already filled by tag", res[label].xy_node)
            res[label] = tag_obj
        for label, xy_tag in tags.kwargs.items():
            tag_obj = self.eval(xy_tag)
            if label in res:
                raise CompilationError(f"Label '{label}' already filled by tag", res[label].xy_node)
            res[label] = tag_obj
        return res

    def lookup(self, name: str):
        for ns in reversed(self.namespaces):
            if name in ns:
                return ns[name]
        return None

    def eval(self, node, msg=None):
        if isinstance(node, xy.Id):
            res = self.lookup(node.name)
            if res is None:
                if msg is None:
                    msg = f"Cannot find symbol '{node.name}'"
                raise CompilationError(msg, node)
            return res
        elif isinstance(node, xy.Const):
            const_type_obj = None
            if node.type is not None:
                const_type_obj = self.get_compiled_type(node.type)
            return ConstObj(value=node.value, xy_node=node, c_node=c.Const(node.value),
                            infered_type=const_type_obj)
        elif isinstance(node, xy.StrLiteral):
            return StrObj(
                prefix=node.prefix,
                parts=[self.eval(p) for p in node.parts],
                xy_node=node
            )
        elif isinstance(node, xy.StructLiteral):
            instance_type = self.eval(node.name)
            if instance_type is None:
                raise CompilationError("Cannot find name", node)
            obj = InstanceObj(type_obj=instance_type, xy_node=node)
            if len(node.args) > 0:
                for (fname, fobj), xy_arg in zip(instance_type.fields.items(), node.args):
                    obj.kwargs[fname] = self.eval(xy_arg)
            for name, value in node.kwargs.items():
                ct_value = self.eval(value)
                if ct_value is None:
                    raise CompilationError("Cannot eval at compile-time", value)
                obj.kwargs[name] = ct_value
            return obj
        elif isinstance(node, xy.ArrayLit):
            return ArrayObj(elems=[self.eval(elem) for elem in node.elems], xy_node=node)
        elif isinstance(node, xy.BinExpr):
            if node.op == ".":
                base = self.eval(node.arg1)
                assert isinstance(node.arg2, xy.Id)
                if isinstance(base, ImportObj):
                    # XXX assume c library
                    return ExtSpace(node.arg2.name)
                elif isinstance(base, TypeObj):
                    return base.fields[node.arg2.name]
                elif isinstance(base, VarObj):
                    if node.arg2.name not in base.type_desc.fields:
                        raise CompilationError(f"No field {node.arg2.name}", node.arg2)
                    return base.type_desc.fields[node.arg2.name]
                else:
                    raise CompilationError("Cannot evaluate", node)
        elif isinstance(node, xy.AttachTags):
            obj = self.eval(node.arg)
            if isinstance(obj, ConstObj):
                obj.tags = self.eval_tags(node.tags)
            elif isinstance(obj, TypeObj):
                base_type = obj
                obj = copy(obj)
                obj.base_type_obj = base_type
                obj.tags = self.eval_tags(node.tags, obj.tag_specs)
            else:
                raise CompilationError("Cannot assign tags", node)
            return obj
        else:
            raise CompilationError(
                "Cannot evaluate at compile time. "
                f"Unknown expression type '{type(node).__name__}'",
                node)
        
    def create_tmp_var(self, type_obj, name_hint="") -> VarObj:
        tmp_var_name = f"tmp{'_' if name_hint else ''}{name_hint}"
        tmp_var_name = f"{tmp_var_name}{self.tmp_var_i}"
        self.tmp_var_i += 1

        # TODO rewrite expression and call other func
        c_tmp = c.VarDecl(name=tmp_var_name, qtype=c.QualType(is_const=False))
        if isinstance(type_obj, ArrTypeObj):
            c_tmp.qtype.type.name = type_obj.base_type_obj.c_name
            c_tmp.qtype.type.dims = type_obj.dims
        else:
            c_tmp.qtype.type.name = type_obj.c_name

        if type_obj.init_value is not None:
            c_tmp.value = type_obj.init_value

        return VarObj(None, c_tmp, type_obj)
    
    def enter_block(self):
        # TODO implement
        self.tmp_var_i = 0

    def exit_block(self):
        # TODO implement
        pass
            

def compile_module(builder, module_name, asts):
    ctx = CompilerContext(builder, module_name)
    res = c.Ast()

    compile_import(xy.Import(lib="xy.builtins"), ctx, asts, res)
    ctx.void_obj = ctx.global_ns["void"]
    ctx.bool_obj = ctx.global_ns["bool"]
    ctx.ptr_obj = ctx.global_ns["Ptr"]
    ctx.size_obj = ctx.global_ns["Size"]
    ctx.tagctor_obj = ctx.global_ns["TagCtor"]
    ctx.uint_obj = ctx.global_ns["uint"]
    ctx.int_obj = ctx.global_ns["int"]
    ctx.prim_int_objs = (
        ctx.global_ns["byte"],
        ctx.global_ns["ubyte"],
        ctx.global_ns["short"],
        ctx.global_ns["ushort"],
        ctx.global_ns["int"],
        ctx.global_ns["uint"],
        ctx.global_ns["long"],
        ctx.global_ns["ulong"],
    )
    ctx.enum_obj = ctx.global_ns["Enum"]
    ctx.flags_obj = ctx.global_ns["Flags"]

    compile_header(ctx, asts, res)
    
    for ast in asts:
        compile_funcs(ctx, ast, res)
    
    maybe_add_main(ctx, res)

    mh = ModuleHeader(
        module_name=module_name,
        namespace=ctx.module_ns, str_prefix_reg=ctx.str_prefix_reg, ctx=ctx
    )

    for obj in ctx.module_ns.values():
        if isinstance(obj, FuncSpace):
            for func_obj in obj._funcs:
                func_obj.module_header = mh

    return mh, res

def compile_builtins(builder, module_name):
    ctx = CompilerContext(builder, module_name)
    res = c.Ast()

    import_builtins(ctx, res)

    return ModuleHeader(
        namespace=ctx.module_ns, str_prefix_reg=ctx.str_prefix_reg
    ), res

def compile_header(ctx: CompilerContext, asts, cast):
    for ast in asts:
        for node in ast:
            if isinstance(node, xy.Import):
                compile_import(node, ctx, ast, cast)

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.VarDecl):
                if node.value is None:
                    raise CompilationError(
                        "Global variables are threated as global constants. "
                        "They must have a compile-time known value",
                        node
                    )
                cdef = c.Define(
                    name=mangle_define(node.name, ctx.module_name),
                )
                ctx.module_ns[node.name] = VarObj(
                    xy_node=node,
                    c_node=cdef,
                )
                cast.consts.append(cdef)
                

    compile_structs(ctx, asts, cast)

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.VarDecl):
                _ = ctx.eval(node.value)
                value_obj = compile_expr(node.value, cast, None, ctx)
                ctx.module_ns[node.name].c_node.value = value_obj.c_node
                ctx.module_ns[node.name].type_desc = value_obj.infered_type

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.FuncDef):
                compile_func_prototype(node, cast, ctx)

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.FuncDef):
                fill_param_default_values(node, cast, ctx)

    return cast

def compile_structs(ctx: CompilerContext, asts, cast: c.Ast):
    # 1st pass - compile just the names
    for ast in asts:
        for node in ast:
            if isinstance(node, xy.StructDef):
                type_obj = TypeObj(
                    xy_node = node,
                )
                ctx.module_ns[node.name] = type_obj

    # 2nd pass - compile fields
    for ast in asts:
        for node in ast:
            if isinstance(node, xy.StructDef):
                type_obj = ctx.module_ns[node.name]
                fully_compile_type(type_obj, cast, ast, ctx)

def fully_compile_type(type_obj: TypeObj, cast, ast, ctx):
    if type_obj.fully_compiled:
        return
    
    tag_specs, tag_objs = ctx.split_and_eval_tags(type_obj.xy_node.tags, cast, ast)
    type_obj.tags.update(tag_objs)
    type_obj.tag_specs = tag_specs

    type_obj.is_enum = type_obj.tags.get("xy_enum", None) is ctx.enum_obj
    type_obj.is_flags = type_obj.tags.get("xy_flags", None) is ctx.flags_obj

    target_cast = None
    if isinstance(type_obj, ArrTypeObj):
        fully_compile_type(type_obj.base_type_obj, cast, ast, ctx)
        type_obj.c_node = c.Type(
            name=type_obj.base_type_obj.c_node.name,
            dims=type_obj.dims,
        )
    elif not (type_obj.is_enum or type_obj.is_flags):
        cstruct = c.Struct(name=mangle_struct(type_obj.xy_node, ctx))
        type_obj.c_node = cstruct
        cast.type_decls.append(c.Typedef("struct " + cstruct.name, cstruct.name))
        target_cast = cast.structs
    else:
        # use typedef and fill actual type latter
        cenum = c.Typedef(None, mangle_struct(type_obj.xy_node, ctx))
        type_obj.c_node = cenum
        target_cast = cast.type_decls

    # finaly compile fields
    if isinstance(type_obj, ArrTypeObj):
        assert len(type_obj.dims) == 1 # TODO implmenent multi dim
        for i in range(type_obj.dims[0]):
            type_obj.fields[i] = VarObj(
                xy_node=type_obj.xy_node, c_node=None,
                type_desc=type_obj.base_type_obj,
            )
        type_obj.init_value = c.StructLiteral(
            name=None,
            args=[c.Const(0)]
        )
    elif not (type_obj.is_enum or type_obj.is_flags):
        compile_struct_fields(type_obj, ast, cast, ctx)
    else:
        compile_enumflags_fields(type_obj, ast, cast, ctx)
        autogenerate_ops(type_obj, ast, cast, ctx)

    type_obj.fully_compiled = True
    if target_cast is not None:
        target_cast.append(type_obj.c_node)

def compile_struct_fields(type_obj, ast, cast, ctx):
    node = type_obj.xy_node
    cstruct = type_obj.c_node
    fields = {}
    default_values = []
    default_values_zeros = []
    for field in node.fields:
        field_type_obj = None
        if field.type is not None:
            field_type_obj = find_type(field.type, ctx)

        if field.is_pseudo:
            if field.value is None:
                raise CompilationError("All pseudo fields must have an explicit value")
            default_value_obj = ctx.eval(field.value)
            default_value_obj.c_node = compile_expr(field.value, cast, cast, ctx).c_node
            if field_type_obj is None:
                field_type_obj = default_value_obj.infered_type
            elif field_type_obj is not default_value_obj.infered_type:
                raise CompilationError("Explicit and infered types differ", field)
        elif field.value is not None:
            default_value_obj = ctx.eval(field.value)
            if field_type_obj is None:
                field_type_obj = default_value_obj.infered_type
            elif field_type_obj is not default_value_obj.infered_type:
                raise CompilationError("Explicit and infered types differ", field)
            dv_cnode = default_value_obj.c_node
            default_values.append(dv_cnode)
            default_values_zeros.append(isinstance(dv_cnode, c.Const) and dv_cnode.value == 0)
        else:
            fully_compile_type(field_type_obj, cast, ast, ctx)
            assert field_type_obj.init_value is not None
            default_value_obj = InstanceObj(type_obj=field_type_obj, xy_node=field)
            default_values.append(field_type_obj.init_value)
            default_values_zeros.append(field_type_obj.is_init_value_zeros)

        field_ctype = field_type_obj.c_node if isinstance(field_type_obj.c_node, c.Type) else field_type_obj.c_name
        cfield = c.VarDecl(
            name=mangle_field(field),
            qtype=c.QualType(field_ctype)
        )
        fields[field.name] = VarObj(
            xy_node=field,
            c_node=cfield,
            type_desc=field_type_obj,
            is_pseudo=field.is_pseudo,
            default_value_obj=default_value_obj
        )

        if not field.is_pseudo:
            cstruct.fields.append(cfield)
    type_obj.fields = fields

    if len(fields) == 0:
        cstruct.fields.append(c.VarDecl(
            name="__empty_structs_are_not_allowed_in_c__",
            qtype=c.QualType("char")
        ))

    all_zeros = all(default_values_zeros)
    c_init_args = [c.Const(0)] if all_zeros else default_values
    type_obj.init_value = c.StructLiteral(
        name=cstruct.name,
        args=c_init_args
    )
    type_obj.is_init_value_zeros = all_zeros

def compile_enumflags_fields(type_obj, ast, cast, ctx):
    node = type_obj.xy_node

    base_field = None

    # first we need to find the one non pseudo field:
    for field in node.fields:
        if not field.is_pseudo:
            if base_field is None:
                base_field = field
            else:
                raise CompilationError("Enums can have only 1 non pseudo field", field)

    base_type_obj = None
    if field.type is not None:
        base_type_obj = find_type(field.type, ctx)
        fully_compile_type(base_type_obj, cast, ast, ctx)
    else:
        raise CompilationError("An explicit type must be specified", field)

    if field.value is not None:
        raise CompilationError(
            "The default value for the enum is the value associated "
            "with the first flag", field)

    type_obj.c_node.typename = base_type_obj.c_name

    # go though the pseudo fields
    fields = {}
    next_num = 0
    init_value = None
    if type_obj.is_flags:
        init_value = base_type_obj.init_value

    for field in node.fields:
        if not field.is_pseudo:
            # this is the base field
            fields[field.name] = VarObj(
                xy_node=field,
                c_node=type_obj.c_node,
                type_desc=base_type_obj,
            )
            continue

        if field.type is not None:
            field_type = find_type(field.type, ctx)
            if field_type is not base_type_obj:
                raise CompilationError("Type mismatch", field)

        c_value = c.Const(next_num)
        if field.value is not None:
            state_obj = ctx.eval(field.value)
            c_value = state_obj.c_node
            if isinstance(c_value, c.Const) and isinstance(c_value.value, (float, int)):
                next_num = c_value.value
        if init_value is None:
            init_value = c_value

        cfield = c.Define(
            f"{type_obj.c_node.name}__{field.name}",
            value=c_value,
        )
        fields[field.name] = VarObj(
            xy_node=field,
            c_node=cfield,
            type_desc=type_obj,
            default_value_obj=ExprObj(
                xy_node=field,
                c_node=c.Id(cfield.name),
                infered_type=type_obj,
            )
        )
        cast.consts.append(cfield)

        next_num += 1
    type_obj.fields = fields

    if init_value is None:
        init_value = base_type_obj.init_value
    type_obj.init_value = init_value

def autogenerate_ops(type_obj: TypeObj, ast, cast, ctx):
    assert type_obj.is_enum or type_obj.is_flags

    base_field = None
    # first we need to find the one non pseudo field:
    for field in type_obj.fields.values():
        if not field.xy_node.is_pseudo:
            base_field = field
            break
    base_type = base_field.type_desc

    xy_node = type_obj.xy_node
    cmp_obj = ctx.eval_to_fspace(
        xy.Id("cmp", src=xy_node.src, coords=xy_node.coords),
        msg=f"Cannot find any functions cmp",
    ).find(
        xy.FuncCall(xy.Id("cmp"), src=xy_node.src, coords=xy_node.coords),
        ArgList([base_type, base_type]),
        ctx
    )
    if cmp_obj is None:
        raise CompilationError("Enum base fields need to be comparable", base_field.xy_node)
    
    gen_cmp_obj = copy(cmp_obj)
    # gen_cmp_obj.xy_node = type_obj.xy_node
    gen_cmp_obj.param_objs = [copy(param) for param in cmp_obj.param_objs]
    for param in gen_cmp_obj.param_objs:
        param.type_desc = type_obj
    ctx.ensure_func_space(xy.Id("cmp")).append(gen_cmp_obj)

    # autogen | and &
    gen_or_obj = FuncObj(
        xy_node=xy.FuncDef(
            name="bor",
            src=xy_node.src, coords=xy_node.coords,
        ),
        rtype_obj=type_obj,
        etype_obj=None,
        param_objs=[VarObj(type_desc=type_obj), VarObj(type_desc=type_obj)],
        builtin=True,
    )
    ctx.ensure_func_space(xy.Id("or")).append(gen_or_obj)

    gen_or_obj = FuncObj(
        xy_node=xy.FuncDef(
            name="band",
            src=xy_node.src, coords=xy_node.coords,
        ),
        rtype_obj=type_obj,
        etype_obj=None,
        param_objs=[VarObj(type_desc=type_obj), VarObj(type_desc=type_obj)],
        builtin=True,
    )
    ctx.ensure_func_space(xy.Id("and")).append(gen_or_obj)

def compile_func_prototype(node, cast, ctx):
    func_space = ctx.ensure_func_space(node.name)

    cfunc = c.Func(None)
    param_objs = []
    move_args_to_temps = False
    for param in node.params:
        param_obj = VarObj(xy_node=param, passed_by_ref=should_pass_by_ref(param))

        if param.value is not None:
            move_args_to_temps = True

        if param.type is not None:
            param_obj.type_desc = find_type(param.type, ctx)
        else:
            param_obj.type_desc = try_infer_type(param.value, ctx)

        if param_obj.type_desc:
            c_type = param_obj.type_desc.c_name
            if param_obj.passed_by_ref:
                c_type = c_type + "*"
        else:
            c_type = None

        if not param.is_pseudo:
            cparam = c.VarDecl(param.name, c.QualType(c_type))
            cfunc.params.append(cparam)
            param_obj.c_node = cparam

        param_objs.append(param_obj)
    if len(node.params) > 0 and not move_args_to_temps:
        move_args_to_temps = node.params[-1].is_pseudo

    expand_name = len(func_space) > 0
    if expand_name:
        check_params_have_types(param_objs, ctx)
    if len(func_space) == 1:
        # Already present. Expand name.
        func_desc = func_space[0]
        check_params_have_types(func_desc.param_objs, ctx)
        func_desc.c_node.name = mangle_def(
            func_desc.xy_node, func_desc.param_objs, ctx, expand=True
        )
    cfunc.name = mangle_def(node, param_objs, ctx, expand=expand_name)

    etype_compiled = None
    if return_by_param(node):
        for iret, ret in enumerate(node.returns):
            if ctx.eval(ret.type) is ctx.void_obj:
                rtype_compiled = ctx.void_obj
                assert len(node.returns) == 1
                continue
            param_name = f"__{ret.name}" if ret.name else f"_res{iret}"
            retparam = c.VarDecl(param_name, c.QualType(get_c_type(ret.type, ctx) + "*"))
            cfunc.params.append(retparam)
            rtype_compiled = ctx.get_compiled_type(ret.type)
        if node.etype is not None:
            etype_compiled = ctx.get_compiled_type(node.etype)
    elif len(node.returns) == 1:
        rtype_compiled = ctx.get_compiled_type(node.returns[0].type)
    else:
        rtype_compiled = ctx.void_obj

    if not isinstance(node.body, list) and len(node.returns) == 0:
        # shorthand notation
        ctx.push_ns()
        for pobj in param_objs:
            ctx.ns[pobj.xy_node.name] = pobj
        rtype_compiled = do_infer_type(node.body, ctx)
        ctx.pop_ns()

    if isinstance(rtype_compiled, TypeInferenceError):
        raise CompilationError(
            rtype_compiled.msg,
            node.returns[0] if len(node.returns) > 0 else node.body
        )
    cfunc.rtype = (etype_compiled.c_name
                    if etype_compiled is not None
                    else rtype_compiled.c_name)

    cast.func_decls.append(cfunc)
    compiled = FuncObj(
        node, cfunc, rtype_obj=rtype_compiled, etype_obj=etype_compiled,
        param_objs=param_objs, move_args_to_temps=move_args_to_temps
    )

    if node.etype is not None:
        compiled.etype_obj = ctx.get_compiled_type(node.etype)

    # compile tags
    compiled.tags = ctx.eval_tags(node.tags)
    if "xyStr" in compiled.tags:
        # TODO assert it is a StrCtor indeed
        str_lit = compiled.tags["xyStr"].kwargs["prefix"]
        prefix = str_lit.parts[0].value if len(str_lit.parts) else ""
        ctx.str_prefix_reg[prefix] = compiled
    if "xy.entrypoint" in compiled.tags:
        # TODO assert it is the correct type
        ctx.entrypoint_obj = compiled

    func_space.append(compiled)

    return compiled

def check_params_have_types(param_objs, ctx):
    for pobj in param_objs:
        if pobj.type_desc is None:
            do_infer_type(pobj.xy_node.value, ctx)
            raise CompilationError("Unreachable. Report Bug.", pobj.xy_node)

def fill_param_default_values(node, cast, ctx):
    fspace = ctx.eval_to_fspace(node.name)
    fobj : FuncObj = fspace.find(node, [], ctx)
    ctx.push_ns()
    for pobj in fobj.param_objs:
        if pobj.type_desc is not None:
            ctx.ns[pobj.xy_node.name] = pobj
            continue
        if pobj.xy_node.value is None:
            raise CompilationError("Cannot infer type", pobj.xy_node)
        type_obj = do_infer_type(pobj.xy_node.value, ctx)
        pobj.type_desc = type_obj

        c_type = pobj.type_desc.c_name
        if pobj.passed_by_ref:
            c_type = c_type + "*"
        pobj.c_node.qtype = c.QualType(c.Type(c_type))

        ctx.ns[pobj.xy_node.name] = pobj
    ctx.pop_ns()

def import_builtins(ctx: CompilerContext, cast):
    # always include it as it is everywhere
    cast.includes.append(c.Include("stdint.h"))
    cast.includes.append(c.Include("stddef.h"))
    cast.includes.append(c.Include("stdbool.h"))

    int_types = [
       "byte", "ubyte",
       "short", "ushort",
       "int", "uint",
       "long", "ulong",
       "Size", 
    ]
    num_types = [
       *int_types,
       "float", "double"
    ]

    ctype_map = {
        "byte": "int8_t", "ubyte": "uint8_t",
        "short": "int16_t", "ushort": "uint16_t",
        "int": "int32_t", "uint": "uint32_t",
        "long": "int64_t", "ulong": "uint64_t",
        "Size": "size_t",
        "float": "float", "double": "double",
        "Ptr": "void*", "bool": "bool",
        "void": "void",
    }

    for xtype, ctype in ctype_map.items():
        type_obj = TypeObj(
            xy_node=xy.StructDef(name=xtype),
            c_node=c.Struct(name=ctype),
            builtin=True,
            init_value=c.Const(0),
            fully_compiled=True,
        )
        type_obj.fields = {
            "": VarObj(type_desc=type_obj, xy_node=xy.VarDecl())
        }
        ctx.module_ns[xtype] = type_obj

    # fill in base math operations
    for p1, type1 in enumerate(num_types):
        for p2, type2 in enumerate(num_types):
            types = {type1, type2}
            if "Size" in types and ("float" in types or "double" in types):
                continue
            larger_type = type1 if p1 > p2 else type2
            for fname, rtype_name in [
                ("add", larger_type), ("mul", larger_type),
                ("sub", larger_type), ("div", larger_type),
                ("addEqual", type1), ("mulEqual", type1),
                ("subEqual", type1), ("divEqual", type1),
                ("cmp", larger_type),
            ]:
                func = xy.FuncDef(
                    fname,
                    params=[
                        xy.VarDecl("x", xy.Id(type1)),
                        xy.VarDecl("y", xy.Id(type2))
                    ],
                    returns=xy.SimpleRType(rtype_name)
                )
                desc = register_func(func, ctx)
                desc.builtin = True
                desc.rtype_obj = ctx.module_ns[rtype_name]
                desc.param_objs = [
                    VarObj(xy_node=xy.VarDecl(name="a"), type_desc=ctx.module_ns[type1]),
                    VarObj(xy_node=xy.VarDecl(name="b"), type_desc=ctx.module_ns[type2])
                ]

    for type in int_types:
        for fname in ["add", "sub"]:
            func = xy.FuncDef(
                fname,
                params=[
                    xy.VarDecl("x", xy.Id("Ptr")),
                    xy.VarDecl("y", xy.Id(type))
                ],
                returns=xy.SimpleRType("Ptr")
            )
            desc = register_func(func, ctx)
            desc.builtin = True
            desc.rtype_obj = ctx.module_ns["Ptr"]
            desc.param_objs = [
                VarObj(type_desc=ctx.module_ns["Ptr"]),
                VarObj(type_desc=ctx.module_ns[type])
            ]
    
    # fill in ++(inc) and --(dec)
    for type1 in num_types:
        for fname in ["inc", "dec"]:
            func = xy.FuncDef(
                fname,
                params=[
                    xy.VarDecl("x", xy.Id(type1)),
                ],
                returns=xy.SimpleRType(type1)
            )
            desc = register_func(func, ctx)
            desc.builtin = True
            desc.rtype_obj = ctx.module_ns[rtype_name]
            desc.param_objs = [
                VarObj(type_desc=ctx.module_ns[type1]),
            ]
    
    for int_type in int_types:
        select = xy.FuncDef(name="select", params=[
            xy.VarDecl("arr", xy.ArrayType(base=None)),
            xy.VarDecl("index", xy.Id(int_type)),
        ])
        select_obj = register_func(select, ctx)
        select_obj.builtin = True
        select_obj.rtype_obj = None
        select_obj.param_objs = [
            VarObj(type_desc=ArrTypeObj(base_type_obj=any_type_obj)),
            VarObj(type_desc=ctx.module_ns[int_type]),
        ]

    # tag construction
    tag_ctor = xy.StructDef(name="TagCtor", fields=[
        xy.VarDecl("label", type=None)
    ])
    tag_obj = TypeObj(tag_ctor, c.Struct("TagCtor"), builtin=True, fully_compiled=True)
    tag_obj.tags["xyTag"] = InstanceObj(
        kwargs={
            "label": StrObj(parts=[ConstObj(value="xyTag")])
        },
        type_obj=tag_obj
    )
    ctx.module_ns["TagCtor"] = tag_obj

    # string construction
    str_ctor = xy.StructDef(name="StrCtor", fields=[
        xy.VarDecl("prefix", type=None)
    ])
    str_obj = TypeObj(str_ctor, c.Struct("StrCtor"), builtin=True, fully_compiled=True)
    str_obj.tags["xyTag"] = InstanceObj(
        kwargs={
            "label": StrObj(parts=[ConstObj(value="xyStr")])
        },
        type_obj=tag_obj
    )
    ctx.module_ns["StrCtor"] = str_obj

    # iter construction
    iter_ctor = xy.StructDef(name="IterCtor")
    iter_ctor = TypeObj(str_ctor, c.Struct("IterCtor"), builtin=True, fully_compiled=True)
    iter_ctor.tags["xyTag"] = InstanceObj(
        kwargs={
            "label": StrObj(parts=[ConstObj(value="xyIter")])
        },
        type_obj=tag_obj
    )
    ctx.module_ns["IterCtor"] = iter_ctor

    # entry point
    entrypoint = xy.StructDef(name="EntryPoint")
    ep_obj = TypeObj(entrypoint, builtin=True, fully_compiled=True)
    ep_obj.tags["xyTag"] = InstanceObj(
        kwargs={
            "label": StrObj(parts=[ConstObj(value="xy.entrypoint")])
        }
    )
    ctx.module_ns["EntryPoint"] = ep_obj

    # clib
    clib = xy.StructDef(name="CLib")
    clib_ojb = TypeObj(clib, builtin=True)
    clib_ojb.tags["xyTag"] = InstanceObj(
        kwargs={
            "label": StrObj(parts=[ConstObj(value="xyc.lib")])
        }
    )
    ctx.module_ns["CLib"] = clib_ojb

    # typeof
    typeof = xy.FuncDef("typeof", params=[xy.VarDecl("val")])
    typeof_obj = register_func(typeof, ctx)
    typeof_obj.builtin = True
    typeof_obj.param_objs = [
        VarObj()
    ]

    # tagsof
    tagsof = xy.FuncDef("tagsof", params=[xy.VarDecl("val")])
    tagsof_obj = register_func(tagsof, ctx)
    tagsof_obj.builtin = True
    tagsof_obj.param_objs = [
        VarObj()
    ]

    # sizeof
    sizeof = xy.FuncDef("sizeof", params=[xy.VarDecl("val")])
    sizeof_obj = register_func(sizeof, ctx)
    sizeof_obj.builtin = True
    sizeof_obj.param_objs = [
        VarObj()
    ]

    # addrof
    addrof = xy.FuncDef("addrof", params=[xy.VarDecl("val")])
    addrof_obj = register_func(addrof, ctx)
    addrof_obj.builtin = True
    addrof_obj.param_objs = [
        VarObj()
    ]

    # Enum
    enum = xy.StructDef(name="Enum")
    enum_ojb = TypeObj(enum, builtin=True, fully_compiled=True)
    enum_ojb.tags["xyTag"] = InstanceObj(
        kwargs={
            "label": StrObj(parts=[ConstObj(value="xy_enum")])
        }
    )
    ctx.module_ns["Enum"] = enum_ojb

    # Flags
    flags = xy.StructDef(name="Flags")
    flags_ojb = TypeObj(flags, builtin=True, fully_compiled=True)
    flags_ojb.tags["xyTag"] = InstanceObj(
        kwargs={
            "label": StrObj(parts=[ConstObj(value="xy_flags")])
        }
    )
    ctx.module_ns["Flags"] = flags_ojb

def compile_funcs(ctx, ast, cast):
    for node in ast:
        if isinstance(node, xy.FuncDef):
            compile_func(node, ctx, ast, cast)
        elif isinstance(node, xy.Comment):
            pass
        elif not isinstance(node, (xy.StructDef, xy.Import, xy.VarDecl)):
            raise CompilationError(f"{type(node).__name__} not allowed here", node)

def compile_func(node, ctx, ast, cast):
    fspace = ctx.eval_to_fspace(node.name)
    fdesc = fspace.find(node, [], ctx)
    cfunc = fdesc.c_node

    param_objs = []
    ctx.push_ns()
    for param_obj in fdesc.param_objs:
        ctx.ns[param_obj.xy_node.name] = param_obj

    ctx.current_fobj = fdesc
    if isinstance(node.body, list):
        compile_body(node.body, cast, cfunc, ctx, is_func_body=True)
    else:
        # function shorthand notation
        gen_return = xy.Return(node.body)
        obj_ret = compile_return(gen_return, cast, cfunc, ctx)
        cfunc.body.append(obj_ret.c_node)
        cfunc.rtype = obj_ret.infered_type.c_name
    ctx.current_fobj = None

    cast.funcs.append(cfunc)
    ctx.pop_ns()

def compile_body(body, cast, cfunc, ctx, is_func_body=False):
    ctx.enter_block()
    for node in body:
        if isinstance(node, xy.Comment):
            continue
        if isinstance(node, xy.Return):
            obj = compile_return(node, cast, cfunc, ctx)
            cfunc.body.append(obj.c_node)
        elif isinstance(node, xy.Error):
            obj = compile_error(node, cast, cfunc, ctx)
            cfunc.body.append(obj.c_node)
        elif isinstance(node, xy.VarDecl):
            vardecl_obj = compile_vardecl(node, cast, cfunc, ctx)
            cfunc.body.append(vardecl_obj.c_node)
        else:
            expr_obj = compile_expr(node, cast, cfunc, ctx)
            if expr_obj.c_node is not None:
                cfunc.body.append(expr_obj.c_node)
    if is_func_body and ctx.current_fobj.etype_obj is not None:
        if len(body) == 0 or not isinstance(body[-1], xy.Return):
            cfunc.body.append(c.Return(ctx.current_fobj.etype_obj.init_value))
    ctx.exit_block()

def compile_vardecl(node, cast, cfunc, ctx):
    cvar = c.VarDecl(name=node.name, qtype=c.QualType(is_const=not node.varying))
    value_obj = compile_expr(node.value, cast, cfunc, ctx) if node.value is not None else None
    type_desc = find_type(node.type, ctx) if node.type is not None else None
    if type_desc is None:
        if value_obj is None:
            raise CompilationError(
                "Cannot create variable with no type and no value",
                node
            )
        type_desc = value_obj.infered_type
        if isinstance(type_desc, TypeInferenceError):
            raise CompilationError(
                type_desc.msg,
                node
            )
    if isinstance(type_desc, ArrTypeObj):
        cvar.qtype.type.name = type_desc.base_type_obj.c_name
        cvar.qtype.type.dims = type_desc.dims
    else:
        cvar.qtype.type.name = type_desc.c_name
    res_obj = VarObj(node, cvar, type_desc)
    ctx.ns[node.name] = res_obj

    if node.value is not None:
        cvar.value = value_obj.c_node
    if node.value is None and isinstance(type_desc, ArrTypeObj):
        cvar.value = c.InitList()
    if cvar.value is None:
        cvar.value = type_desc.init_value

    return res_obj

c_symbol_type = TypeInferenceError(
    "The types of c symbols cannot be inferred. Please be explicit and specify the type."
)

def compile_expr(expr, cast, cfunc, ctx: CompilerContext, lhs=False) -> ExprObj:
    if isinstance(expr, xy.Const):
        return ExprObj(
            xy_node=expr,
            c_node=c.Const(expr.value_str),
            infered_type=ctx.get_compiled_type(expr.type)
        )
    elif isinstance(expr, xy.BinExpr):
        if expr.op not in {'.', '=', '.='}:
            return compile_binop(expr, cast, cfunc, ctx)
        elif expr.op == '.':
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx)
            assert isinstance(expr.arg2, xy.Id)
            field_name = expr.arg2.name
            if isinstance(arg1_obj.infered_type, ImportObj):
                assert arg1_obj.infered_type.is_external
                res = c.Id(field_name)
                return ExprObj(
                    c_node=res,
                    infered_type=c_symbol_type
                )
            elif arg1_obj.infered_type is tag_list_type_obj:
                if field_name not in arg1_obj.tags:
                    raise CompilationError(f"No tag '{field_name}'", expr)
                type_obj = arg1_obj.tags[field_name]
                return ExprObj(
                    c_node=c.Id(type_obj.c_node.name),
                    infered_type=type_obj,
                )
            else:
                struct_obj = arg1_obj.infered_type
                if field_name not in struct_obj.fields:
                    raise CompilationError(f"No such field in struct {struct_obj.xy_node.name}", expr.arg2)
                return field_get(arg1_obj, struct_obj.fields[field_name], cast, cfunc, ctx, lhs)
        elif expr.op == '.=':
            if not (isinstance(expr.arg2, xy.StructLiteral) and expr.arg2.name is None):
                raise CompilationError("The right hand side of the '.=' operator must be an anonymous struct literal")
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx, lhs=True)
            val_obj = do_compile_struct_literal(expr.arg2, arg1_obj.infered_type, arg1_obj, cast, cfunc, ctx)
            return ExprObj(
                c_node=None,
                infered_type=arg1_obj.infered_type
            ) 
        else:
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx, lhs=True)
            arg2_obj = compile_expr(expr.arg2, cast, cfunc, ctx)
            if isinstance(arg1_obj, RefObj):
                return ref_set(arg1_obj, arg2_obj, cast, cfunc, ctx)
            else:
                res = c.Expr(arg1_obj.c_node, arg2_obj.c_node, op=expr.op)
                return ExprObj(
                    xy_node=expr,
                    c_node=res,
                    infered_type=arg2_obj.infered_type
                )
    elif isinstance(expr, xy.UnaryExpr):
        fcall = rewrite_unaryop(expr, ctx)
        return compile_expr(fcall, cast, cfunc, ctx)
    elif isinstance(expr, xy.Id):
        var_obj = ctx.eval(expr)
        if isinstance(var_obj, VarObj):
            c_node = c.Id(var_obj.c_node.name) if var_obj.c_node is not None else None
            if var_obj.passed_by_ref:
                c_node = c.UnaryExpr(c_node, op="*", prefix=True)
            return ExprObj(
                xy_node=expr,
                c_node=c_node,
                infered_type=var_obj.type_desc
            )
        elif isinstance(var_obj, TypeObj):
            return ExprObj(
                xy_node=expr,
                c_node=c.Id(var_obj.c_node.name),
                infered_type=var_obj,
                compiled_obj=var_obj
            )
        elif isinstance(var_obj, ImportObj):
            return ExprObj(
                c_node=None,
                xy_node=var_obj.xy_node,
                infered_type=var_obj
            )
        elif isinstance(var_obj, ExprObj):
            return var_obj
        else:
            raise CompilationError("Invalid expression", expr)
    elif isinstance(expr, xy.FuncCall):
        return compile_fcall(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.StructLiteral):
        return compile_struct_literal(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.StrLiteral):
        return compile_strlit(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.ArrayLit):
        res = c.InitList()
        arr_type = "Cannot infer type of empty list"
        for elem in expr.elems:
            elem_expr = compile_expr(elem, cast, cfunc, ctx)
            res.elems.append(elem_expr.c_node)
            arr_type = elem_expr.infered_type
        return ExprObj(
            xy_node=expr,
            c_node=res,
            infered_type=ArrTypeObj(base_type_obj=arr_type, dims=[len(expr.elems)])
        )
    elif isinstance(expr, xy.Select):
        rewritten = rewrite_select(expr, ctx)
        return compile_expr(rewritten, cast, cfunc, ctx)
    elif isinstance(expr, xy.IfExpr):
        return compile_if(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.DoWhileExpr):
        return compile_dowhile(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.WhileExpr):
        return compile_while(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.ForExpr):
        return compile_for(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.Break):
        return compile_break(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.AttachTags):
        obj = compile_expr(expr.arg, cast, cfunc, ctx)
        obj.tags = ctx.eval_tags(expr.tags)
        return obj
    elif isinstance(expr, xy.SliceExpr):
        # rewrite slice
        kwargs = {}
        if expr.start is not None:
            kwargs["start"] = expr.start
        if expr.end is not None:
            kwargs["end"] = expr.end
        if expr.step is not None:
            kwargs["step"] = expr.step
        slice_ctor_fcall = xy.FuncCall(
            xy.Id("slice", src=expr.src, coords=expr.coords),
            kwargs=kwargs,
            src=expr.src,
            coords=expr.coords
        )
        return compile_fcall(slice_ctor_fcall, cast, cfunc, ctx)
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)
    
def ref_get(ref_obj: RefObj, cast, cfunc, ctx: CompilerContext):
    obj = ref_obj.container
    struct_obj = obj if isinstance(obj, TypeObj) else obj.infered_type
    if not (struct_obj.is_enum or struct_obj.is_flags):
        return find_and_call(
            "get",
            ArgList([
                ref_obj.container,
                ref_obj.ref,
            ]),
            cast, cfunc, ctx, ref_obj.xy_node
        )
    elif struct_obj.is_enum:
        # field of an enum
        if isinstance(ref_obj.container, TypeObj) or isinstance(ref_obj.container, ExprObj) and struct_obj is obj.compiled_obj:
            res = c.Id(ref_obj.ref.c_node.name)
        else:
            res = c.Expr(
                op='==',
                arg1=obj.c_node,
                arg2=c.Id(ref_obj.ref.c_node.name)
            )
    else:
        assert struct_obj.is_flags
        if isinstance(obj, TypeObj) or isinstance(obj, ExprObj) and struct_obj is obj.compiled_obj:
            res = c.Id(ref_obj.ref.c_node.name)
        else:
            res = c.Expr(
                op='&',
                arg1=obj.c_node,
                arg2=c.Id(ref_obj.ref.c_node.name)
            )

    return ExprObj(
        c_node=res,
        xy_node=ref_obj.xy_node,
        infered_type=struct_obj
    )

def ref_set(ref_obj: RefObj, val_obj: CompiledObj, cast, cfunc, ctx: CompilerContext):
    if not ref_obj.container.infered_type.is_flags:
        return find_and_call(
            "set",
            ArgList([
                ref_obj.container,
                ref_obj.ref,
                val_obj,
            ]),
            cast, cfunc, ctx, ref_obj.xy_node
        )
    else:
        return ExprObj(
            xy_node=ref_obj.xy_node,
            infered_type=ref_obj.container.infered_type,
            c_node=c.Expr(
                arg1=ref_obj.container.c_node,
                arg2=ref_obj.ref.c_node,
                op="|=",
            )
        )

def field_set(obj: CompiledObj, field: VarObj, val: CompiledObj, cast, cfunc, ctx: CompilerContext):
    if isinstance(obj, VarObj):
        obj = ExprObj(
            xy_node=obj.xy_node,
            c_node=c.Id(obj.c_node.name),
            infered_type=obj.type_desc,
        )
    if not field.is_pseudo:
        val_type = val.infered_type
        is_arr_assign = isinstance(val_type, ArrTypeObj)
        if is_arr_assign:
            tmp_obj = ctx.create_tmp_var(val_type)
            tmp_obj.c_node.value = val.c_node
            cfunc.body.append(tmp_obj.c_node)
            c_res = c.FuncCall(
                "memcpy",
                args=[
                    c.UnaryExpr(
                        c_deref(obj.c_node, field=c.Id(field.c_node.name)),
                        op="&",
                        prefix=True,
                    ),
                    c.UnaryExpr(
                        c.Id(tmp_obj.c_node.name),
                        op="&",
                        prefix=True,
                    ),
                    c.Expr(
                        c.Const(val_type.dims[0]),
                        c.FuncCall("sizeof", args=[c.Id(val_type.base_type_obj.c_name)]),
                        op="*"
                    )
                ]
            )
        else:
            # non array field
            c_res = c.Expr(
                c_deref(obj.c_node, field=c.Id(field.c_node.name)),
                val.c_node,
                op="=",
            )

        return ExprObj(
            c_node=c_res,
        )
    else:
        ref_obj = RefObj(
            container=obj,
            ref=field.default_value_obj,
            xy_node=val.xy_node,
        )
        return ref_set(ref_obj, val, cast, cfunc, ctx)
    
def field_get(obj: CompiledObj, field_obj: VarObj, cast, cfunc, ctx: CompilerContext, lhs=False):
    struct_obj = obj if isinstance(obj, TypeObj) else obj.infered_type
    if field_obj.xy_node.is_pseudo:
        ref_obj = RefObj(
            container=obj,
            ref=field_obj.default_value_obj,
            xy_node=obj.xy_node,
        )
        if obj.xy_node is None:
            import pdb; pdb.set_trace()
        if lhs:
            return ref_obj
        else:
            return ref_get(ref_obj, cast, cfunc, ctx)

    if not (struct_obj.is_enum or struct_obj.is_flags):
        # normal field
        res = c_deref(obj.c_node, field=c.Id(field_obj.c_node.name))
    elif struct_obj.is_enum:
        # field of an enum
        if isinstance(obj, TypeObj) or isinstance(obj, ExprObj) and struct_obj is obj.compiled_obj:
            res = c.Id(field_obj.c_node.name)
        else:
            res = c.Expr(
                op='==',
                arg1=obj.c_node,
                arg2=c.Id(field_obj.c_node.name)
        )
    else:
        assert struct_obj.is_flags
        if isinstance(obj, TypeObj) or isinstance(obj, ExprObj) and struct_obj is obj.compiled_obj:
            res = c.Id(field_obj.c_node.name)
        else:
            res = c.Expr(
                op='&',
                arg1=obj.c_node,
                arg2=c.Id(field_obj.c_node.name)
            )

    return ExprObj(
        c_node=res,
        xy_node=obj.xy_node,
        infered_type=field_obj.type_desc
    )
    

def compile_struct_literal(expr, cast, cfunc, ctx: CompilerContext):
    type_obj = ctx.eval(expr.name, msg="Cannot find type")
    tmp_obj = None
    if not isinstance(type_obj, TypeObj):
        assert isinstance(type_obj, VarObj)
        var_obj = type_obj
        type_obj = type_obj.type_desc
        if not type_obj.is_flags:
            tmp_obj = ctx.create_tmp_var(type_obj)
            tmp_obj.c_node.value = c.Id(var_obj.c_node.name)
            cfunc.body.append(tmp_obj.c_node)
        else:
            tmp_obj = var_obj

    return do_compile_struct_literal(expr, type_obj, tmp_obj, cast, cfunc, ctx)

def do_compile_struct_literal(expr, type_obj, tmp_obj, cast, cfunc, ctx: CompilerContext):
    fully_compile_type(type_obj, cast, None, ctx)
    if type_obj.is_flags:
        return do_compile_flags_literal(expr, type_obj, tmp_obj, cast, cfunc, ctx)

    expr_args = expr.args
    expr_kwargs = copy(expr.kwargs)

    # map positional and named fields
    name_to_pos = {}
    num_real_fields = 0
    for fname, fobj in type_obj.fields.items():
        if not fobj.xy_node.is_pseudo:
            name_to_pos[fname] = num_real_fields
            num_real_fields += 1
    pos_objs = [None] * num_real_fields
    named_objs = {}
    field_objs = list(type_obj.fields.values())

    any_pseudos = False
    for i, arg in enumerate(expr_args):
        val_obj = compile_expr(arg, cast, cfunc, ctx)
        named_objs[field_objs[i].xy_node.name] = val_obj
        if field_objs[i].xy_node.is_pseudo:
            any_pseudos = True
        if not any_pseudos:
            pos_objs[i] = compile_expr(arg, cast, cfunc, ctx)

    for name, arg in expr_kwargs.items():
        if name not in type_obj.fields:
            raise CompilationError(f"No field named '{name}", arg)
        if name in named_objs:
            raise CompilationError(f"Field {name} already set", arg)
        named_objs[name] = compile_expr(arg, cast, cfunc, ctx)
        if type_obj.fields[name].xy_node.is_pseudo:
            any_pseudos = True
        if not any_pseudos:
            i = name_to_pos[name]
            pos_objs[i] = named_objs[name]

    # create tmp if needed
    injected_tmp = False
    if tmp_obj is None and any_pseudos:
        tmp_obj = ctx.create_tmp_var(type_obj)
        cfunc.body.append(tmp_obj.c_node)
        injected_tmp = True

    # eliminate any trailing zeros
    last_non_zero_idx = 0
    for i in range(len(pos_objs) - 1, -1, -1):
        if pos_objs[i] is not None:
            last_non_zero_idx = i+1
            break
    pos_objs = pos_objs[:last_non_zero_idx]

    c_args = []
    if tmp_obj is None or injected_tmp:
        for i, obj in enumerate(pos_objs):
            if obj is not None:
                c_args.append(obj.c_node)
            else:
                c_args.append(field_objs[i].type_desc.init_value)

    if injected_tmp:
        pos_to_name = list(name_to_pos.keys())
        for i in range(len(c_args)):
            del named_objs[pos_to_name[i]]

        if len(c_args) > 0:
            tmp_obj.c_node.value = c.StructLiteral(
                name=type_obj.c_name,
                args=c_args,
            )
        else:
            tmp_obj.c_node.value = type_obj.init_value       

    if tmp_obj is None:
        # creating a new struct
        if len(pos_objs) != 0:
            ctypename = type_obj.c_name
            res = c.StructLiteral(
                name=ctypename,
                args=c_args,
            )
        else:
            res = type_obj.init_value
    else:
        # craeting a new struct from an existing one
        for fname, fval_obj in named_objs.items():
            field = type_obj.fields[fname]
            obj = field_set(tmp_obj, field, fval_obj, cast, cfunc, ctx)
            cfunc.body.append(obj.c_node)
        res = c.Id(tmp_obj.c_node.name)

    
    return ExprObj(
        xy_node=expr,
        c_node=res,
        infered_type=type_obj
    )

def do_compile_flags_literal(expr, type_obj, tmp_obj, cast, cfunc, ctx: CompilerContext):
    res = None if tmp_obj is None else c.Id(tmp_obj.c_node.name)
    field_objs = list(type_obj.fields)
    for i, arg in enumerate(expr.args):
        if field_objs[i].xy_node.is_pseudo:
            val_obj = field_get(type_obj, field_objs[i], cast, cfunc, ctx)
            if res is not None:
                res = c.Expr(
                    res,
                    val_obj.c_node,
                    op="|"
                )
            else:
                res = val_obj.c_node

    for fname, arg in expr.kwargs.items():
        if fname not in type_obj.fields:
            raise CompilationError(f"No field '{fname}'", arg)
        if type_obj.fields[fname].xy_node.is_pseudo:
            val_obj = field_get(type_obj, type_obj.fields[fname], cast, cfunc, ctx)
            if res is not None:
                res = c.Expr(
                    res,
                    val_obj.c_node,
                    op="|"
                )
            else:
                res = val_obj.c_node

    if res is None:
        res = c.Const(0)

    return ExprObj(
        xy_node=expr,
        c_node=res,
        infered_type=type_obj
    )

def should_pass_by_ref(param: xy.VarDecl):
    return param.is_out or param.is_inout

def c_deref(c_node, field=None):
    if isinstance(c_node, c.UnaryExpr) and c_node.op == "*" and c_node.prefix:
        return c.Expr(c_node.arg, field, op='->') 
    return c.Expr(c_node, field, op='.')

def c_getref(c_node):
    if isinstance(c_node, c.UnaryExpr) and c_node.op == "*" and c_node.prefix:
        return c_node.arg
    return c.UnaryExpr(c_node, op='&', prefix=True)

def try_infer_type(expr, ctx):
    try:
        return do_infer_type(expr, ctx)
    except CompilationError:
        return None
    
def do_infer_type(expr, ctx):
    if isinstance(expr, xy.StructLiteral):
        return ctx.get_compiled_type(expr.name)
    try:
        return compile_expr(expr, None, None, ctx).infered_type
    except CompilationError as e:
        raise CompilationError(
            f"Cannot infer type because: {e.error_message}", e.xy_node,
            notes=e.notes
        )

def compile_strlit(expr, cast, cfunc, ctx: CompilerContext):
    if expr.prefix not in ctx.str_prefix_reg:
        raise CompilationError(
            f"No string constructor registered for prefix \"{expr.prefix}\"",
            expr
        )
    func_desc: FuncObj = ctx.str_prefix_reg[expr.prefix]

    interpolation = ("interpolation" in func_desc.tags["xyStr"].kwargs and
                     ct_isTrue(func_desc.tags["xyStr"].kwargs["interpolation"]))
    if not interpolation:
        is_error = len(expr.parts) > 1
        if not is_error and len(expr.parts) == 1:
            is_error = not isinstance(expr.parts[0], xy.Const)
        if is_error:
            raise CompilationError(
                f"Interpolation is not enabled for prefix \"{expr.prefix}\"",
                expr
            )
    
    if not interpolation:
        str_const = expr.parts[0].value if len(expr.parts) else ""
        c_func = c.FuncCall(func_desc.c_name, args=[
            c.Const(f'"{str_const}"'),
            c.Const(cstr_len(str_const)),
        ])
        return ExprObj(
            c_node=c_func,
            infered_type=func_desc.rtype_obj
        )
    else:
        builder_tmpvar = ctx.create_tmp_var(func_desc.rtype_obj, f"{expr.prefix}str")
        cfunc.body.append(builder_tmpvar.c_node)
        ctx.ns[builder_tmpvar.c_node.name] = builder_tmpvar
        builder_tmpvar_id = ExprObj(
            xy_node=expr,
            c_node=c.Id(builder_tmpvar.c_node.name),
            infered_type=func_desc.rtype_obj
        )
        builder_tmpvar.c_node.value = do_compile_fcall(
            expr=expr,
            func_obj=func_desc,
            arg_exprs=ArgList([
                ConstObj(c_node=c.Const(f'"{expr.full_str}"'), value=""),
                ConstObj(c_node=c.Const(cstr_len(expr.full_str)), value=0)
            ]),
            cast=cast,
            cfunc=cfunc,
            ctx=ctx
        ).c_node
        for part in expr.parts:
            if is_str_const(part):
                append_call = find_and_call(
                    "append",
                    ArgList([
                        builder_tmpvar_id,
                        ExprObj(c_node=c.Const('"' + part.value + '"'), infered_type=ctx.ptr_obj),
                        ExprObj(c_node=c.Const(cstr_len(part.value)), infered_type=ctx.size_obj),
                    ]),
                    cast,
                    cfunc,
                    ctx,
                    xy_node=expr,
                )
                cfunc.body.append(append_call.c_node)
            else:
                assert isinstance(part, xy.Args)
                if part.is_introspective:
                    part_str = part.args[0].src.code[part.args[0].coords[0]:part.args[0].coords[1]] + "="
                    append_call = find_and_call(
                        "append",
                        ArgList([
                            builder_tmpvar_id,
                            ExprObj(c_node=c.Const('"' + part_str + '"'), infered_type=ctx.ptr_obj),
                            ExprObj(c_node=c.Const(cstr_len(part_str)), infered_type=ctx.size_obj),
                        ]),
                        cast,
                        cfunc,
                        ctx,
                        xy_node=expr,
                    )
                    cfunc.body.append(append_call.c_node)
                gen_fcall = xy.FuncCall(
                    xy.Id("append", src=part.src, coords=part.coords),
                    args=[xy.Id(builder_tmpvar.c_node.name, src=part.src, coords=part.coords)] + part.args,
                    kwargs=part.kwargs,
                    src=part.src,
                    coords=part.coords
                )
                append_call = compile_fcall(gen_fcall, cast, cfunc, ctx)
                cfunc.body.append(append_call.c_node)
        
        to_obj = func_desc.tags["xyStr"].kwargs.get("to", None)
        if to_obj is not None:
            return find_and_call(
                "to",
                ArgList([
                    builder_tmpvar_id,
                    ExprObj(
                        c_node=c.Id(to_obj.c_node.name),
                        infered_type=to_obj
                    )
                ]),
                cast,
                cfunc,
                ctx,
                xy_node=expr
            )
        else:
            return builder_tmpvar_id
    
def is_str_const(node: xy.Node) -> bool:
    return isinstance(node, xy.Const) and isinstance(node.value, str)


def ct_isTrue(obj: CompiledObj):
    if isinstance(obj, ConstObj) and isinstance(obj.value, bool):
        return obj.value
    raise CompilationError(
        "Should be true or false",
        obj.xy_node
    )

def cstr_len(s: str) -> int:
    res = 0
    i = 0
    while i < len(s):
        res += 1
        if s[i] == '\\':
            i += 2
        else:
            i += 1
    return res

def compile_fcall(expr: xy.FuncCall, cast, cfunc, ctx: CompilerContext):
    arg_exprs = ArgList()
    expr_to_move_idx = None
    for i in range(len(expr.args)):
        obj = compile_expr(expr.args[i], cast, cfunc, ctx)
        if cfunc is not None and not is_simple_cexpr(obj.c_node):
            is_builitin_math = (
                expr_to_move_idx is not None and
                arg_exprs[expr_to_move_idx].infered_type.builtin and obj.infered_type.builtin
                and isinstance(expr.name, xy.Id) and expr.name.name in {"add", "sub", "mul", "div"}
            )
            if expr_to_move_idx is not None and not is_builitin_math:
                tmp_obj = move_to_temp(arg_exprs[expr_to_move_idx], cast, cfunc, ctx)
                arg_exprs[expr_to_move_idx] = tmp_obj
            expr_to_move_idx = i

        arg_exprs.args.append(obj)
    if len(expr.kwargs) > 0 and expr_to_move_idx is not None:
        arg_exprs[expr_to_move_idx] = maybe_move_to_temp(
            arg_exprs[expr_to_move_idx], cast, cfunc, ctx
        )
        expr_to_move_idx = None
    for pname, pexpr in expr.kwargs.items():
        obj = compile_expr_for_arg(pexpr, cast, cfunc, ctx)
        arg_exprs.kwargs[pname] = obj

    arg_infered_types = ArgList(
        args=[arg.infered_type for arg in arg_exprs.args],
        kwargs={key: arg.infered_type for key, arg in arg_exprs.kwargs.items()}
    )

    fspace = ctx.eval_to_fspace(expr.name)
    func_obj = fspace.find(expr, arg_infered_types, ctx)

    if expr_to_move_idx is not None and func_obj.move_args_to_temps:
        arg_exprs[expr_to_move_idx] = maybe_move_to_temp(
            arg_exprs[expr_to_move_idx], cast, cfunc, ctx
        )

    return do_compile_fcall(expr, func_obj, arg_exprs, cast, cfunc, ctx)

def compile_expr_for_arg(arg: xy.Node, cast, cfunc, ctx: CompilerContext):
    expr_obj = compile_expr(arg, cast, cfunc, ctx)
    return maybe_move_to_temp(expr_obj, cast, cfunc, ctx)

def maybe_move_to_temp(expr_obj, cast, cfunc, ctx):
    if cfunc is not None and not is_simple_cexpr(expr_obj.c_node):
        return move_to_temp(expr_obj, cast, cfunc, ctx)
    else:
        return expr_obj
    
def move_to_temp(expr_obj, cast, cfunc, ctx):
    tmp_obj = ctx.create_tmp_var(expr_obj.infered_type, name_hint="arg")
    tmp_obj.c_node.value = expr_obj.c_node
    cfunc.body.append(tmp_obj.c_node)
    return ExprObj(
        xy_node=expr_obj.xy_node,
        c_node=c.Id(tmp_obj.c_node.name),
        infered_type=expr_obj.infered_type,
        tags=expr_obj.tags
    )

def is_simple_cexpr(expr):
    if isinstance(expr, (c.Id, c.Const)):
        return True
    if isinstance(expr, c.Expr):
        return is_simple_cexpr(expr.arg1) and is_simple_cexpr(expr.arg2)
    if isinstance(expr, c.UnaryExpr):
        return is_simple_cexpr(expr.arg)
    if isinstance(expr, c.StructLiteral):
        return all(is_simple_cexpr(e) for e in expr.args)
    if isinstance(expr, c.Index):
        return is_simple_cexpr(expr.expr) and is_simple_cexpr(expr.index)
    return False 
    

def find_and_call(name: str, arg_objs, cast, cfunc, ctx, xy_node):
    fobj = ctx.eval_to_fspace(
        xy.Id(name, src=xy_node.src, coords=xy_node.coords),
        msg=f"Cannot find any functions {name}",
    ).find(
        xy.FuncCall(xy.Id(name), src=xy_node.src, coords=xy_node.coords),
        ArgList([obj.infered_type for obj in arg_objs]),
        ctx
    )
    return do_compile_fcall(
        xy_node,
        fobj,
        arg_exprs=arg_objs,
        cast=cast, cfunc=cfunc, ctx=ctx
    )

def do_compile_fcall(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    if func_obj.builtin and func_obj.xy_node.name == "select":
        # TODO what if args is more numerous
        assert len(arg_exprs) == 2
        res = c.Index(
            arg_exprs[0].c_node,
            arg_exprs[1].c_node,
        )
        return ExprObj(
            xy_node=expr,
            c_node=res,
            infered_type=arg_exprs[0].infered_type.base_type_obj
        )
    elif func_obj.builtin and len(arg_exprs) == 2 and func_obj.xy_node.name != "cmp":
        func_to_op_map = {
            "add": '+',
            "sub": '-',
            "mul": '*',
            "div": '/',
            "addEqual": "+=",
            "subEqual": "-=",
            "mulEqual": "*=",
            "divEqual": "/=",
            "or": "||",
            "opEqual": "||=",
            "and": "&&",
            "andEqual": "&&=",
            "bor": "|",
            "band": "&"
        }
        c_arg1 = arg_exprs[0].c_node
        if func_obj.rtype_obj == ctx.ptr_obj:
            # TODO what if function returns multiple values if len(func_obj.xy_node.returns) == 1
            # TODO what if Ptr has an attached type
            c_arg1 = c.Cast(c_arg1, to="int8_t*")
        res = c.Expr(
            c_arg1, arg_exprs[1].c_node,
            op=func_to_op_map[func_obj.xy_node.name]
        )
        return ExprObj(
            xy_node=func_obj.xy_node,
            c_node=res,
            infered_type=func_obj.rtype_obj
        )
    elif func_obj.builtin and func_obj.xy_node.name == "cmp":
        res = c.Expr(arg_exprs[0].c_node, arg_exprs[1].c_node, op="-")
        return ExprObj(
            c_node=res,
            xy_node=expr,
            infered_type=func_obj.rtype_obj
        )
    elif func_obj.builtin and func_obj.xy_node.name == "typeof":
        return ExprObj(
            c_node=c.Id(arg_exprs[0].infered_type.c_node.name),
            infered_type=arg_exprs[0].infered_type,
            tags=arg_exprs[0].infered_type.tags
        )
    elif func_obj.builtin and func_obj.xy_node.name == "tagsof":
        return ExprObj(
            infered_type=tag_list_type_obj,
            tags=arg_exprs[0].tags
        )
    elif func_obj.builtin and func_obj.xy_node.name == "sizeof":
        return ExprObj(
            c_node=c.FuncCall("sizeof", [arg_exprs[0].c_node]),
            infered_type=ctx.size_obj
        )
    elif func_obj.builtin and func_obj.xy_node.name == "addrof":
        return ExprObj(
            c_node=c.UnaryExpr(arg=arg_exprs[0].c_node, op="&", prefix=True),
            infered_type=ctx.ptr_obj
        )
    elif func_obj.builtin:
        assert len(arg_exprs) == 1
        func_to_op_map = {
            "inc": '++',
            "dec": '--',
        }
        res = c.UnaryExpr(
            arg=arg_exprs[0].c_node,
            op=func_to_op_map[expr.name.name]
        )
        return ExprObj(
            c_node=res,
            xy_node=expr,
            infered_type=func_obj.rtype_obj
        )

    default_val_ctx = ctx
    if func_obj.module_header is not None:
        default_val_ctx = func_obj.module_header.ctx
    res = c.FuncCall(name=func_obj.c_name)
    if func_obj.xy_node is not None:
        default_val_ctx.push_ns()
        for pobj, arg in zip(func_obj.param_objs, arg_exprs.args):
            default_val_ctx.ns[pobj.xy_node.name] = arg
            if pobj.xy_node.is_pseudo:
                continue
            if pobj.passed_by_ref:
                res.args.append(c_getref(arg.c_node))
            else:
                res.args.append(arg.c_node)

        for pobj in func_obj.param_objs[len(arg_exprs.args):]:
            if pobj.xy_node.name not in arg_exprs.kwargs:
                default_obj = compile_expr(pobj.xy_node.value, cast, cfunc, default_val_ctx)
                res.args.append(default_obj.c_node)
            else:
                res.args.append(arg_exprs.kwargs[pobj.xy_node.name].c_node)
        default_val_ctx.pop_ns()
    else:
        # external c function
        for arg in arg_exprs:
            res.args.append(arg.c_node)

    if (
        func_obj.xy_node is not None and
        (func_obj.etype_obj is not None or len(func_obj.xy_node.returns) > 1)
    ):
        tmp_cid = None
        if func_obj.rtype_obj is not ctx.void_obj:
            tmp_obj = ctx.create_tmp_var(func_obj.rtype_obj, name_hint="res")
            cfunc.body.append(tmp_obj.c_node)
            tmp_cid = c.Id(tmp_obj.c_node.name)
            res.args.append(c.UnaryExpr(op='&', prefix=True, arg=tmp_cid))

        if func_obj.etype_obj is not None:
            # error handling
            err_obj = ctx.create_tmp_var(func_obj.etype_obj, name_hint="err")
            err_obj.c_node.qtype.is_const = True
            err_obj.c_node.value = res
            cfunc.body.append(err_obj.c_node)

            check_error_fobj = ctx.eval_to_fspace(
                xy.Id("to", src=expr.src, coords=expr.coords),
                msg=f"Cannot handle error because there is no 'to' "
                f"function to convert {func_obj.etype_obj.xy_node.name} to bool"
            ).find(
                xy.FuncCall(xy.Id("to"), args=[xy.Id(""), xy.Id("")]),
                ArgList([func_obj.etype_obj, ctx.get_compiled_type(xy.Id("bool"))]),
                ctx
            )
            if check_error_fobj is None:
                raise CompilationError("Cannot find how to check for error", expr)
            check_if = c.If(
                cond=c.FuncCall(
                    name=check_error_fobj.c_name,
                    args=[c.Id(err_obj.c_node.name)]
                )
            )
            if func_obj.etype_obj is ctx.current_fobj.etype_obj:
                check_if.body.append(c.Return(c.Id(err_obj.c_node.name)))
            else:
                cast.includes.append(c.Include("stdlib.h"))
                check_if.body.append(c.FuncCall("abort"))
            cfunc.body.append(check_if)

        else:
            cfunc.body.append(res)

        return FCallObj(
            c_node=tmp_cid,
            xy_node=expr,
            infered_type=func_obj.rtype_obj,
            func_obj=func_obj
        )
    else:
        return FCallObj(
            c_node=res,
            xy_node=expr,
            infered_type=func_obj.rtype_obj,
            func_obj=func_obj
        )

def compile_if(ifexpr, cast, cfunc, ctx):
    c_if = c.If()
    cond_obj = compile_expr(ifexpr.cond, cast, cfunc, ctx)
    # TODO check type is bool
    c_if.cond = cond_obj.c_node
    
    # the first if in an if chain is handled seperately becase it should 
    # provide the return type for the entire chain
    infered_type = None
    c_res = None
    if_exp_obj = None
    if ifexpr.block.is_embedded:
        if_exp_obj = compile_expr(ifexpr.block.body, cast, cfunc, ctx)
        infered_type = if_exp_obj.infered_type
    elif len(ifexpr.block.returns) > 0:
        if len(ifexpr.block.returns) > 1:
            raise CompilationError("Multiple results are NYI", ifexpr)
        infered_type = find_type(ifexpr.block.returns[0].type, ctx)
    else:
        infered_type = ctx.void_obj

    # create tmp var if needed
    if infered_type is not None and infered_type is not ctx.void_obj:
        name_hint = None
        if not ifexpr.block.is_embedded:
            name_hint = ifexpr.block.returns[0].name
        if name_hint is None:
            name_hint = ifexpr.name
            name_hint = ctx.eval_to_id(name_hint) if name_hint is not None else ""
        var_obj = ctx.create_tmp_var(infered_type, name_hint=name_hint)
        cfunc.body.append(var_obj.c_node)
        ctx.ns[name_hint] = var_obj
        c_res = c.Id(var_obj.c_node.name)

    # compile if body
    cfunc.body.append(c_if)
    if if_exp_obj is None:
        compile_body(ifexpr.block.body, cast, c_if, ctx)
    elif infered_type is not ctx.void_obj:
        res_assign = c.Expr(c_res, if_exp_obj.c_node, op='=')
        c_if.body.append(res_assign)
    else:
        c_if.body.append(if_exp_obj.c_node)

    # subsequent ifs
    next_if = ifexpr.else_node
    next_c_if = c_if
    while isinstance(next_if, xy.IfExpr):
        gen_if = c.If()
        gen_if.cond = compile_expr(next_if.cond, cast, cfunc, ctx).c_node
        if not next_if.block.is_embedded:
            compile_body(next_if.block.body, cast, gen_if, ctx)
        elif next_if.block is not None:
            if_exp_obj = compile_expr(next_if.block.body, cast, cfunc, ctx)
            res_assign = c.Expr(c_res, if_exp_obj.c_node, op='=')
            # TODO compare types
            gen_if.body = [res_assign]

        next_c_if.else_body = gen_if
        next_c_if = gen_if
        next_if = next_if.else_node

    # finaly the else if any
    assert isinstance(next_if, xy.Block) or next_if is None
    if next_if is not None and not next_if.is_embedded:
        # normal else
        # XXX fix that
        hack_if = c.If()
        compile_body(next_if.body, cast, hack_if, ctx)
        next_c_if.else_body = hack_if.body
    elif next_if is not None:
        # else is direct result
        else_exp_obj = compile_expr(next_if.body, cast, cfunc, ctx)
        res_assign = c.Expr(c_res, else_exp_obj.c_node, op='=')
        # TODO compare types
        next_c_if.else_body = [res_assign]

    return ExprObj(
        xy_node=ifexpr,
        c_node=c_res,
        infered_type=infered_type
    )

def compile_while(xywhile, cast, cfunc, ctx: CompilerContext):
    cwhile = c.While()

    cond_obj = compile_expr(xywhile.cond, cast, cfunc, ctx)
    cwhile.cond = cond_obj.c_node

    # determine return type if any
    inferred_type = None
    res_c = None
    update_expr_obj = None

    # register loop variables
    for loop_vardecl in xywhile.block.returns:
        if loop_vardecl.name:
            value_obj = compile_expr(loop_vardecl.value, cast, cfunc, ctx) if loop_vardecl.value is not None else None
            type_desc = find_type(loop_vardecl.type, ctx) if loop_vardecl.type is not None else None

            inferred_type = type_desc if type_desc is not None else value_obj.infered_type
            name_hint = loop_vardecl.name
            tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
            ctx.ns[name_hint] = tmp_obj
            if value_obj is not None:
                tmp_obj.c_node.value = value_obj.c_node
            cfunc.body.append(tmp_obj.c_node)
            res_c = c.Id(tmp_obj.c_node.name)

    if xywhile.block.is_embedded:
        update_expr_obj = compile_expr(xywhile.block.body, cast, cwhile, ctx)
        inferred_type = update_expr_obj.infered_type

    # create tmp var if needed
    if inferred_type is not None and inferred_type is not ctx.void_obj and res_c is None:
        name_hint = None
        if isinstance(xywhile.block, xy.Block):
            name_hint = xywhile.block.returns[0].name
        if name_hint is None:
            name_hint = ctx.eval_to_id(xywhile.name)
        tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
        ctx.module_ns[name_hint] = tmp_obj
        cfunc.body.append(tmp_obj.c_node)
        res_c = c.Id(tmp_obj.c_node.name)
    else:
        inferred_type = ctx.void_obj


    # compile body
    if update_expr_obj is None:
        compile_body(xywhile.block.body, cast, cwhile, ctx)
    else:
        cwhile.body.append(update_expr_obj.c_node)

    cfunc.body.append(cwhile)

    return ExprObj(
        xy_node=xywhile,
        c_node=res_c,
        infered_type=inferred_type,
    )

def compile_dowhile(xydowhile, cast, cfunc, ctx):
    cdowhile = c.DoWhile()

    # determine return type if any
    inferred_type = None
    res_c = None
    update_expr_obj = None

    # register loop variables
    for loop_vardecl in xydowhile.block.returns:
        if loop_vardecl.name:
            value_obj = compile_expr(loop_vardecl.value, cast, cfunc, ctx) if loop_vardecl.value is not None else None
            type_desc = find_type(loop_vardecl.type, ctx) if loop_vardecl.type is not None else None

            inferred_type = type_desc if type_desc is not None else value_obj.infered_type
            name_hint = loop_vardecl.name
            tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
            ctx.module_ns[name_hint] = tmp_obj
            if value_obj is not None:
                tmp_obj.c_node.value = value_obj.c_node
            cfunc.body.append(tmp_obj.c_node)
            res_c = c.Id(tmp_obj.c_node.name)

    if xydowhile.block.is_embedded:
        update_expr_obj = compile_expr(xydowhile.block.body, cast, cdowhile, ctx)
        inferred_type = update_expr_obj.infered_type

    # create tmp var if needed
    if inferred_type is not None and inferred_type is not ctx.void_obj and res_c is None:
        name_hint = None
        if isinstance(xydowhile.block, xy.Block):
            name_hint = xydowhile.block.returns[0].name
        if name_hint is None:
            name_hint = ctx.eval_to_id(xydowhile.name)
        tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
        ctx.module_ns[name_hint] = tmp_obj
        cfunc.body.append(tmp_obj.c_node)
        res_c = c.Id(tmp_obj.c_node.name)
    else:
        inferred_type = ctx.void_obj

    # compile cond
    cond_obj = compile_expr(xydowhile.cond, cast, cfunc, ctx)
    cdowhile.cond = cond_obj.c_node

    # finaly compile body
    if update_expr_obj is None:
        compile_body(xydowhile.block.body, cast, cdowhile, ctx)
    else:
        cdowhile.body.append(update_expr_obj.c_node)

    cfunc.body.append(cdowhile)

    return ExprObj(
        xy_node=xydowhile,
        c_node=res_c,
        infered_type=inferred_type,
    )

def compile_for(for_node: xy.ForExpr, cast, cfunc, ctx: CompilerContext):
    cfor = c.For()
    ctx.push_ns()

    for_outer_block = None
    no_for_vars = False
    if len(for_node.over) > 1:
        for_outer_block = c.Block()
        no_for_vars = True

    for iter_node in for_node.over:
        if isinstance(iter_node, xy.BinExpr) and iter_node.op == "in":
            iter_name = ctx.eval_to_id(iter_node.arg1)
            if iter_name == "_":
                iter_name = ctx.create_tmp_var(ctx.void_obj, "iter").c_node.name
            collection_node = iter_node.arg2

            if isinstance(collection_node, xy.SliceExpr):
                # iterating over a slice. Check for built-in case
                start_obj = (
                    compile_expr(collection_node.start, cast, cfunc, ctx)
                    if collection_node.start is not None else None
                )
                end_obj = (
                    compile_expr(collection_node.end, cast, cfunc, ctx)
                    if collection_node.end is not None else None
                )
                step_obj = (
                    compile_expr(collection_node.step, cast, cfunc, ctx)
                    if collection_node.step is not None else None
                )
                is_prim_int = (
                    (start_obj is None or ctx.is_prim_int(start_obj.infered_type)) and
                    (end_obj is None or ctx.is_prim_int(end_obj.infered_type)) and
                    (step_obj is None or ctx.is_prim_int(step_obj.infered_type))
                )

                if is_prim_int:
                    # built-in case of a slice of only ints

                    if start_obj is not None:
                        iter_type = start_obj.infered_type
                    elif end_obj is not None:
                        iter_type = end_obj.infered_type
                    elif step_obj is not None:
                        iter_type = step_obj.infered_type
                    else:
                        iter_type = ctx.uint_obj

                    # compile start
                    start_value = start_obj.c_node if start_obj is not None else iter_type.init_value 
                    iter_var_decl = c.VarDecl(iter_name, c.QualType(iter_type.c_name, is_const=False), value=start_value)
                    ctx.ns[iter_name] = VarObj(xy_node=iter_node, c_node=iter_var_decl, type_desc=iter_type)
                    if no_for_vars:
                        for_outer_block.body.append(iter_var_decl)
                    else:
                        cfor.inits.append(iter_var_decl)

                    # compile condition
                    if end_obj is not None:
                        c_cond = c.Expr(
                            c.Id(iter_var_decl.name),
                            end_obj.c_node,
                            op="<"
                        )
                        if cfor.cond is None:
                            cfor.cond = c_cond
                        else:
                            cfor.cond = c.Expr(cfor.cond, c_cond, op="&&")

                    # compile step
                    if (step_obj is None or
                        (isinstance(step_obj.c_node, c.Const) and
                        step_obj.c_node.value in (1, -1))):
                        op = "++" if step_obj is None or step_obj.c_node.value == 1 else "--"
                        cfor.updates.append(
                            c.UnaryExpr(c.Id(iter_name), op=op, prefix=True)
                        )
                    else:
                        cfor.updates.append(
                            c.Expr(
                                arg1=c.Id(iter_name),
                                arg2=step_obj.c_node,
                                op="+="
                            )
                        )
                else:
                    pass # TODO
            else:
                # not a slice but somesort of collection
                collection_obj = compile_expr(collection_node, cast, cfunc, ctx)
                iter_arg_objs = []
                if is_iter_ctor_call(collection_obj):
                    ictor_obj = collection_obj
                else:
                    collection_obj = move_to_temp(collection_obj, cast, cfunc, ctx)
                    iter_arg_objs = [collection_obj]
                    ictor_obj = find_and_call("iter", ArgList(iter_arg_objs), cast, cfunc, ctx, collection_node)

                # init
                iter_var_decl = ctx.create_tmp_var(ictor_obj.infered_type, "iter")
                iter_var_decl.c_node.value = ictor_obj.c_node
                iter_obj = ExprObj(
                    xy_node=collection_node,
                    c_node=c.Id(iter_var_decl.c_node.name),
                    infered_type=iter_var_decl.type_desc
                )
                ctx.ns[iter_var_decl.c_node.name] = iter_var_decl
                if no_for_vars:
                    for_outer_block.body.append(iter_var_decl.c_node)
                else:
                    cfor.inits.append(iter_var_decl.c_node)

                # compile condition
                valid_obj = find_and_call("valid", ArgList([iter_obj, *iter_arg_objs]), cast, cfunc, ctx, collection_node)
                if cfor.cond is None:
                    cfor.cond = c_cond
                else:
                    cfor.cond = c.Expr(cfor.cond, valid_obj.c_node, op="&&")

                # compile step
                next_obj = find_and_call("next", ArgList([iter_obj, *iter_arg_objs]), cast, cfunc, ctx, collection_node)
                cfor.updates.append(c.Expr(iter_obj.c_node, next_obj.c_node, "="))

                # deref in for body
                deref_obj = find_and_call("deref", ArgList([iter_obj, *iter_arg_objs]), cast, cfunc, ctx, collection_node)

                val_cdecl = c.VarDecl(iter_name, c.QualType(deref_obj.infered_type.c_node.name), value=deref_obj.c_node)
                val_obj = VarObj(collection_node, val_cdecl, deref_obj.infered_type)
                ctx.ns[iter_name] = val_obj
                cfor.body.append(val_cdecl)
        else:
            # Bool expression. Continue if false
            pass # TODO check expression
    if for_outer_block is not None:
        for_outer_block.body.append(cfor)

    inferred_type = ctx.void_obj
    return_objs = []
    for rtn in for_node.block.returns:
        ret_obj = compile_vardecl(rtn, cast, cfunc, ctx)
        return_objs.append(ret_obj)
        cfunc.body.append(ret_obj.c_node)
        inferred_type = ret_obj.type_desc
    assert len(return_objs) <= 1

    if for_node.block.is_embedded:
        update_expr = compile_expr(for_node.block.body, cast, cfor, ctx)
        cfor.body.append(update_expr.c_node)
    else:
        compile_body(for_node.block.body, cast, cfor, ctx)
    ctx.pop_ns()

    if len(return_objs) > 0:
        cfunc.body.append(cfor if for_outer_block is None else for_outer_block)

    if len(return_objs) > 0:
        c_res = c.Id(return_objs[0].c_node.name)
    elif for_outer_block is not None:
        c_res = for_outer_block
    else:
        c_res = cfor

    return ExprObj(
        xy_node=for_node,
        c_node=c_res,
        infered_type=inferred_type,
    )

def is_iter_ctor_call(expr_obj: ExprObj):
    if not isinstance(expr_obj, FCallObj):
        return False
    return "xyIter" in expr_obj.func_obj.tags

def compile_break(xybreak, cast, cfunc, ctx):
    if xybreak.loop_name is not None:
        raise CompilationError("Breaking the outer loop is NYI", xybreak)
    return ExprObj(
        xy_node=xybreak,
        c_node=c.Break(),
        infered_type=ctx.void_obj,
    )

def return_by_param(xy_func):
    return xy_func.etype is not None or len(xy_func.returns) > 1

def compile_return(xyreturn, cast, cfunc, ctx: CompilerContext):
    xy_func = ctx.current_fobj.xy_node
    if not return_by_param(xy_func):
        ret = c.Return()
        if xyreturn.value:
            value_obj = compile_expr(xyreturn.value, cast, cfunc, ctx)
            ret.value = value_obj.c_node
        return ExprObj(
            xy_node=xyreturn,
            c_node=ret,
            infered_type=value_obj.infered_type
        )
    else:
        # return by param(s)
        for iret, ret in enumerate(xy_func.returns):
            value_obj = compile_expr(xyreturn.value, cast, cfunc, ctx)
            param_name = f"__{ret.name}" if ret.name else f"_res{iret}"
            cfunc.body.append(c.Expr(
                arg1=c.UnaryExpr(op="*", arg=c.Id(param_name), prefix=True),
                arg2=value_obj.c_node,
                op="="
            ))
        ret = c.Return()
        if xy_func.etype is not None:
            ret.value = ctx.current_fobj.etype_obj.init_value
        return ExprObj(
            xy_node=xyreturn,
            c_node=ret,
            infered_type=None
        )


def compile_error(xyerror, cast, cfunc, ctx: CompilerContext):
    assert xyerror.value is not None
    value_obj = compile_expr(xyerror.value, cast, cfunc, ctx)

    if ctx.current_fobj.etype_obj is None or \
        ctx.current_fobj.etype_obj is not value_obj.infered_type:
        # error in function not returing an error
        ret = compile_unhandled_error(xyerror, value_obj, cast, cfunc, ctx)
        return ExprObj(
            xy_node=xyerror,
            c_node=ret,
            infered_type=value_obj.infered_type
        )

    # normal error
    ret = c.Return()
    ret.value = value_obj.c_node
    return ExprObj(
        xy_node=xyerror,
        c_node=ret,
        infered_type=value_obj.infered_type
    )

def compile_unhandled_error(xyerror, value_obj, cast, cfunc, ctx):
    if not ctx.stdlib_included:
        cast.includes.append(c.Include("stdlib.h"))
        ctx.stdlib_included = True
    return c.FuncCall("abort")

def get_c_type(type_expr, ctx):
    id_desc = find_type(type_expr, ctx, required=True)
    return id_desc.c_name

def mangle_def(fdef: xy.FuncDef, param_objs: list[VarObj], ctx, expand=False):
    mangled = mangle_name(fdef.name.name, ctx.module_name)
    if expand:
        mangled = [mangled, "__with"]
        for param_obj in param_objs:
            mangled.append("__")
            mangled.append(param_obj.type_desc.xy_node.name)
        mangled = "".join(mangled)
    return mangled

def mangle_field(field: xy.VarDecl):
    # mangle in order to prevent duplication with macros
    return f"m_{field.name}"

def mangle_struct(struct: xy.StructDef, ctx):
    return mangle_name(struct.name, ctx.module_name)

def mangle_define(name: str, module_name: str):
    return mangle_name(name, module_name).upper()

def mangle_name(name: str, module_name: str):
    return module_name.replace(".", "_") + "_" + name


class CompilationError(Exception):
    def __init__(self, msg, node, notes=None):
        self.notes = notes
        loc = node.coords[0]
        loc_len = node.coords[1] - node.coords[0]

        line_num = 1 if loc >= 0 else -1
        line_loc = 0
        for i in range(loc):
            if node.src.code[i] == "\n":
                line_num += 1
                line_loc = i+1

        line_end = len(node.src.code)
        for i in range(line_loc, len(node.src.code)):
            if node.src.code[i] == "\n":
                line_end = i
                break

        cwd = os.getcwd()
        fn = node.src.filename
        if fn.startswith(cwd):
            fn = fn[len(cwd)+1:]
        
        src_line = node.src.code[line_loc:line_end].replace("\t", " ")
        self.error_message = msg
        self.xy_node = node
        self.fmt_msg = f"{fn}:{line_num}:{loc - line_loc + 1}: error: {msg}\n"
        if loc >= 0:
            self.fmt_msg += f"| {src_line}\n"
            self.fmt_msg += "  " + (" " * (loc-line_loc)) + ("^" * loc_len) + "\n"

        if notes is not None and len(notes) > 0:
            self.fmt_msg += "\n".join(n[0] for n in notes)


    def __str__(self):
        return self.fmt_msg


def register_func(fdef, ctx):
    fspace = ctx.ensure_func_space(fdef)
    res = FuncObj(fdef)
    fspace.append(res)
    return res

def find_type(texpr, ctx, required=True):
    if isinstance(texpr, xy.Id) and texpr.name == "struct":
        # Special case for struct
        return TypeObj(builtin=True)
    elif isinstance(texpr, xy.Id) and texpr.name == "?":
        # Special case for ?
        return any_type_obj
    if not isinstance(texpr, xy.ArrayType):
        res = ctx.eval(texpr, msg="Cannot find type")
        return res
    else:
        if len(texpr.dims) == 0:
            raise CompilationError("Arrays must have a length known at compile time", texpr)

        base_type = find_type(texpr.base, ctx)
        dims = []
        for d in texpr.dims:
            dims.append(ct_eval(d, ctx))
        
        return ArrTypeObj(xy_node=texpr, base_type_obj=base_type, dims=dims)

def ct_eval(expr, ctx):
    if isinstance(expr, xy.Const):
        return expr.value
    raise CompilationError("Cannot Compile-Time Evaluate", expr)

def find_func(fcall, ctx):
    fspace = ctx.eval_to_fspace(fcall.name)
    return fspace.find(fcall, ctx)

def compile_binop(binexpr, cast, cfunc, ctx):
    if binexpr.op in {"==", "!=", ">", "<", "<=", ">="} and \
        isinstance(binexpr.arg2, xy.Const) and binexpr.arg2.value == 0:
        arg1_eobj = compile_expr(binexpr.arg1, cast, cfunc, ctx)
        if isinstance(arg1_eobj.c_node, c.Expr) and arg1_eobj.c_node.op == "-":
            c_res = c.Expr(
                arg1=arg1_eobj.c_node.arg1,
                arg2=arg1_eobj.c_node.arg2,
                op=binexpr.op
            )
            return ExprObj(binexpr, c_res, infered_type=ctx.bool_obj)
        else:
            tmp_obj = ctx.create_tmp_var(arg1_eobj.infered_type)
            ctx.ns[tmp_obj.c_node.name] = arg1_eobj
            binexpr = xy.BinExpr(
                arg1=xy.Id(tmp_obj.c_node.name),
                arg2=binexpr.arg2,
                op=binexpr.op
            )

    fcall = rewrite_op(binexpr, ctx)
    return compile_expr(fcall, cast, cfunc, ctx)

def rewrite_op(binexpr, ctx):
    fname = {
        "+": "add",
        "+=": "addEqual",
        "-": "sub",
        "-=": "subEqual",
        "*": "mul",
        "*=": "mulEqual",
        "/": "div",
        "/=": "divEqual",
        "|": "or",
        "|=": "orEqual",
        "&": "and",
        "&=": "andEqual",
    }.get(binexpr.op, None)
    if fname is not None:
        return xy.FuncCall(
            xy.Id(fname, src=binexpr.src, coords=binexpr.coords),
            args=[binexpr.arg1, binexpr.arg2],
            src=binexpr.src, coords=binexpr.coords)
    elif binexpr.op in {"==", "!=", ">", "<", "<=", ">="}:
        cmp_call = xy.FuncCall(
            xy.Id("cmp", src=binexpr.src, coords=binexpr.coords),
            args=[binexpr.arg1, binexpr.arg2],
            src=binexpr.src, coords=binexpr.coords)
        return xy.BinExpr(arg1=cmp_call, arg2=xy.Const(0), op=binexpr.op,
                          src=binexpr.src, coords=binexpr.coords)
    else:
        raise CompilationError(f"Unrecognized operator '{binexpr.op}'", binexpr)

def rewrite_unaryop(expr, ctx):
    if expr.op == "++":
        fname = "inc"
    elif expr.op == "--":
        fname = "dec"
    else:
        raise CompilationError(f"Unrecognized operator '{expr.op}'", expr)
    return xy.FuncCall(
        xy.Id(fname, src=expr.src, coords=expr.coords),
        args=[expr.arg],
        src=expr.src, coords=expr.coords
    )

def rewrite_select(select, ctx):
    fcall = xy.FuncCall(
        xy.Id("select"), args=[select.base, *select.args.args],
        kwargs=select.args.kwargs,
        src=select.src,
        coords=select.coords
    )
    return fcall

def compile_import(imprt, ctx: CompilerContext, ast, cast):
    compiled_tags = ctx.eval_tags(imprt.tags)
    import_obj = None
    if "xyc.lib" in compiled_tags:
        obj = compiled_tags["xyc.lib"]
        # TODO assert obj.xy_node.name.name == "CLib"
        headers = obj.kwargs["headers"]
        for header_obj in headers.elems:
            # TODO what if header_obj is an expression
            if len(header_obj.prefix) > 0:
                raise CompilationError("Only unprefixed strings are recognized", header.xy_node)
            cast.includes.append(c.Include(header_obj.parts[0].value))
        import_obj = ImportObj(name=imprt.lib)
    else:
        assert imprt.in_name is None
        module_header = ctx.builder.import_module(imprt.lib)
        ctx.global_ns.merge(module_header.namespace)
        ctx.str_prefix_reg.update(module_header.str_prefix_reg)
    
    if imprt.in_name:
        # XXX what about multiple in names
        ctx.module_ns[imprt.in_name] = import_obj

def maybe_add_main(ctx, cast):
    if ctx.entrypoint_obj is not None:
        main = c.Func(
            name="main", rtype="int",
            params=[
                c.VarDecl("argc", c.QualType("int",)),
                c.VarDecl("argv", c.QualType("char**"))
            ], body=[
                c.VarDecl("res", c.QualType("int", is_const=True), value=c.FuncCall(ctx.entrypoint_obj.c_name)),
                c.Return(c.Id("res")),
            ]
        )
        cast.funcs.append(main)
