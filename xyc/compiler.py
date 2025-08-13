import itertools
import os
from copy import copy
import xyc.ast as xy
import xyc.cast as c
from dataclasses import dataclass, field, replace

@dataclass
class CompiledObj:
    tags: dict[str, 'CompiledObj'] = field(kw_only=True, default_factory=dict)
    xy_node : any = None
    c_node : any = None

@dataclass
class LazyObj(CompiledObj):
    inferred_type: 'TypeObj' = None
    compiled_obj: CompiledObj | None = None
    ctx: 'CompilerContext' = None

@dataclass
class TypeObj(CompiledObj):
    tag_specs: list['VarObj'] = field(default_factory=list)
    builtin : bool = False
    is_external: bool = False
    fields: dict[str, 'VarObj'] = field(default_factory=dict)
    init_value: any = None
    is_init_value_zeros: bool = True
    needs_dtor: bool = False
    has_explicit_dtor: bool = False
    has_auto_dtor: bool = False
    base_type_obj: 'TypeObj' = None
    fully_compiled: bool = False
    module_header: 'ModuleHeader' = None  # None means current module

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
        if self.builtin and self.xy_node.name == "Ptr" and "to" in self.tags \
            and self.tags["to"] is not calltime_expr_obj:
            to_obj = self.tags["to"]
            return to_obj.c_name + "*"
        if self.c_node is not None:
            return self.c_node.name
        return None

    @property
    def visibility(self):
        if hasattr(self.xy_node, 'visibility'):
            return self.xy_node.visibility
        return xy.PackageVisibility

@dataclass
class TypeExprObj(CompiledObj):
    type_obj: TypeObj = None

    @property
    def c_name(self):
        if self.builtin and self.type_obj.xy_node.name == "Ptr" and "to" in self.tags \
            and self.tags["to"] is not calltime_expr_obj:
            to_obj = self.tags["to"]
            return to_obj.c_name + "*"
        return self.type_obj.c_name

    @property
    def name(self):
        return self.type_obj.name

    @property
    def fields(self):
        return self.type_obj.fields

    @property
    def module_header(self):
        return self.type_obj.module_header

    @property
    def base_type_obj(self):
        return self.type_obj

    @property
    def needs_dtor(self):
        return self.type_obj.needs_dtor

    @needs_dtor.setter
    def needs_dtor(self, needs_dtor):
        self.type_obj.needs_dtor = needs_dtor

    @property
    def has_explicit_dtor(self):
        return self.type_obj.has_explicit_dtor

    @has_explicit_dtor.setter
    def has_explicit_dtor(self, val):
        self.type_obj.has_explicit_dtor = val

    @property
    def has_auto_dtor(self):
        return self.type_obj.has_auto_dtor

    @has_auto_dtor.setter
    def has_auto_dtor(self, val):
        self.type_obj.has_auto_dtor = val

    @property
    def visibility(self):
        return self.type_obj.visibility

    @property
    def init_value(self):
        return self.type_obj.init_value

    @property
    def builtin(self):
        return self.type_obj.builtin

    @property
    def is_init_value_zeros(self):
        return self.type_obj.is_init_value_zeros

    def get_base_type(self):
        return self.type_obj

@dataclass
class ArrTypeObj(TypeObj):
    dims : list = field(default_factory=list)

    @property
    def c_name(self):
        return self.base_type_obj.c_name + "*"

    @property
    def name(self):
        return self.base_type_obj.name + '[' + ']'

@dataclass
class FuncTypeObj(TypeObj):
    func_obj: 'FuncObj' = None
    c_typename: str = ""

    @property
    def c_name(self):
        return self.c_typename

    @property
    def name(self):
        res = "("
        for i, p in enumerate(self.func_obj.param_objs):
            if i > 0:
                res += ", "
            res += p.xy_node.type.name
        res += ")"
        res += "->" + self.func_obj.rtype_obj.name
        return res

@dataclass
class TypeInferenceError:
    msg: str = ""
    needs_dtor: bool = False

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
    def inferred_type(self):
        return self.type_obj

    @property
    def compiled_obj(self):
        return None

@dataclass
class FuncObj(CompiledObj):
    rtype_obj: TypeObj = None
    etype_obj: TypeObj = None
    param_objs: list['VarObj'] = field(default_factory=list)
    builtin: bool = False
    move_args_to_temps: bool = False
    module_header: 'ModuleHeader' = None  # None means current module
    params_compiled: bool = False
    prototype_compiled: bool = False
    has_calltime_tags: bool = False
    decl_visible: bool = False
    is_macro: bool = False

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None

    @property
    def visibility(self):
        if hasattr(self.xy_node, 'visibility'):
            return self.xy_node.visibility
        return xy.PackageVisibility

@dataclass
class VarObj(CompiledObj):
    type_desc: TypeObj | None = None
    passed_by_ref: bool = False # True if the variable is a hidden pointer
    is_pseudo: bool = False
    default_value_obj: CompiledObj = None
    needs_dtor: bool = False
    fieldof_obj: TypeObj | None = None # set to the type this varobj is a field of
    is_stored_global: bool = False

    @property
    def inferred_type(self):
        return self.type_desc

@dataclass
class ImportObj(CompiledObj):
    name: str | None = None
    module_header: 'ModuleHeader' = None
    is_external: bool = False

@dataclass
class ExprObj(CompiledObj):
    inferred_type: CompiledObj | str | None = None
    compiled_obj: CompiledObj | None = None
    first_cnode_idx: int = -1
    num_cnodes: int = -1
    tmp_var_names: set = field(default_factory=set)
    is_iter_ctor: bool = False
    from_lazy_ctx: 'CompilerContext' = None

@dataclass
class ConstObj(ExprObj):
    value: int | float | str | None = None

@dataclass
class IdxObj(ExprObj):
    container: CompiledObj = None
    idx: CompiledObj = None

@dataclass()
class ExtSymbolObj(CompiledObj):
    @property
    def symbol(self):
        return self.c_node.name

    @property
    def c_name(self):
        return self.c_node.name

def ext_symbol_to_type(ext_obj):
    return TypeObj(
        xy_node=ext_obj.xy_node,
        c_node=ext_obj.c_node,
        builtin=False,
        fully_compiled=True,
        init_value=c.InitList([c.Const(0)]),
        is_external=True
    )

@dataclass
class NameAmbiguity:
    modules: list[str] = field(default_factory=list)

any_type_obj = TypeObj(xy_node=xy.Id("Any"), builtin=True, c_node=c.Id("ANY_TYPE_REPORT_IF_YOU_SEE_ME"))
any_struct_type_obj = TypeObj(xy_node=xy.Id("Any"), builtin=True, c_node=c.Id("ANY_TYPE_REPORT_IF_YOU_SEE_ME"))
fieldarray_type_obj = TypeObj(xy_node=xy.Id("FieldArray"), builtin=True, c_node=c.Id("FIELD_TYPE_ARRAY_REPORT_IF_YOU_SEE_ME"))
fselection_type_obj = TypeObj(xy_node=xy.Id("$*"), builtin=True, c_node=c.Id("FUN_SELECTION_REPORT_IF_YOU_SEE_ME"))
macro_type_obj = TypeObj(xy_node=xy.Id("?"), builtin=True, c_node=c.Id("MACRO_TYPE_REPORT_IF_YOU_SEE_ME"))
calltime_expr_obj = TypeObj(builtin=True)
global_memory_type = TypeObj(xy_node=xy.Id("GLOBAL_MEM_REPORT_IF_YOU_SEE_ME"), builtin=True)
global_memory = ExprObj(
    xy_node=xy.Id("GLOBAL_MEM"),
    c_node=c.Id("GLOBAL_MEM"),
    inferred_type=global_memory_type,
)
param_container = VarObj()
recursive_pseudo_field_type_obj = TypeObj(c_node=c.Type("PLACEHOLDER"), xy_node=field)

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

class NamespaceType:
    Loop = 1

@dataclass
class CatchFrame:
    var_name: str
    err_label: str
    inferred_type: TypeExprObj = None
    ref_count: int = 0

@dataclass
class NamespaceData:
    type: NamespaceType = None
    continue_label_name: str = None
    loop_name: str = None
    label_used: bool = False

class IdTable(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = NamespaceData()

    def merge(self, other: 'IdTable', ctx: 'CompilerContext', other_module_name: str):
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
            elif isinstance(current, TypeObj) and not is_obj_visible(current, ctx):
                self[key] = value
            elif isinstance(value, TypeObj) and not is_obj_visible(value, ctx):
                pass
            else:
                self[key] = NameAmbiguity(modules=[ctx.module_name, other_module_name])

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

    def report_multiple_matches(self, candidate_fobjs, node, args_inferred_types, ctx):
        fsig = ctx.eval_to_id(node.name) + "(" + \
            ", ".join(fmt_type(t) for t in args_inferred_types) + \
            ", ".join(f"{pname}: {fmt_type(t)}" for pname, t in args_inferred_types.kwargs.items()) + \
            ")"
        err_msg = f"Multiple function matches for '{fsig}'"
        candidates = "\n    ".join((
            func_sig(f, include_ret=True) for f in candidate_fobjs
        ))
        raise CompilationError(
            err_msg, node,
            notes=[(f"Candidates are:\n    {candidates}", None)]
        )

    def report_no_matches(self, candidate_fobjs, node, args_inferred_types, ctx):
        if hasattr(node.name, 'name'):
            fname = node.name.name
        else:
            fname = node.name.src.code[node.name.coords[0]:node.name.coords[1]]
        fsig = fcall_sig(fname, args_inferred_types, node.inject_args)
        err_msg = f"Cannot find function '{fsig}' in {ctx.module_name}"

        candidates = ''
        prev_module_name = None
        for i, cfobj in enumerate(candidate_fobjs):
            if i > 0:
                candidates += "\n";
            module_name = cfobj.module_header.module_name if cfobj.module_header is not None else ctx.module_name
            if module_name != prev_module_name:
                candidates += f"    in module {module_name}\n"
                prev_module_name = module_name
            candidates += "        " + func_sig(cfobj, include_ret=True)
            if not is_obj_visible(cfobj, ctx):
                candidates += f";; not visible from {ctx.module_name}"

        notes = [(f"Candidates are:\n{candidates}", None)]
        if (fname in {"add", "sub", "div", "mul"} and len(args_inferred_types) == 2 and
            args_inferred_types[0] is not args_inferred_types[1] and
            args_inferred_types[0].builtin and args_inferred_types[0].builtin):
            err_msg += "; Mixed signedness arithmetic is not allowed."
            notes = None

        raise CompilationError(
            err_msg, node,
            notes=notes
        )

    def find(self, node, args_inferred_types, ctx, partial_matches=False, return_no_matches=False):
        candidate_fobjs = self.findAll(node, args_inferred_types, ctx, partial_matches)
        if len(candidate_fobjs) > 1:
            self.report_multiple_matches(candidate_fobjs, node, args_inferred_types, ctx)
        elif len(candidate_fobjs) == 1:
                return candidate_fobjs[0]
        elif not return_no_matches:
            candidate_fobjs = []
            space = self
            while space is not None:
                candidate_fobjs.extend(space._funcs)
                space = space.parent_space
            self.report_no_matches(candidate_fobjs, node, args_inferred_types, ctx)
        else:
            return None

    def findAll(self, node, args_inferred_types, ctx, partial_matches=False):
        space = self
        while space is not None:
            candidate_fobjs = space.find_candidates(node, args_inferred_types, partial_matches, ctx)
            if len(candidate_fobjs) > 0:
                    return candidate_fobjs
            space = space.parent_space
        return []

    def find_candidates(self, node, args_inferred_types, partial_matches, ctx):
        if isinstance(node, (xy.FuncCall, xy.FuncSelect)):
            candidate_fobjs = []
            for desc in self._funcs:
                if cmp_call_def(args_inferred_types, desc, partial_matches, ctx):
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

    def find(self, node, args_inferred_types, ctx, partial_matches=False):
        return FuncObj(c_node=c.Func(name=self.ext_name, rtype=None))

def fmt_type(obj: CompiledObj):
    if isinstance(obj, TypeInferenceError):
        return "???"
    return obj.name

def cmp_call_def(fcall_args_types: ArgList, fobj: FuncObj, partial_matches, ctx):
    if len(fcall_args_types) > len(fobj.param_objs):
        return False
    if fobj.builtin and fobj.xy_node.name.name in {"sizeof", "addrof", "typeEqs"}:
        return fobj

    # check visibility
    if not is_obj_visible(fobj, ctx):
        return False

    satisfied_params = set()
    # go through positional
    for type_obj, param_obj in zip(fcall_args_types.args, fobj.param_objs):
        if not cmp_arg_param_types(type_obj, param_obj.type_desc):
            return False

        if param_obj.xy_node is not None and param_obj.xy_node.name is not None:
            satisfied_params.add(param_obj.xy_node.name)

    # go through named
    pobjs_dict = {pobj.xy_node.name: pobj for pobj in fobj.param_objs if pobj.xy_node is not None and pobj.xy_node.name is not None}
    for pname, type_obj in fcall_args_types.kwargs.items():
        param_obj = pobjs_dict.get(pname, None)
        if param_obj is None:
            return False
        if not cmp_arg_param_types(type_obj, param_obj.type_desc):
            return False

        if pname in satisfied_params:
            return False
        satisfied_params.add(pname)

    if not partial_matches:
        for p_obj in fobj.param_objs[len(fcall_args_types.args):]:
            if p_obj.xy_node.name not in satisfied_params and p_obj.xy_node.value is None:
                return False

    return True

def is_obj_visible(obj, ctx: 'CompilerContext'):
    if obj.visibility in xy.ModuleVisibility:
        if obj.module_header is not None:
            return False
    if obj.visibility == xy.PackageVisibility:
        if obj.module_header is not None:
            if ctx.module_name.split('.')[0] != obj.module_header.module_name.split('.')[0]:
                return False
    return True

def cmp_arg_param_types(arg_type, param_type):
    if param_type is any_type_obj:
        return True

    if isinstance(arg_type, ArrTypeObj):
        if not isinstance(param_type, ArrTypeObj):
            return False
        return True
        if len(arg_type.dims) != len(param_type.dims):
            return False
        for i in range(len(arg_type.dims)):
            if arg_type.dims[i] != param_type.dims[i]:
                return False

    if isinstance(arg_type, FuncTypeObj) and isinstance(param_type, FuncTypeObj):
        return True  # XXX

    arg_type_module = arg_type.module_header.module_name if arg_type.module_header is not None else ""
    param_type_module = param_type.module_header.module_name if param_type.module_header is not None else ""
    if not (arg_type_module == param_type_module and arg_type.get_base_type().xy_node.name == param_type.get_base_type().xy_node.name):
        return False

    return True

def compatible_types(src_type, dst_type):
    # TODO maybe remove cmp_arg_param_types
    if src_type is dst_type:
        return True

    if dst_type is any_type_obj:
        return True

    if isinstance(src_type, ArrTypeObj):
        if not isinstance(dst_type, ArrTypeObj):
            return False
        return True
        if len(arg_type.dims) != len(param_type.dims):
            return False
        for i in range(len(arg_type.dims)):
            if arg_type.dims[i] != param_type.dims[i]:
                return False

    if isinstance(src_type, FuncTypeObj) and isinstance(dst_type, FuncTypeObj):
        return True  # XXX

    if src_type.get_base_type() is not dst_type.get_base_type():
        return False

    return True

def cmp_types_updated(src_type: TypeObj, dst_type: TypeObj, xy_node, fcall_rules=False):
    if src_type is None or dst_type is None:
        return [] ## c types
    # TODO maybe remove cmp_arg_param_types
    if src_type is dst_type:
        return []

    if dst_type is any_type_obj:
        return []

    if isinstance(src_type, ArrTypeObj):
        if not isinstance(dst_type, ArrTypeObj):
            return [("Left side is not an array", dst_type.xy_node)]
        return []
        if len(arg_type.dims) != len(param_type.dims):
            return False
        for i in range(len(arg_type.dims)):
            if arg_type.dims[i] != param_type.dims[i]:
                return False

    if isinstance(src_type, FuncTypeObj) and isinstance(dst_type, FuncTypeObj):
        return []  # XXX

    if isinstance(dst_type, TypeInferenceError) or dst_type is any_type_obj or src_type is any_type_obj:
        return []

    if not (src_type.get_base_type().xy_node.name == dst_type.get_base_type().xy_node.name and src_type.get_base_type().c_name == dst_type.get_base_type().c_name):
        return [(f"Type mismatch in assignment: {fmt_type(src_type.get_base_type())} and {fmt_type(dst_type.get_base_type())}", xy_node)]


    for tag_name, tag in dst_type.tags.items():
        other_tag = src_type.tags.get(tag_name, None)
        if not fcall_rules and other_tag is None:
            return [
                (f"Cannot discard tag '{tag_name}'", xy_node),
                (f"Tag attached here", tag.xy_node),
            ]
        if other_tag is not None and not ct_equals(tag, other_tag):
            return [
                (f"Values for tag '{tag_name}' differ", xy_node),
                (f"Left tag attached here", other_tag.xy_node),
                (f"Right tag attached here", tag.xy_node),
            ]

    return []

def ct_equals(tag, other_tag):
    if isinstance(other_tag, (TypeExprObj, TypeObj)) and isinstance(tag, (TypeExprObj, TypeObj)):
        return tag.c_name == other_tag.c_name
    if not isinstance(tag, type(other_tag)):
        return False
    if tag == other_tag:
        return True
    if isinstance(tag, FuncTypeObj):
        return tag.c_name == other_tag.c_name
    return False

def check_type_compatibility(xy_node, expr1_obj, expr2_obj, ctx, fcall_rules=False):
    errors = cmp_types_updated(expr1_obj.inferred_type, expr2_obj.inferred_type, xy_node, fcall_rules)
    if len(errors) > 0:
        if implicit_zero_conversion(expr2_obj, expr1_obj.inferred_type, ctx):
            return
        raise CompilationError(*errors[0],
            notes=[*errors[1:]]
        )

def fcall_sig(name, args_inferred_types, inject_args=False):
    sig = name + "(" + \
        ", ".join(fmt_type(t) for t in args_inferred_types.args)
    if len(args_inferred_types.kwargs) > 0:
        if len(args_inferred_types.args) > 0:
            sig += ", "
        sig += \
        ", ".join(f"{pname}: {fmt_type(t)}" for pname, t in args_inferred_types.kwargs.items()) + \
        (", ..." if inject_args else "" )
    sig +=  ")"
    return sig

def func_sig(fobj: FuncObj, include_ret=False):
    fdef: xy.FuncDef = fobj.xy_node
    name = fdef.name if isinstance(fdef.name, str) else fdef.name.name
    if fdef.visibility == xy.ModuleVisibility:
        res = '-'
    elif fdef.visibility == xy.PublicVisibility:
        res = '*'
    else:
        res = ''
    res += name + "("
    for i, pobj in enumerate(fobj.param_objs):
        if i > 0:
            res += ", "
        if pobj.xy_node is not None and pobj.xy_node.value is not None:
            res += "["
        if pobj.type_desc == any_type_obj:
            res += "Any"
        else:
            res += pobj.type_desc.name
        if pobj.xy_node is not None and pobj.xy_node.value is not None:
            res += "]"
    if include_ret and not fobj.is_macro:
        res += ") -> "
        if len(fdef.returns) > 1:
            res += "("
        if fobj.rtype_obj is None:
            res += "<ERROR>!"
        else:
            res += fobj.rtype_obj.name
        if len(fdef.returns) > 1:
            res += ")"
    else:
        res += ")"
    return res

@dataclass
class ModuleHeader:
    data_namespace: IdTable
    func_namespace: IdTable
    module_name: str = None
    str_prefix_reg: dict[str, any] = field(default_factory=dict)
    unstr_prefix_reg: dict[str, any] = field(default_factory=dict)
    ctx: 'CompilerContext' = None

@dataclass
class TmpNames:
    tmp_var_i: int = 0

    def gen_tmp_name(self, name_hint="") -> str:
        tmp_name = f"tmp_{self.tmp_var_i}{'_' if name_hint else ''}{name_hint}"
        self.tmp_var_i += 1
        return tmp_name

    def enter_block(self):
        pass

    def enter_func(self):
        self.tmp_var_i = 0

    def exit_block(self):
        pass

@dataclass(repr=False)
class CompilerContext:
    builder: any
    module_name: str  # TODO maybe module_name should be a list of the module names
    module_path: str = ""
    imported_modules: set[str] = field(default_factory=set)

    data_ns: IdTable = field(default_factory=IdTable)
    func_ns: IdTable = field(default_factory=IdTable)
    global_data_ns: IdTable = field(default_factory=IdTable)
    global_func_ns: IdTable = field(default_factory=IdTable)

    str_prefix_reg: dict[str, any] = field(default_factory=dict)
    unstr_prefix_reg: dict[str, any] = field(default_factory=dict)
    added_alignof_macro: bool = False
    defined_c_symbols: set[str] = field(default_factory=set)

    current_fobj: FuncObj | None = None
    tmp_names: TmpNames = field(default_factory=TmpNames)

    global_types: list[TypeObj] = field(default_factory=list)

    catch_frames: list[CatchFrame] = field(default_factory=list)

    entrypoint_obj: any = None
    entrypoint_priority: int = 0
    void_obj: any = None
    bool_obj: any = None
    ptr_obj: any = None
    size_obj: any = None

    stdlib_included = False
    compiling_header = False
    func_compilation_stack : dict = field(default_factory=dict)
    eval_calltime_exprs = True

    next_label_idx = 0

    fsig2obj: dict[str, CompiledObj] = field(default_factory=dict)

    caller_contexts: list['CompilerContext'] = field(default_factory=list)

    ctx_obj_stack: list['CompiledObj'] = field(default_factory=list)

    empty_struct_name: str | None = None

    def __post_init__(self):
        self.data_namespaces = [self.global_data_ns, self.data_ns]
        self.func_namespaces = [self.global_func_ns, self.func_ns]

    def fill_builtin_objs(self, data_ns, func_ns):
        self.void_obj = data_ns["void"]
        self.bool_obj = data_ns["Bool"]
        self.ptr_obj = data_ns["Ptr"]
        self.global_obj = data_ns["Global"]
        self.ptr_to_byte_obj = TypeExprObj(
            self.ptr_obj.xy_node, self.ptr_obj.c_node, self.ptr_obj,
            tags={"to": data_ns["Byte"]},
        )
        self.size_obj = data_ns["Size"]
        self.tagctor_obj = data_ns["TagCtor"]
        self.uint_obj = data_ns["Uint"]
        self.int_obj = data_ns["Int"]
        self.prim_int_objs = (
            data_ns["Byte"],
            data_ns["Ubyte"],
            data_ns["Short"],
            data_ns["Ushort"],
            data_ns["Int"],
            data_ns["Uint"],
            data_ns["Long"],
            data_ns["Ulong"],
            data_ns["Size"],
        )

    def is_prim_int(self, type_obj):
        if isinstance(type_obj,TypeExprObj):
            type_obj = type_obj.base_type_obj
        return type_obj in self.prim_int_objs

    def is_int(self, type_obj):
        if isinstance(type_obj,TypeExprObj):
            type_obj = type_obj.base_type_obj
        return type_obj is self.int_obj

    def push_ns(self, ns_type=None):
        table = IdTable()
        if ns_type is not None:
            table.data.type = ns_type
        self.data_namespaces.append(table)
        return table

    def push_catch_frame(self, cf: CatchFrame):
        self.catch_frames.append(cf)

    def pop_catch_frame(self):
        self.catch_frames.pop()

    def push_ctx_obj(self, new_ctx_obj):
        self.ctx_obj_stack.append(new_ctx_obj)

    def pop_ctx_obj(self):
        self.ctx_obj_stack.pop()

    @property
    def ns(self):
        return self.data_namespaces[-1]

    def pop_ns(self):
        return self.data_namespaces.pop()

    def ensure_func_space(self, name: xy.Id):
        if name.name not in self.func_ns:
            fspace = FuncSpace()
            self.func_ns[name.name] = fspace
            parent_space = self.global_func_ns.get(name.name, None)
            if isinstance(parent_space, FuncSpace):
                fspace.parent_space = parent_space
            return fspace
        candidate = self.func_ns[name.name]
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
        space = self.eval(name, is_func=True, msg=msg)
        if space is None:
            if msg is not None:
                raise CompilationError(msg, name)
            else:
                return None
        if isinstance(space, ExtSymbolObj):
            return ExtSpace(space.symbol)
        if not isinstance(space, FuncSpace):
            # TODO add notes here
            raise CompilationError(f"Not a function.", name)
        return space

    def eval_to_var(self, name: xy.Node):
        var_obj = self.eval(name)
        if var_obj is None:
            var_name = f" '{name.name}'" if isinstance(name, xy.Id) else ""
            raise CompilationError(f"Cannot find variable {var_name}", name)
        if not isinstance(var_obj, VarObj):
            raise CompilationError(f"Not a variable.", name)
        return var_obj

    def eval_to_type(self, name: xy.Node, msg = None):
        obj = self.eval(name, msg=msg)
        if obj is None:
            raise CompilationError(f"Cannot find type '{self.eval_to_id(name)}'", name)
        if isinstance(obj, ExtSymbolObj):
            return ext_symbol_to_type(obj)
        if not isinstance(obj, (TypeObj, TypeExprObj)):
            raise CompilationError("Not a type", name)
        if not is_obj_visible(obj, self):
            raise CompilationError(f"Struct '{obj.name}' is not visible", name)
        return obj

    def eval_to_id(self, name: xy.Node):
        if isinstance(name, xy.CallerContextExpr):
            name = name.arg
        if isinstance(name, xy.Id):
            return name.name
        if isinstance(name, xy.BinExpr):
            return self.eval_to_id(name.arg1) + name.op + self.eval_to_id(name.arg2)
        raise CompilationError("Cannot determine identifier", name)

    def get_compiled_type(self, name: xy.Id | str):
        res = self.eval_to_type(name if not isinstance(name, str) else xy.Id(name))
        return res

    def split_and_eval_tags(self, tags: xy.TagList, cast, ast):
        kw_tags = copy(tags.kwargs)
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
                if xy_tag.value is not None:
                    kw_tags[xy_tag.name] = xy_tag.value
        tag_specs = [
            VarObj(xy_node=xy_tag, type_desc=find_type(xy_tag.type, cast, self))
            for xy_tag in open_tags
        ]
        remaining_args = tags.args[after_open:]
        return tag_specs, self.eval_tags(xy.TagList(remaining_args, kw_tags), cast=cast, ast=ast)


    def eval_tags(self, tags: xy.TagList, tag_specs: list[VarObj] = [], cast=None, ast=None):
        res = {}
        no_label_msg = "Please associate default label by adding the TagCtor tag" \
        ": ~[TagCtor{label=\"default-label\"}] " \
        "or add a positional tag to the struct"
        for i, xy_tag in enumerate(tags.args):
            try:
                tag_obj = self.eval(xy_tag, msg="Cannot find symbol")
            except NoCallerContextError:
                tag_obj = calltime_expr_obj
            if i < len(tag_specs):
                spec = tag_specs[i]
                label = spec.xy_node.name
            elif isinstance(tag_obj, TypeObj):
                fully_compile_type(tag_obj, cast, ast, self)
                if "xyTag" not in tag_obj.tags:
                    raise CompilationError(
                        f"Missing default label for type '{tag_obj.xy_node.name}'",
                        xy_tag, notes=[(no_label_msg, None)])
                label = tag_obj.tags["xyTag"].kwargs["label"].as_str()
                tag_obj = TypeExprObj(
                    xy_node=xy_tag, c_node=tag_obj.c_node,
                    type_obj=tag_obj, tags=copy(tag_obj.tags)
                )
            elif isinstance(tag_obj, InstanceObj):
                assert tag_obj.type_obj is not None
                if "xyTag" not in tag_obj.type_obj.tags:
                    raise CompilationError(
                        f"Missing default label for type '{tag_obj.type_obj.xy_node.name}'",
                        xy_tag, notes=[(no_label_msg, None)])
                label = tag_obj.type_obj.tags["xyTag"].kwargs["label"].as_str()
            elif isinstance(tag_obj, ExtSymbolObj):
                raise CompilationError("C Symbols must be attached using an explicit label", xy_tag)
            elif tag_obj.primitive:
                raise CompilationError("Primitive types have to have an explicit label", xy_tag)
            else:
                raise CompilationError("Cannot determine label for tag", xy_tag)

            if label in res:
                raise CompilationError(f"Label '{label}' already filled by tag", res[label].xy_node)
            res[label] = tag_obj
        for label, xy_tag in tags.kwargs.items():
            try:
                tag_obj = self.eval(xy_tag)
            except NoCallerContextError:
                tag_obj = calltime_expr_obj
            if label in res:
                raise CompilationError(f"Label '{label}' already filled by tag", res[label].xy_node)
            if isinstance(tag_obj, TypeObj):
                fully_compile_type(tag_obj, cast, ast, self)
                tag_obj = TypeExprObj(
                    xy_node=xy_tag, c_node=tag_obj.c_node,
                    type_obj=tag_obj, tags=copy(tag_obj.tags)
                )
            res[label] = tag_obj
        return res

    def lookup(self, name: str, is_func: bool):
        namespaces = self.data_namespaces if not is_func else self.func_namespaces
        for ns in reversed(namespaces):
            if name in ns:
                return ns[name]
        return None

    def eval(self, node, msg=None, is_func=False):
        res = self.do_eval(node, msg=msg, is_func=is_func)
        if isinstance(res, NameAmbiguity):
            modules_str = '\n    '.join(res.modules)
            raise CompilationError(
                "Symbol is defined in multiple modules. Pelase be explicit and specify the module. See TBD for more info",
                node, notes=(
                    (f"Symbol is defined in the following modules\n    {modules_str}", None),
                )
            )
        return res

    def register_global_type(self, type_obj):
        self.global_types.append(type_obj)

    def print_data_namespaces(self):
        self.print_namespaces(self.data_namespaces)

    def print_namespaces(ctx, namespaces):
        print(f"module: {ctx.module_name}")
        for ns in namespaces:
            print(ns.keys())

    def do_eval(self, node, msg=None, is_func=False):
        if isinstance(node, xy.Id):
            res = self.lookup(node.name, is_func=is_func)
            if res is None and msg is not None:
                raise CompilationError(msg, node)
            return res
        elif isinstance(node, xy.CallerContextExpr):
            if not self.eval_calltime_exprs:
                raise NoCallerContextError
            if not self.has_caller_context():
                raise CompilationError("No caller context", node)
            return self.get_caller_context().eval(node.arg, msg=msg, is_func=is_func)
        elif isinstance(node, xy.Const):
            const_type_obj = None
            if node.type is not None:
                const_type_obj = self.get_compiled_type(node.type)
            return ConstObj(value=node.value, xy_node=node,
                            c_node=c.Const(node.value_str),
                            inferred_type=const_type_obj)
        elif isinstance(node, xy.StrLiteral):
            if node.prefix != "inlinec":
                return StrObj(
                    prefix=node.prefix,
                    parts=[self.eval(p) for p in node.parts],
                    xy_node=node
                )
            else:
                if len(node.parts) > 1:
                    raise CompilationError("Cannot evaluate expression at compile time", node.parts[1])
                return ExtSymbolObj(
                    c_node=c.Id(node.full_str),
                    xy_node=node,
                )
        elif isinstance(node, xy.StructLiteral):
            instance_type = self.eval(node.name)
            if instance_type is None:
                raise CompilationError(f"Cannot find name '{self.eval_to_id(node.name)}'", node.name)
            obj = InstanceObj(type_obj=instance_type, xy_node=node)
            pos_to_name = list(instance_type.fields.keys())
            for i, arg in enumerate(node.args):
                if isinstance(arg, xy.BinExpr) and arg.op=="=":
                    # named field
                    fname = arg.arg1.name
                    obj.kwargs[fname] = self.eval(arg.arg2)
                else:
                    # positional field
                    fname = pos_to_name[i]
                    obj.kwargs[fname] = self.eval(arg)
                if obj.kwargs[fname] is None:
                    raise CompilationError("Cannot eval at compile-time", arg)
            return obj
        elif isinstance(node, xy.ArrayLit):
            return ArrayObj(
                # TODO inferred_type=
                elems=[self.eval(elem) for elem in node.elems],
                xy_node=node
            )
        elif isinstance(node, xy.BinExpr):
            if node.op == ".":
                base = self.eval(node.arg1, msg="Cannot find symbol")
                if isinstance(base, ImportObj):
                    if base.is_external:
                        assert isinstance(node.arg2, xy.Id)
                        return ExtSymbolObj(
                            c_node=c.Id(node.arg2.name),
                            xy_node=node.arg2,
                        )
                    else:
                        assert isinstance(node.arg2, xy.Id)
                        return base.module_header.ctx.eval(node.arg2, msg, is_func=is_func)
                elif isinstance(base, (TypeObj, TypeExprObj)):
                    return base.fields[node.arg2.name]
                elif isinstance(base, VarObj):
                    if node.arg2.name not in base.type_desc.fields:
                        raise CompilationError(f"No field {node.arg2.name}", node.arg2)
                    return base.type_desc.fields[node.arg2.name]
                else:
                    raise CompilationError("Cannot evaluate", node)
            elif node.op == "..":
                base = self.eval(node.arg1, is_func=is_func)
                return tag_get(node, base, node.arg2.name, self)
            assert False
        elif isinstance(node, xy.AttachTags):
            obj = self.eval(node.arg)
            if isinstance(obj, ConstObj):
                obj.tags = self.eval_tags(node.tags)
            elif isinstance(obj, TypeObj):
                base_type = obj
                obj = TypeExprObj(
                    xy_node=node, c_node=base_type.c_node, type_obj=base_type,
                    tags=copy(obj.tags)
                )
                obj.tags.update(self.eval_tags(node.tags, base_type.tag_specs))
            else:
                raise CompilationError(f"Cannot assign tags to obj of type {obj.__class__.__name__}", node)
            return obj
        else:
            try:
                obj = compile_expr(node, None, None, self, deref=False)
            except NoCallerContextError:
                return calltime_expr_obj
            if isinstance(obj, TypeObj):
                return obj
            elif obj.compiled_obj is not None:
                return obj.compiled_obj
            elif isinstance(obj, IdxObj) and obj.container is global_memory and isinstance(obj.idx.inferred_type, FuncTypeObj):
                # calling a callback
                return obj.idx
            raise CompilationError(
                "Cannot evaluate at compile time.",
                node)

    def create_tmp_var(self, type_obj, name_hint="", xy_node=None) -> VarObj:
        tmp_var_name = self.gen_tmp_name(name_hint)

        # TODO rewrite expression and call other func
        c_tmp = c.VarDecl(name=tmp_var_name, qtype=c.QualType(is_const=False))
        if isinstance(type_obj, ArrTypeObj):
            c_tmp.qtype.type.name = type_obj.base_type_obj.c_name
            c_tmp.qtype.type.dims = type_obj.dims
        else:
            c_tmp.qtype.type.name = type_obj.c_name

        if type_obj.init_value is not None:
            c_tmp.value = type_obj.init_value

        dummy_xy_node = xy.VarDecl(
            name="dummy_xy_node",
            src=xy_node.src if xy_node is not None else None,
            coords=xy_node.coords if xy_node is not None else (-1, -1),
        )
        res = VarObj(dummy_xy_node, c_tmp, type_obj, needs_dtor=type_needs_dtor(type_obj))
        self.ns[tmp_var_name] = res
        return res

    def compile_tmp_var(self, value_expr, cast, cfunc, name_hint="") -> VarObj:
        tmp_var_name = self.gen_tmp_name(name_hint)
        tmp = xy.VarDecl(
            tmp_var_name, value=value_expr,
            src=value_expr.src, coords=value_expr.coords
        )
        obj = compile_vardecl(tmp, cast, cfunc, self)
        cfunc.body.append(obj.c_node)
        return obj

    def gen_tmp_name(self, name_hint="") -> str:
        return self.tmp_names.gen_tmp_name(name_hint=name_hint)

    def gen_tmp_label_name(self, name_hint="") -> str:
        res = f"L_{self.next_label_idx}_CONTINUE_{name_hint}"
        self.next_label_idx += 1
        return res

    def enter_block(self):
        self.tmp_names.enter_block()

    def enter_func(self):
        self.next_label_idx = 0
        self.tmp_names.enter_func()

    def exit_block(self):
        self.tmp_names.exit_block()

    def trueObj(self, xy_node):
        return ConstObj(
            xy_node=xy_node,
            c_node=c.Const("true"),
            inferred_type=self.bool_obj
        )

    def falseObj(self, xy_node):
        return ConstObj(
            xy_node=xy_node,
            c_node=c.Const("false"),
            inferred_type=self.bool_obj
        )

    def has_caller_context(self):
        return len(self.caller_contexts) > 0

    def get_caller_context(self):
        return self.caller_contexts[-1]

    def push_caller_context(self, caller_ctx):
        self.caller_contexts.append(caller_ctx)

    def pop_caller_context(self):
        return self.caller_contexts.pop()

def compile_module(builder, module_name, asts, module_path):
    ctx = CompilerContext(builder, module_name)
    ctx.module_path = module_path
    res = c.Ast()

    if module_name == "xy.builtins":
        ctx.global_data_ns["c"] = ImportObj(is_external=True)
    else:
        compile_import(xy.Import(lib="xy.builtins"), ctx, asts, res)
        ctx.fill_builtin_objs(ctx.global_data_ns, ctx.global_func_ns)

    ctx.compiling_header = True
    fobjs = compile_header(ctx, asts, res)
    ctx.compiling_header = False

    for fobj in fobjs:
        compile_func(fobj, res, ctx)

    # maybe_add_main(ctx, res)

    mh = ModuleHeader(
        module_name=module_name,
        data_namespace=ctx.data_ns, func_namespace=ctx.func_ns,
        str_prefix_reg=ctx.str_prefix_reg, unstr_prefix_reg=ctx.unstr_prefix_reg,
        ctx=ctx
    )

    for obj in itertools.chain(ctx.data_ns.values(), ctx.func_ns.values()):
        if isinstance(obj, FuncSpace):
            for func_obj in obj._funcs:
                func_obj.module_header = mh
        elif isinstance(obj, TypeObj):
            obj.module_header = mh

    # TODO should that really be here
    if module_name.startswith("xy."):
        for obj in itertools.chain(ctx.data_ns.values(), ctx.func_ns.values()):
            obj.builtin = True

            if isinstance(obj, FuncSpace):
                for func_obj in obj._funcs:
                    func_obj.builtin = True

    if module_name == "xy.builtins":
        ctx.fill_builtin_objs(ctx.data_ns, ctx.func_ns)

    return mh, res

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
                validate_name(node, ctx)
                cdef = c.Define(
                    name=mangle_define(node.name, ctx.module_name),
                )
                ctx.data_ns[node.name] = VarObj(
                    xy_node=node,
                    c_node=cdef,
                )
                try_compile_const_value(ctx.data_ns[node.name], node.value, cast, ctx)
                cast.consts.append(cdef)


    compile_structs(ctx, asts, cast)

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.VarDecl) and ctx.data_ns[node.name].c_node.value is None:
                do_compile_const_value(ctx.data_ns[node.name], node.value, cast, ctx)

    fobjs = []
    for ast in asts:
        for node in ast:
            if isinstance(node, xy.FuncDef):
                create_fobj(node, fobjs, ctx)

    for fobj in fobjs:
        compile_func_prototype(fobj, cast, ctx)

    for fobj in fobjs:
        fill_param_default_values(fobj, cast, ctx)
        fsig = func_sig(fobj)
        if (other := ctx.fsig2obj.get(fsig, None)) is not None:
            raise CompilationError(
                f"Function with the same signature already exists: {fsig}", fobj.xy_node,
                notes=[
                    ("Previous definition is here", other.xy_node)
                ]
            )
        ctx.fsig2obj[fsig] = fobj

    # finally check if we need to auto generate any dtors
    for ast in asts:
        for node in ast:
            if isinstance(node, xy.StructDef):
                type_obj: TypeObj = ctx.data_ns[node.name]
                fill_missing_dtors(type_obj, fobjs, asts, cast, ctx)

    return fobjs

def try_compile_const_value(obj, node, cast, ctx):
    can_compile_now = False
    try:
        do_compile_const_value(obj, node, cast, ctx)
        ctx.eval(node)
        can_compile_now = True
    except:
        pass

    if can_compile_now:
        value_obj = compile_expr(node, cast, None, ctx)
        obj.c_node.value = value_obj.c_node
        obj.type_desc = value_obj.inferred_type

    return can_compile_now

def do_compile_const_value(obj, node, cast, ctx):
    ctx.eval(node)
    value_obj = compile_expr(node, cast, None, ctx)
    obj.c_node.value = value_obj.c_node
    obj.type_desc = value_obj.inferred_type

def create_fobj(node: xy.FuncDef, fobjs, ctx):
    for i, param in enumerate(node.params):
        if isinstance(param.type, xy.Enumeration):
            for item in param.type.items:
                gen_fn = copy(node)
                gen_fn.params = copy(node.params)
                gen_param = copy(param)
                gen_param.type = item
                gen_fn.params[i] = gen_param
                create_fobj(gen_fn, fobjs, ctx)
            return
    # No param type enumeration
    fobj = FuncObj(
        xy_node=node,
    )
    validate_name(node, ctx)
    func_space = ctx.ensure_func_space(node.name)
    func_space.append(fobj)
    fobjs.append(fobj)

def fill_missing_dtors(type_obj: TypeObj, all_fobjs, asts, cast, ctx):
    if type_obj.module_header is not None:
        return type_obj.needs_dtor
    if type_obj.has_explicit_dtor or type_obj.has_auto_dtor:
        return True
    if not type_obj.needs_dtor:
        # maybe it doesn't need a dtor or maybe we don't realize it yet
        for f in type_obj.fields.values():
            if not f.is_pseudo:
                f.needs_dtor = fill_missing_dtors(f.type_desc, all_fobjs, asts, cast, ctx)
                type_obj.needs_dtor = type_obj.needs_dtor or f.needs_dtor
    if type_obj.needs_dtor:
        type_obj.has_auto_dtor = True
        dtor_node = xy.FuncDef(
            xy.Id("dtor"), xy.PublicVisibility,
            params=[xy.VarDecl("obj", xy.Id(type_obj.xy_node.name))],
            body=[],
        )
        fobj = FuncObj(
            xy_node=dtor_node,
        )
        func_space = ctx.ensure_func_space(dtor_node.name)
        func_space.append(fobj)
        compile_func_prototype(fobj, cast, ctx)
        asts[0].append(dtor_node)
        all_fobjs.append(fobj)
        return True
    return False

keywords = {
    "if", "ef", "else", "for", "while", "Any", "def", "struct", "in", "inout",
    "outin", "out", "ref", "macro", "yield", "do", "switch", "continue",
    "break", "goto",
}

def validate_name(node: xy.Node, ctx: CompilerContext):
    name = node.name
    if isinstance(name, xy.Id):
        name = name.name
    if not isinstance(name, str):
        raise CompilationError("Invalid identifier", node)
    if '_' in name:
        raise CompilationError("Underscores are not allowed in names. For more info go to TBD", node)
    if not name[0].isalpha():
        raise CompilationError("Names should start with a letter", node)
    for i in range(1, len(name)):
        if not name[i].isalnum():
            raise CompilationError("Names should be alphanumeric", node)
    if name in keywords:
        raise CompilationError(f"'{name}' is a keyword", node)

def compile_structs(ctx: CompilerContext, asts, cast: c.Ast):
    # 1st pass - compile just the names
    for ast in asts:
        for node in ast:
            if isinstance(node, xy.StructDef):
                validate_name(node, ctx)
                type_obj = TypeObj(
                    xy_node = node,
                )
                if node.name in ctx.data_ns:
                    raise CompilationError(
                        "Struct with same name already defined in module", node,
                        notes=[("Previous definition", ctx.data_ns[node.name].xy_node)]
                    )
                ctx.data_ns[node.name] = type_obj

    # 2nd pass - compile fields
    for ast in asts:
        for node in ast:
            if isinstance(node, xy.StructDef):
                type_obj = ctx.data_ns[node.name]
                fully_compile_type(type_obj, cast, ast, ctx)

def fully_compile_type(type_obj: TypeObj, cast, ast, ctx):
    if isinstance(type_obj, TypeExprObj):
        type_obj = type_obj.type_obj
    if type_obj.fully_compiled:
        return
    type_obj.fully_compiled = True

    tag_specs, tag_objs = ctx.split_and_eval_tags(type_obj.xy_node.tags, cast, ast)
    type_obj.tags.update(tag_objs)
    type_obj.tag_specs = tag_specs

    target_cast = None
    compile_pseudo = False
    if isinstance(type_obj, ArrTypeObj):
        fully_compile_type(type_obj.base_type_obj, cast, ast, ctx)
        type_obj.c_node = c.Type(
            name=type_obj.base_type_obj.c_node.name,
            dims=type_obj.dims,
        )
    elif isinstance(type_obj, FuncTypeObj):
        pass
        # assert type_obj.c_node is not None
    else:
        cstruct = c.Struct(name=mangle_struct(type_obj.xy_node, ctx))
        type_obj.c_node = cstruct
        c_typedef = c.Typedef("struct " + cstruct.name, cstruct.name)
        cast.type_decls.append(c_typedef)
        target_cast = cast.structs

    # finaly compile fields
    if isinstance(type_obj, ArrTypeObj):
        assert len(type_obj.dims) == 1 # TODO implmenent multi dim
        for i in range(type_obj.dims[0]):
            type_obj.fields[i] = VarObj(
                xy_node=type_obj.xy_node, c_node=None,
                type_desc=type_obj.base_type_obj,
            )
        type_obj.init_value = c.CompoundLiteral(
            name=None,
            args=[c.Const(0)]
        )
    elif isinstance(type_obj, FuncTypeObj):
        type_obj.init_value = c.Const(0)
    else:
        compile_pseudo = True
        compile_struct_fields(type_obj, ast, cast, ctx)
        num_non_pseudo_fields = sum(int(not f.is_pseudo) for f in type_obj.fields.values())
        if num_non_pseudo_fields == 0:
            empty_name = ensure_empty_struct(cast, ast, ctx)
            c_typedef.typename = "struct " + empty_name
            target_cast = None

    if target_cast is not None:
        target_cast.append(type_obj.c_node)

    if compile_pseudo:
        compile_pseudo_fields(type_obj, ast, cast, ctx)

def ensure_empty_struct(cast, ast, ctx):
    if ctx.empty_struct_name:
        return ctx.empty_struct_name
    ctx.empty_struct_name = mangle_name("_EMPTY_STRUCT_", ctx.module_name)
    cast.structs.append(c.Struct(ctx.empty_struct_name, fields=[
        c.VarDecl(
            name="__empty_structs_are_not_allowed_in_c__",
            qtype=c.QualType("char")
        )
    ]))
    return ctx.empty_struct_name

def compile_struct_fields(type_obj, ast, cast, ctx):
    node = type_obj.xy_node
    cstruct = type_obj.c_node
    fields = {}
    default_values = []
    default_values_zeros = []
    for field in node.fields:
        field_type_obj = None
        if field.type is not None:
            field_type_obj = find_type(field.type, cast, ctx)
            if field_type_obj is type_obj:
                raise CompilationError("Recursive structs are not possible", field)
            fully_compile_type(field_type_obj, cast, ast, ctx)

        if field.is_pseudo:
            if field.value is None:
                raise CompilationError("All pseudo fields must have an explicit value")
            default_value_obj = None
            field_type_obj = recursive_pseudo_field_type_obj
        elif field.value is not None:
            default_value_obj = ctx.eval(field.value)
            if default_value_obj.inferred_type is type_obj:
                raise CompilationError("Recursive structs are not possible", field)
            if isinstance(default_value_obj, InstanceObj):
                # I don't like that. Why not just call compile_expr
                default_value_obj.c_node = compile_expr(field.value, cast, None, ctx).c_node
            elif isinstance(default_value_obj, VarObj):
                default_value_obj = copy(default_value_obj)  # Don't overwrite var obj
                default_value_obj.c_node = c.Id(default_value_obj.c_node.name)
            if field_type_obj is None:
                field_type_obj = default_value_obj.inferred_type
            elif field_type_obj is not default_value_obj.inferred_type:
                raise CompilationError("Explicit and inferred types differ", field)
            dv_cnode = default_value_obj.c_node
            default_values.append(dv_cnode)
            default_values_zeros.append(isinstance(dv_cnode, c.Const) and dv_cnode.value == 0)
        else:
            fully_compile_type(field_type_obj, cast, ast, ctx)
            if field_type_obj.init_value is None:
                if field_type_obj.is_external:
                    raise CompilationError("Fields with external types must have an explicit default value", field)
                else:
                    raise CompilationError("COMPILER BUG! Missing init value for type", field)
            default_value_obj = InstanceObj(type_obj=field_type_obj, xy_node=field)
            default_values.append(field_type_obj.init_value)
            default_values_zeros.append(field_type_obj.is_init_value_zeros)

        field_ctype = field_type_obj.c_node if isinstance(field_type_obj.c_node, c.Type) else field_type_obj.c_name
        cfield = c.VarDecl(
            name=mangle_field(field),
            qtype=c.QualType(field_ctype)
        )
        if field.name in fields:
            raise CompilationError("Field already defined", field)
        fields[field.name] = VarObj(
            xy_node=field,
            c_node=cfield,
            type_desc=field_type_obj,
            is_pseudo=field.is_pseudo,
            default_value_obj=default_value_obj,
            fieldof_obj=type_obj,
            needs_dtor=field_type_obj.needs_dtor,
        )

        if not field.is_pseudo:
            type_obj.needs_dtor = type_obj.needs_dtor or field_type_obj.needs_dtor
            cstruct.fields.append(cfield)
    type_obj.fields = fields

    all_zeros = all(default_values_zeros)
    c_init_args = [c.Const(0)] if all_zeros else default_values
    type_obj.init_value = c.CompoundLiteral(
        name=cstruct.name,
        args=c_init_args
    )
    type_obj.is_init_value_zeros = all_zeros

def compile_pseudo_fields(type_obj, ast, cast, ctx):
    fields = type_obj.fields
    for field in type_obj.xy_node.fields:
        if not field.is_pseudo:
            continue
        field_type_obj = None
        if field.type is not None:
            field_type_obj = find_type(field.type, cast, ctx)

        if field.value is None:
            raise CompilationError("All pseudo fields must have an explicit value")
        dvo_c_node = compile_expr(field.value, cast, None, ctx).c_node
        default_value_obj = ctx.eval(field.value)
        default_value_obj.c_node = dvo_c_node
        if field_type_obj is None:
            field_type_obj = default_value_obj.inferred_type
        elif field_type_obj is not default_value_obj.inferred_type:
            raise CompilationError("Explicit and inferred types differ", field)

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
            default_value_obj=default_value_obj,
            fieldof_obj=type_obj,
        )

def compile_func_prototype(fobj: FuncObj, cast, ctx):
    if fobj.params_compiled or fobj.prototype_compiled:
        return fobj
    if id(fobj) in ctx.func_compilation_stack:
        notes = [
            ("Depends on", prev_fobj.xy_node)
            for prev_fobj in ctx.func_compilation_stack.values()
        ]
        raise CompilationError("Recursive dependancy", fobj.xy_node, notes=notes)
    ctx.func_compilation_stack[id(fobj)] = fobj

    if not isinstance(fobj.xy_node.body, list):
        fobj.is_macro = True

    node: xy.FuncDef = fobj.xy_node

    cfunc = c.Func(None)
    ctx.push_ns()

    move_args_to_temps = len(node.in_guards) > 0 or len(node.out_guards) > 0
    param_objs, any_default_values = compile_params(node.params, cast, cfunc, ctx)
    move_args_to_temps = move_args_to_temps or any_default_values
    move_args_to_temps = move_args_to_temps or any(p.is_pseudo for p in node.params)

    func_space = ctx.ensure_func_space(node.name)
    expand_name = len(func_space) > 1
    cfunc.name = mangle_def(node, param_objs, ctx, expand=expand_name)

    fobj.params_compiled = True
    fobj.param_objs = param_objs

    # check if dtor
    if fobj.xy_node.name.name == "dtor" and len(param_objs) > 0:
        param_objs[0].inferred_type.needs_dtor = True
        param_objs[0].inferred_type.has_explicit_dtor = True

    rtype_compiled, etype_compiled, any_refs, has_calltime_tags = compile_ret_err_types(node, cast, cfunc, ctx)
    move_args_to_temps = move_args_to_temps or any_refs
    fobj.has_calltime_tags = has_calltime_tags

    if fobj.is_macro:
        # Macros have boundary expressions as body so the type may very depending on the
        # arguments.
        rtype_compiled = macro_type_obj

        # Let's do an early check about returning a type
        if isinstance(fobj.xy_node.body, xy.UnaryExpr) and fobj.xy_node.body.op == "%":
            raise CompilationError("Functions cannot return a type", fobj.xy_node.body)

    ctx.pop_ns()

    if isinstance(rtype_compiled, TypeInferenceError):
        raise CompilationError(
            rtype_compiled.msg,
            node.returns[0] if len(node.returns) > 0 else node.body
        )
    cfunc.rtype = (etype_compiled.c_name
                    if etype_compiled is not None
                    else rtype_compiled.c_name)

    fobj.c_node = cfunc
    fobj.rtype_obj = rtype_compiled
    fobj.etype_obj = etype_compiled
    fobj.move_args_to_temps = move_args_to_temps

    if node.etype is not None:
        fobj.etype_obj = ctx.get_compiled_type(node.etype)

    # compile tags
    fobj.tags = ctx.eval_tags(node.tags)
    if "xyStr" in fobj.tags:
        # TODO assert it is a StrCtor indeed
        str_lit = fobj.tags["xyStr"].kwargs.get("prefix", xy.StrLiteral())
        prefix = str_lit.parts[0].value if len(str_lit.parts) else ""
        ctx.str_prefix_reg[prefix] = fobj
    if "xy.unstr" in fobj.tags:
        # TODO assert it is a StrCtor indeed
        str_lit = fobj.tags["xy.unstr"].kwargs.get("prefix", xy.StrLiteral())
        prefix = str_lit.parts[0].value if len(str_lit.parts) else ""
        ctx.unstr_prefix_reg[prefix] = fobj
    if "xy.entrypoint" in fobj.tags:
        # TODO assert it is the correct type
        tag_obj = fobj.tags["xy.entrypoint"]
        priority = 0
        if isinstance(tag_obj, InstanceObj):
            priority = tag_obj.kwargs["priority"].value

        if ctx.entrypoint_obj is not None and priority == ctx.entrypoint_priority:
            raise CompilationError("Multiple entry points found.", fobj.xy_node, notes=[
                ("Previous entrypoint", ctx.entrypoint_obj.xy_node),
            ])
        ctx.entrypoint_obj = fobj
        ctx.entrypoint_priority = priority

    del ctx.func_compilation_stack[id(fobj)]
    fobj.prototype_compiled = True
    return fobj

def compile_params(params, cast, cfunc, ctx):
    param_objs = []
    any_default_value_params = False
    for param in params:
        if param.name is not None:
            validate_name(param, ctx)
        param_obj = VarObj(xy_node=param)

        if param.value is not None:
            any_default_value_params = True

        if param.type is not None:
            ptype_obj = find_type(param.type, cast, ctx)
            if isinstance(param.type, xy.Id) and len(ptype_obj.tags):
                ptype_obj = TypeExprObj(
                    xy_node=ptype_obj.xy_node,
                    c_node=ptype_obj.c_node,
                    type_obj=ptype_obj
                )
            param_obj.type_desc = ptype_obj
        else:
            param_obj.type_desc = do_infer_type(param.value, cast, ctx)

        param_obj.passed_by_ref=should_pass_by_ref(param, param_obj.type_desc)

        if param_obj.type_desc:
            c_type = param_obj.type_desc.c_name
            if param_obj.passed_by_ref:
                c_type = c_type + "*"
        else:
            raise CompilationError("Compiler Error: Cannot infer type of param", param)

        if param_obj.type_desc is any_struct_type_obj:
            raise CompilationError("function parameters cannot be of type struct.", param)

        cparam = c.VarDecl(mangle_var(param, ctx), c.QualType(c_type))
        param_obj.c_node = cparam
        param_obj.is_pseudo = param.is_pseudo
        if not param.is_pseudo:
            cfunc.params.append(cparam)

        param_objs.append(param_obj)
        ctx.ns[param_obj.xy_node.name] = param_obj

    return param_objs, any_default_value_params

def compile_ret_err_types(node, cast, cfunc, ctx):
    eval_stored_value = ctx.eval_calltime_exprs
    ctx.eval_calltime_exprs = False

    etype_compiled = None
    any_refs = False
    if return_by_param(node):
        for iret, ret in enumerate(node.returns):
            if ctx.eval(ret.type) is ctx.void_obj:
                rtype_compiled = ctx.void_obj
                assert len(node.returns) == 1
                continue
            param_name = f"__{ret.name}" if ret.name else f"_res{iret}"
            retparam = c.VarDecl(param_name, c.QualType(get_c_type(ret.type, cast, ctx) + "*"))
            cfunc.params.append(retparam)
            rtype_compiled = ctx.get_compiled_type(ret.type)
            any_refs = any_refs or ret.is_index
        if node.etype is not None:
            etype_compiled = ctx.get_compiled_type(node.etype)
    elif len(node.returns) == 1:
        rtype_compiled = ctx.get_compiled_type(node.returns[0].type)
        any_refs = any_refs or node.returns[0].is_index
    else:
        rtype_compiled = ctx.void_obj

    has_calltime_tags = remove_calltime_tags(rtype_compiled) if rtype_compiled is not None else False

    ctx.eval_calltime_exprs = eval_stored_value

    return rtype_compiled, etype_compiled, any_refs, has_calltime_tags

def fill_param_default_values(fobj, cast, ctx):
    # This func is not needed any more. The only useful thing it does now
    # is to check for the length of arrays which can easily be accomblished in
    # compile_func_prototype.
    # TODO Remove this func.
    ctx.push_ns()
    for pobj in fobj.param_objs:
        if pobj.type_desc is not None:
            ctx.ns[pobj.xy_node.name] = pobj
            continue
        if pobj.xy_node.value is None:
            raise CompilationError("Cannot infer type", pobj.xy_node)
        type_obj = do_infer_type(pobj.xy_node.value, cast, ctx)
        pobj.type_desc = type_obj

        c_type = pobj.type_desc.c_name
        if pobj.passed_by_ref:
            c_type = c_type + "*"
        pobj.c_node.qtype = c.QualType(c.Type(c_type))

        ctx.ns[pobj.xy_node.name] = pobj
    ctx.pop_ns()

    for pobj in fobj.param_objs:
        if isinstance(pobj.type_desc, ArrTypeObj) and len(pobj.type_desc.dims) == 0:
            if not pobj.is_pseudo:
                raise CompilationError(
                    "Only pseudo params are allowed to have a length not known "
                    "at compile time", pobj.xy_node
                )

    return fobj

def remove_calltime_tags(obj: CompiledObj):
    has_any = False
    tags = obj.tags

    for tag in tags.values():
        if tag is calltime_expr_obj:
            has_any = True
            break

    if has_any:
        obj.tags = {}
        for label, tag in tags.items():
            if tag is not calltime_expr_obj:
                obj.tags[label] = tag

    for tag in obj.tags.values():
        any_removed = remove_calltime_tags(tag)
        has_any = has_any or any_removed

    return has_any

def compile_builtins(builder, module_name, asts, module_path):
    mh, _ = compile_module(builder, module_name, asts, module_path)
    cast = c.Ast()

    # always include it as it is everywhere
    cast.includes.append(c.Include("stdint.h"))
    cast.includes.append(c.Include("stddef.h"))
    cast.includes.append(c.Include("stdbool.h"))

    for obj in itertools.chain(mh.ctx.data_ns.values(), mh.ctx.func_ns.values()):
        obj.builtin = True

        if isinstance(obj, FuncSpace):
            for func_obj in obj._funcs:
                func_obj.builtin = True

        if isinstance(obj, TypeObj):
            ctype_map = {
                "Byte": "int8_t", "Ubyte": "uint8_t",
                "Short": "int16_t", "Ushort": "uint16_t",
                "Int": "int32_t", "Uint": "uint32_t", "Char": "int32_t",
                "Long": "int64_t", "Ulong": "uint64_t",
                "Size": "size_t",
                "Float": "float", "Double": "double",
                "Bool": "bool", "void": "void",
                "Ptr": "void*",
                "Bits8": "uint8_t", "Bits16": "uint16_t",
                "Bits32": "uint32_t", "Bits64": "uint64_t",
            }
            bits_to_numeric_map = {
                "Bits8": "Ubyte", "Bits16": "Ushort",
                "Bits32": "Uint", "Bits64": "Ulong",
            }
            if obj.xy_node.name in ctype_map:
                obj.c_node.name = ctype_map[obj.xy_node.name]
                obj.init_value = c.Const(0)
                if not obj.xy_node.name.startswith("Bits"):
                    obj.fields = {
                        "": VarObj(type_desc=obj, xy_node=xy.VarDecl())
                    }

            default_tag_label_map = {
                "TagCtor": "xyTag",
                "StrCtor": "xyStr",
                "UnstrCtor": "xy.unstr",
                "EntryPoint": "xy.entrypoint",
                "IterCtor": "xyIter",
                "Clib": "xyc.lib",
            }
            if obj.xy_node.name in default_tag_label_map:
                label = default_tag_label_map[obj.xy_node.name]
                obj.tags["xyTag"] = InstanceObj(
                    kwargs={
                        "label": StrObj(parts=[ConstObj(value=label)])
                    },
                    type_obj=mh.ctx.data_ns["TagCtor"]
                )

    return mh, cast

def compile_ctti(builder, module_name, asts, module_path):
    mh, _ = compile_module(builder, module_name, asts, module_path)
    cast = c.Ast()

    for obj in itertools.chain(mh.ctx.data_ns.values(), mh.ctx.func_ns.values()):
        obj.builtin = True

        if isinstance(obj, FuncSpace):
            for func_obj in obj._funcs:
                func_obj.builtin = True

    return mh, cast

def compile_func(fdesc, cast, ctx):
    node = fdesc.xy_node
    cfunc = fdesc.c_node

    ctx.push_ns()
    for param_obj in fdesc.param_objs:
        if param_obj.xy_node.name in ctx.ns:
            raise CompilationError(f"Parameter {param_obj.xy_node.name} already defined", param_obj.xy_node)
        ctx.ns[param_obj.xy_node.name] = param_obj

    ctx.current_fobj = fdesc
    if isinstance(node.body, list):
        ctx.enter_func()
        compile_body(node.body, cast, cfunc, ctx, is_func_body=True)

    ctx.current_fobj = None

    if not fdesc.is_macro:
        cast.funcs.append(cfunc)
    fdesc.decl_visible = True

    if node.name.name == "dtor" and len(fdesc.param_objs) > 0:
        # auto call dtors for fields
        call_dtors_for_fields(fdesc.param_objs[0], cast, cfunc, ctx)

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
            validate_name(node, ctx)
            vardecl_obj = compile_vardecl(node, cast, cfunc, ctx)
            if len(cfunc.body) > 0 and isinstance(cfunc.body[-1], c.Label):
                cfunc.body.append(c.InlineCode(""))  # don't generate a label to a definition which is c23 specific
            cfunc.body.append(vardecl_obj.c_node)
        else:
            expr_obj = compile_expr(node, cast, cfunc, ctx, deref=False)
            if isinstance(expr_obj, IdxObj):
                # a dangling index. No point in decaying it completely as the
                # result will be discarded. But the base and index parts do need
                # to be computed
                base_obj = maybe_deref(expr_obj.container, True, cast, cfunc, ctx)
                if base_obj.c_node is not None and not is_simple_cexpr(base_obj.c_node):
                    cfunc.body.append(base_obj.c_node)
                idx_obj = maybe_deref(expr_obj.idx, True, cast, cfunc, ctx)
                if idx_obj.c_node is not None and not is_simple_cexpr(idx_obj.c_node):
                    cfunc.body.append(idx_obj.c_node)
            elif expr_obj.c_node is not None and not isinstance(expr_obj.c_node, c.Id):
                cfunc.body.append(expr_obj.c_node)

    # call dtors if any
    if len(body) > 0 and not isinstance(body[-1], (xy.Return, xy.Break)):
        call_dtors(ctx.ns, cast, cfunc, ctx)

    # add no error return if needed
    if is_func_body and ctx.current_fobj.etype_obj is not None:
        if len(body) == 0 or not isinstance(body[-1], (xy.Return, xy.Error)):
            cfunc.body.append(c.Return(ctx.current_fobj.etype_obj.init_value))

    ctx.exit_block()

def call_dtors_for_fields(obj: VarObj, cast, cfunc, ctx):
    type_obj = obj.type_desc
    for name, field in type_obj.fields.items():
        if not field.is_pseudo and field.needs_dtor:
            expr_obj = field_get(var_to_expr_obj(obj.xy_node, obj, cast, cfunc, ctx, True), field, cast, cfunc, ctx)
            call_dtor(expr_obj, cast, cfunc, ctx)

def call_dtor(obj, cast, cfunc, ctx):
    if not isinstance(obj.inferred_type, ArrTypeObj):
        dtor_obj = find_and_call("dtor", ArgList([obj]), cast, cfunc, ctx, obj.xy_node)
        cfunc.body.append(dtor_obj.c_node)
    else:
        cfor = c.For(
            [c.VarDecl("_i", qtype=c.QualType(c.Type("size_t"), is_const=False), value=c.Const(0))],
            c.Expr(c.Id("_i"), c.Const(obj.inferred_type.dims[0]), op="<"),
            [c.UnaryExpr(c.Id("_i"), op="++", prefix=True)]
        )
        dtor_arg_obj = ExprObj(
            xy_node=obj.xy_node,
            c_node=c.Index(obj.c_node, index=c.Id("_i")),
            inferred_type=obj.inferred_type.base_type_obj,
        )
        dtor_obj = find_and_call("dtor", ArgList([dtor_arg_obj]), cast, cfunc, ctx, obj.xy_node)
        cfor.body.append(dtor_obj.c_node)
        cfunc.body.append(cfor)

def call_dtors(ns, cast, cfunc, ctx):
    for obj in reversed(ns.values()):
        if isinstance(obj, VarObj) and obj.needs_dtor and not obj.xy_node.is_param:
            if obj.is_stored_global:
                restore_global(obj, cast, cfunc, ctx)
                continue
            expr = ExprObj(
                xy_node=obj.xy_node,
                c_node=c.Id(obj.c_node.name),
                inferred_type=obj.inferred_type,
                compiled_obj=obj
            )
            call_dtor(expr, cast, cfunc, ctx)

def call_all_dtors(cast, cfunc, ctx):
    # first 2 are global and local namespaces
    for ns in reversed(ctx.data_namespaces[2:]):
        call_dtors(ns, cast, cfunc, ctx)

def any_dtors(ctx):
    # TODO optimize that function
    for ns in ctx.data_namespaces[2:]:
        for _, obj in ns.items():
            if isinstance(obj, VarObj) and obj.needs_dtor:
                return True
    return False

def type_needs_dtor(type_obj: TypeObj):
    if type_obj is None:
        return False
    elif isinstance(type_obj, ArrTypeObj):
        return type_obj.base_type_obj.needs_dtor
    else:
        return type_obj.needs_dtor

def compile_vardecl(node, cast, cfunc, ctx):
    var_name = node.name
    mangled_name = mangle_var(node, ctx)
    cvar = c.VarDecl(name=mangled_name, qtype=c.QualType(is_const=not node.mutable))
    value_obj = compile_expr(node.value, cast, cfunc, ctx) if node.value is not None else None
    if node.is_move:
        value_obj = move_out(value_obj, cast, cfunc, ctx)
    if isinstance(value_obj, IdxObj):
        value_obj = idx_get(value_obj, cast, None, ctx)

    if value_obj is not None and value_obj.compiled_obj is not None:
        if isinstance(value_obj.compiled_obj, (TypeObj, TypeExprObj)):
            raise CompilationError(
                "Cannot assign a type to a variable. Did you forget to instantiate it?", node
            )
        if isinstance(value_obj.compiled_obj, ImportObj):
            raise CompilationError("Invalid value for variable", node)

    type_desc = find_type(node.type, cast, ctx) if node.type is not None else None
    if type_desc is None:
        if value_obj is None:
            raise CompilationError(
                "Cannot create variable with no type and no value",
                node
            )
        type_desc = value_obj.inferred_type
        if isinstance(type_desc, TypeInferenceError):
            raise CompilationError(
                type_desc.msg,
                node
            )

    if isinstance(type_desc, ArrTypeObj):
        if len(type_desc.dims) == 0:
            raise CompilationError(
                "Only pseudo params are allowed to have a length not known "
                    "at compile time", node)
        cvar.qtype.type.name = type_desc.base_type_obj.c_name
        cvar.qtype.type.dims = type_desc.dims
    elif isinstance(type_desc, (TypeObj, TypeExprObj)):
        cvar.qtype.type.name = type_desc.c_name
    else:
        err_node = node.type if node.type is not None else node
        err_msg = ("Compiler bug! Report to devs at TBD" if type_desc is None
                   else "Not a type")
        raise CompilationError(err_msg, err_node)

    if type_desc.needs_dtor:
        cvar.qtype.is_const = False

    if isinstance(type_desc, FuncTypeObj):
        # XXX Hack to corrent the name of the function that should be called
        type_desc = copy(type_desc)
        type_desc.func_obj = copy(type_desc.func_obj)
        type_desc.func_obj.c_node = cvar

    needs_dtor = type_needs_dtor(type_desc)

    res_obj = VarObj(node, cvar, type_desc, needs_dtor=needs_dtor)

    if var_name in ctx.ns:
        raise CompilationError(
            f"Varaible '{var_name}' already defined", node,
            notes=[("Previous definition", ctx.ns[var_name].xy_node)]
        )
    ctx.ns[var_name] = res_obj

    if value_obj is not None:
        if isinstance(type_desc, ArrTypeObj):
            cvar.value = expand_array_to_init_list(value_obj)
        else:
            cvar.value = value_obj.c_node
    else:
        if isinstance(type_desc, ArrTypeObj):
            cvar.value = c.InitList(elems=[c.Const(0)])
        else:
            cvar.value = type_desc.init_value

    # TODO check if types support assignment

    # auto move if RHS is a tmp i.e. disable dtor
    if value_obj is not None and is_tmp_expr(value_obj) and value_obj.compiled_obj is not None:
        value_obj.compiled_obj.needs_dtor = False

    # remove repeated type in case of struct literals or casts
    if isinstance(cvar.value, c.CompoundLiteral):
        cvar.value = c.InitList(elems=cvar.value.args)
    elif isinstance(cvar.value, c.Cast) and cvar.value.to == res_obj.type_desc.c_name and not cvar.value.to.endswith("*"):
        # the not cvar.value.to.endswith("*") is purely a matter or personal preference
        cvar.value = cvar.value.what

    return res_obj

def mangle_var(node: xy.VarDecl, ctx: CompilerContext):
    if node.is_param:
        return f"p_{node.name}"
    return f"l_{node.name}"

def expand_array_to_init_list(value_obj: ExprObj):
    if isinstance(value_obj.c_node, c.InitList):
        # already an init list
        return value_obj.c_node

    res = c.InitList()
    if len(value_obj.inferred_type.dims) <= 0:
        raise CompilationError("Cannot determine array dimensions", value_obj.xy_node)
    for i in range(0, value_obj.inferred_type.dims[0]):
        res.elems.append(c.Index(value_obj.c_node, c.Const(i)))
    return res

c_symbol_type = TypeInferenceError(
    "The types of c symbols cannot be inferred. Please be explicit and specify the type."
)

def compile_expr(expr, cast, cfunc, ctx: CompilerContext, deref=True) -> ExprObj:
    res = do_compile_expr(expr, cast, cfunc, ctx, deref=deref)
    return res

def do_compile_expr(expr, cast, cfunc, ctx: CompilerContext, deref=True) -> ExprObj:
    if isinstance(expr, xy.Const):
        return compile_const(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.BinExpr):
        if expr.op not in {'.', '=', '.=', '..', '=<', '+=', '-=', '*=', '/=', '@=', '@'}:
            return compile_binop(expr, cast, cfunc, ctx)
        elif expr.op == '.':
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx, deref=False)
            if isinstance(arg1_obj.inferred_type, ImportObj):
                assert arg1_obj.inferred_type.is_external
                if not isinstance(expr.arg2, xy.Id):
                    raise CompilationError("Expected identifier", expr.arg2)
                field_name = expr.arg2.name
                res = c.Id(field_name)
                return ExprObj(
                    c_node=res,
                    xy_node=expr,
                    inferred_type=c_symbol_type
                )
            else:
                return do_compile_field_get(arg1_obj, expr.arg2, cast, cfunc, ctx, deref=deref, expr=expr)
        elif expr.op in {'+=', '-=', '*=', '/=', '&&=', '||='}:
            val_obj = compile_expr(expr.arg2, cast, cfunc, ctx)
            acc_obj = compile_expr(expr.arg1, cast, cfunc, ctx, deref=False)
            acc_tmp = maybe_move_to_temp(acc_obj, cast, cfunc, ctx)
            math_op = find_and_call(operatorToFname[expr.op[0]], ArgList([acc_tmp, val_obj]), cast, cfunc, ctx, expr)
            return compile_assign(acc_obj, math_op, cast, cfunc, ctx, expr)
        elif expr.op == '@=':
            if not isinstance(expr.arg2, xy.ForExpr):
                acc_obj = compile_expr(expr.arg1, cast, cfunc, ctx, deref=False)
                return do_compile_append(acc_obj, expr.arg2, cast, cfunc, ctx, expr)
            # else list comprihension like expression but with @=
            list_comp = xy.ListComprehension(list_type=expr.arg1, loop=expr.arg2, coords=expr.coords, src=expr.src)
            return compile_list_comprehension(list_comp, cast, cfunc, ctx, is_assign=True)
        elif expr.op == '@':
            acc_obj = compile_expr(expr.arg1, cast, cfunc, ctx, deref=False)
            if not isinstance(acc_obj.compiled_obj, (TypeExprObj, TypeObj)):
                copy_obj = find_and_call("copy", ArgList([acc_obj]), cast, cfunc, ctx, expr)
            else:
                copy_obj = ExprObj(
                    expr, c_node=acc_obj.compiled_obj.init_value, inferred_type=acc_obj.inferred_type,
                )
            tmp_obj = ctx.create_tmp_var(copy_obj.inferred_type, "comp")
            tmp_obj.c_node.value = copy_obj.c_node
            cfunc.body.append(tmp_obj.c_node)
            tmp_obj = ExprObj(
                expr,
                c_node=c.Id(tmp_obj.c_node.name),
                inferred_type=tmp_obj.inferred_type,
                compiled_obj=tmp_obj,
            )
            return do_compile_append(tmp_obj, expr.arg2, cast, cfunc, ctx, expr)
        elif expr.op == '.=':
            if not (isinstance(expr.arg2, xy.StructLiteral) and expr.arg2.name is None):
                raise CompilationError("The right hand side of the '.=' operator must be an anonymous struct literal")
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx, deref=False)
            _ = do_compile_struct_literal(expr.arg2, arg1_obj.inferred_type, arg1_obj, cast, cfunc, ctx)
            return ExprObj(
                c_node=None,
                inferred_type=arg1_obj.inferred_type
            )
        elif expr.op in {"=", "=<"}:
            if isinstance(expr.arg1, xy.Select):
                if expr.arg1.base is not None:
                    container_obj = compile_expr(expr.arg1.base, cast, cfunc, ctx, deref=False)
                else:
                    container_obj = global_memory
                assert len(expr.arg1.args.args) == 1
                assert len(expr.arg1.args.kwargs) == 0
                idx_obj = compile_expr(expr.arg1.args.args[0], cast, cfunc, ctx, deref=None)
                value_obj = compile_expr(expr.arg2, cast, cfunc, ctx, deref=False)
                if expr.op == "=<":
                    value_obj = move_out(value_obj, cast, cfunc, ctx)
                value_obj = maybe_deref(value_obj, True, cast, cfunc, ctx)
                return idx_set(IdxObj(xy_node=expr, container=container_obj, idx=idx_obj), value_obj, cast, cfunc, ctx)
            elif isinstance(expr.arg1, xy.StrLiteral):
                return compile_unstring(expr.arg1, expr.arg2, cast, cfunc, ctx)

            arg2_obj = compile_expr(expr.arg2, cast, cfunc, ctx)
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx, deref=False)

            return compile_assign(arg1_obj, arg2_obj, cast, cfunc, ctx, expr, expr.op=="=<")
        else:
            # compile get tag
            assert expr.op == ".."
            if not isinstance(expr.arg2, (xy.Id, xy.Enumeration)):
                raise CompilationError("Invalid expression", expr.arg2)
            if isinstance(expr.arg2, xy.Enumeration) and len(expr.arg2.items) > 2:
                raise CompilationError("Expected '..(tagname, defaultValue)'", expr.arg2);

            tag_name_node = expr.arg2 if isinstance(expr.arg2, xy.Id) else expr.arg2.items[0]
            def_val_node = None
            if isinstance(expr.arg2, xy.Enumeration) and len(expr.arg2.items) <= 2:
                def_val_node = expr.arg2.items[1]

            field_name = tag_name_node.name
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx)
            tag_obj = tag_get(expr, arg1_obj, field_name, ctx, def_val_node)
            if isinstance(tag_obj, (TypeObj, TypeExprObj)):
                return ExprObj(
                    c_node=c.Id(tag_obj.c_node.name),
                    inferred_type=tag_obj,
                )
            else:
                return ExprObj(
                    c_node=tag_obj.c_node,
                    inferred_type=tag_obj.inferred_type,
                )
    elif isinstance(expr, xy.UnaryExpr) and expr.op == '=>':
        lhs_obj = compile_expr(expr.arg, cast, cfunc, ctx)
        tmp_obj = move_out(lhs_obj, cast, cfunc, ctx)
        return tmp_obj
    elif isinstance(expr, xy.UnaryExpr) and expr.op == '&':
        arg_obj = compile_expr(expr.arg, cast, cfunc, ctx, deref=False)
        if isinstance(arg_obj, IdxObj):
            return ExprObj(
                expr,
                c_node=arg_obj.idx.c_node,
                inferred_type=arg_obj.idx.inferred_type,
                tags=arg_obj.idx.tags
            )
        elif isinstance(arg_obj.compiled_obj, VarObj):
            return compile_builtin_addrof(expr, arg_obj, cast, cfunc, ctx)
        else:
            raise CompilationError("Expression doesn't evaluate to a ref", expr.arg)
    elif isinstance(expr, xy.UnaryExpr) and expr.op == '%':
        # compile typeof
        arg_obj = compile_expr(expr.arg, cast, cfunc, ctx)
        return ExprObj(
            xy_node=expr,
            c_node=c.Id(arg_obj.inferred_type.c_node.name),
            inferred_type=arg_obj.inferred_type,
            tags=arg_obj.inferred_type.tags,
            compiled_obj=arg_obj.inferred_type,
        )
    elif isinstance(expr, xy.UnaryExpr):
        fcall = rewrite_unaryop(expr, ctx)
        return compile_expr(fcall, cast, cfunc, ctx)
    elif isinstance(expr, xy.Id):
        var_obj = ctx.eval(expr, f"Cannot find variable '{expr.name}'")
        if isinstance(var_obj, VarObj):
            return var_to_expr_obj(expr, var_obj, cast, cfunc, ctx, deref)
        elif isinstance(var_obj, TypeObj):
            return ExprObj(
                xy_node=expr,
                c_node=c.Id(var_obj.c_node.name),
                inferred_type=var_obj,
                compiled_obj=var_obj,
            )
        elif isinstance(var_obj, ImportObj):
            return ExprObj(
                c_node=None,
                xy_node=var_obj.xy_node,
                inferred_type=var_obj,
                compiled_obj=var_obj,
            )
        elif isinstance(var_obj, ExprObj):
            return maybe_deref(var_obj, deref, cast, cfunc, ctx)
        elif isinstance(var_obj, LazyObj):
            if isinstance(var_obj.xy_node, xy.CallerContextExpr):
                assert var_obj.ctx is not None
                res = compile_expr(var_obj.xy_node.arg, cast, cfunc, var_obj.ctx)
            else:
                res = compile_expr(var_obj.xy_node, cast, cfunc, var_obj.ctx or ctx)
            res.from_lazy_ctx = var_obj.ctx or ctx
            return res
        elif isinstance(var_obj, InstanceObj):
            return ExprObj(
                c_node=var_obj.c_node,
                xy_node=expr,
                inferred_type=var_obj.type_obj,
                compiled_obj=var_obj,
            )
        else:
            raise CompilationError("Invalid expression", expr)
    elif isinstance(expr, xy.CatchExpr):
        catch_var_name = ctx.gen_tmp_name("catch")
        catch_err_label = ctx.gen_tmp_label_name("catch")
        frame = CatchFrame(catch_var_name, catch_err_label)
        c_vardecl = c.VarDecl(catch_var_name)
        cfunc.body.append(c_vardecl)

        ctx.push_catch_frame(frame)
        expr_obj = compile_expr(expr.expr, cast, cfunc, ctx, deref)
        ctx.pop_catch_frame()

        if not is_simple_cexpr(expr_obj.c_node):
            cfunc.body.append(expr_obj.c_node)

        # optimizations for cleaner code
        if not (
            frame.ref_count <= 1 and len(cfunc.body) > 0 and isinstance(cfunc.body[-1], c.If) and
            len(cfunc.body[-1].body) == 1 and isinstance(cfunc.body[-1].body[0], c.Goto) and
            cfunc.body[-1].body[0].label.name == catch_err_label
        ):
            cfunc.body.append(c.Label(catch_err_label))
        else:
            cfunc.body.pop()

        if frame.inferred_type is None:
            raise CompilationError("Expression doesn't produce any errors", expr)
        c_vardecl.value = frame.inferred_type.init_value
        c_vardecl.qtype = c.QualType(c.Type(frame.inferred_type.c_name), is_const=False)

        return ExprObj(
            xy_node=expr,
            c_node=c.Id(catch_var_name),
            inferred_type=frame.inferred_type,
        )
    elif isinstance(expr, xy.FuncCall):
        return maybe_deref(
            compile_fcall(expr, cast, cfunc, ctx),
            deref, cast, cfunc, ctx
        )
    elif isinstance(expr, xy.FuncSelect):
        return compile_fselect(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.StructLiteral):
        return compile_struct_literal(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.StrLiteral):
        return compile_strlit(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.ArrayLit):
        res = c.InitList()
        arr_type = None if expr.base is None else find_type(expr.base, cast, ctx)
        elem_objs = []
        for elem in expr.elems:
            elem_expr = compile_expr(elem, cast, cfunc, ctx)
            elem_objs.append(elem_expr)
            res.elems.append(elem_expr.c_node)
            if arr_type is None:
                arr_type = ArrTypeObj(base_type_obj=elem_expr.inferred_type, dims=[len(expr.elems)])

        if arr_type is None:
            arr_type = "Cannot infer type of empty list"
        elif isinstance(arr_type, ArrTypeObj):
            if len(arr_type.dims) == 0:
                arr_type.dims = [len(expr.elems)]
            elif arr_type.dims[0] < len(expr.elems):
                raise CompilationError("Init list longer than array length", expr)
            elif arr_type.dims[0] > len(expr.elems) and not arr_type.base_type_obj.is_init_value_zeros:
                for i in range(arr_type.dims[0] - len(expr.elems)):
                    res.elems.append(arr_type.base_type_obj.init_value)

            if len(res.elems) == 0:
                res.elems.append(c.Const(0))
        else: # array literal with not array type
            if isinstance(arr_type, (TypeObj, TypeExprObj)):
                tmp = ctx.create_tmp_var(arr_type, "arr_comp", xy_node=expr)
                tmp.needs_dtor = False
                cfunc.body.append(tmp.c_node)
                res = c.Id(tmp.c_node.name)
            else:
                arr_obj = arr_type
                if isinstance(arr_obj, VarObj):
                    arr_obj = ExprObj(
                        xy_node=arr_obj.xy_node,
                        c_node=c.Id(arr_obj.c_node.name),
                        inferred_type=arr_obj.inferred_type,
                        compiled_obj=arr_obj,
                    )
                    arr_type = arr_obj.inferred_type
                tmp = copy_to_temp(arr_obj, cast, cfunc, ctx)
                tmp.compiled_obj.needs_dtor = False
                res = tmp.c_node

            tmp_expr = ExprObj(
                xy_node=expr,
                c_node=res,
                inferred_type=arr_type
            )

            for elem_obj in elem_objs:
                push_call = find_and_call(
                    "push", ArgList([tmp_expr, elem_obj]),
                    cast, cfunc, ctx, xy_node=expr,
                )
                cfunc.body.append(push_call.c_node)

        return ExprObj(
            xy_node=expr,
            c_node=res,
            inferred_type=arr_type
        )
    elif isinstance(expr, xy.ListComprehension):
        return compile_list_comprehension(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.Select):
        # rewritten = rewrite_select(expr, ctx)
        idx_obj = compile_select(expr, cast, cfunc, ctx)
        return maybe_deref(idx_obj, deref, cast, cfunc, ctx)
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
    elif isinstance(expr, xy.Continue):
        return compile_continue(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.AttachTags):
        obj = compile_expr(expr.arg, cast, cfunc, ctx)
        tag_specs = []
        if isinstance(obj.inferred_type, TypeExprObj):
            obj.inferred_type = copy(obj.inferred_type)
            obj.inferred_type.tags = copy(obj.inferred_type.tags)
            tag_specs = obj.inferred_type.type_obj.tag_specs
        elif isinstance(obj.inferred_type, TypeObj):
            obj.inferred_type = TypeExprObj(
                xy_node=expr, c_node=obj.inferred_type.c_node,
                type_obj=obj.inferred_type, tags=copy(obj.inferred_type.tags)
            )
            tag_specs = obj.inferred_type.type_obj.tag_specs
        tags_to_attach = ctx.eval_tags(expr.tags, tag_specs=tag_specs)
        obj.inferred_type.tags.update(tags_to_attach) # tags are attached to the type
        if is_ptr_type(obj.inferred_type, ctx) and "to" in tags_to_attach:
            obj.c_node = optimize_cast(c.Cast(obj.c_node, obj.inferred_type.c_name))
        return obj
    elif isinstance(expr, xy.SliceExpr):
        # rewrite slice
        if expr.op is not None:
            if expr.op not in {"+", "-", "*"}:
                raise CompilationError(f"'{expr.op}' slices are not supported.", expr)
            tmp_obj = ctx.compile_tmp_var(expr.start, cast, cfunc, name_hint="slice")
            expr = copy(expr)  # TODO test this
            expr.start = xy.Id(tmp_obj.xy_node.name, src=expr.start.src, coords=expr.start.coords)
            expr.end = xy.BinExpr(expr.start, expr.end, op=expr.op, src=expr.src, coords=expr.coords)
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
    elif isinstance(expr, xy.CallerContextExpr):
        return compile_caller_context_expr(expr, cast, cfunc, ctx)
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)

def var_to_expr_obj(expr, var_obj, cast, cfunc, ctx, deref):
    c_node = c.Id(var_obj.c_node.name) if var_obj.c_node is not None else None
    if var_obj.passed_by_ref:
        res = IdxObj(
            xy_node=expr,
            inferred_type=var_obj.type_desc,
            container=param_container,
            c_node=c.UnaryExpr(c_node, op="*", prefix=True),  # references are the only one with a c_node
            idx=ExprObj(
                xy_node=expr,
                c_node=c_node,
                inferred_type=ptr_type_to(var_obj.type_desc, ctx)
            )
        )
        return maybe_deref(res, deref, cast, cfunc, ctx)

    return ExprObj(
        xy_node=expr,
        c_node=c_node,
        inferred_type=var_obj.type_desc,
        compiled_obj=var_obj,
    )

def do_compile_append(dst_obj, val: xy.Node, cast, cfunc, ctx, expr):
    vals = [val]
    if isinstance(val, xy.StructLiteral) and val.name is None:
            vals = val.args
    for val_expr in vals:
        val_obj = compile_expr(val_expr, cast, cfunc, ctx)
        append_fcall = find_and_call_append(ArgList([dst_obj, val_obj]), cast, cfunc, ctx, expr)
        cfunc.body.append(append_fcall.c_node)
    return dst_obj

def find_and_call_append(arg_list: ArgList, cast, cfunc, ctx, expr):
    fobj: FuncObj = find_func_obj("append", arg_list, cast, cfunc, ctx, expr)

    if fobj.move_args_to_temps:
        # we move the last argument if we need to. Previous arguments must have
        # been moved by the function caller
        arg_list.args[-1] = maybe_move_to_temp(arg_list.args[-1], cast, cfunc, ctx)

    return do_compile_fcall(
        expr,
        fobj,
        arg_exprs=arg_list,
        cast=cast, cfunc=cfunc, ctx=ctx
    )

def compile_const(expr, cast, cfunc, ctx):
    rtype_obj = ctx.get_compiled_type(xy.Id(
        expr.type, src=expr.src, coords=expr.coords
    ))
    value = expr.value_str
    type_cast = None
    if expr.type == "Char":
        # chars need escaping and conversion to unicode
        value = value.replace("\\`", "`")
        expected_len = 1 if not value.startswith('\\') else 2
        if len(value) != expected_len:
            raise CompilationError("Invalid char literal", expr)
        if not value.startswith('\\'):
            codepoint = ord(value)
            if codepoint > 127:
                value = format(codepoint, "#06x")
            else:
                value = f"'{value}'"
        else:
            value = f"'{value}'"
    elif expr.type in {"Short", "Ushort", "Byte", "Ubyte", "Size"}:
        type_cast = rtype_obj.c_name

    c_val = expr.value
    type_limits = {
        "Byte": (-2**7, 2**7-1),
        "Short": (-2**15, 2**15-1),
        "Int": (-2**31, 2**31-1),
        "Long": (-2**63, 2**63-1),
        "Ubyte": (0, 2**8-1),
        "Ushort": (0, 2**16-1),
        "Uint": (0, 2**32-1),
        "Ulong": (0, 2**64-1),
        "Size": (0, 2**64-1),  # TODO what about 32-bit archs
    }
    if expr.type in type_limits:
        min_lim, max_lim = type_limits[expr.type]
        if expr.value_str.startswith("0x") and c_val > 0 and min_lim < 0:
            # special case of 0x which is not quite base-16 but allows to specify bytes
            max_lim += -min_lim
            min_lim = 0
        error = None
        if c_val < min_lim:
            error = "underflows"
        elif c_val > max_lim:
            error = "overflows"
        if error:
            raise CompilationError(f"Integer constant {error} type '{expr.type}'", expr)

    c_res = c.Const(value=c_val, value_str=value)
    if type_cast:
        c_res = c.Cast(c_res, type_cast)

    return ExprObj(
        xy_node=expr,
        c_node=c_res,
        inferred_type=rtype_obj,
    )

def compile_assign(dest_obj, value_obj, cast, cfunc, ctx, expr_node, is_move=False):
    check_type_compatibility(expr_node, dest_obj, value_obj, ctx)

    if is_move:
        value_obj = move_out(value_obj, cast, cfunc, ctx)
        if dest_obj.inferred_type.needs_dtor:
            call_dtor(dest_obj, cast, cfunc, ctx)

    if isinstance(dest_obj, IdxObj):
        res = idx_set(dest_obj, value_obj, cast, cfunc, ctx)
        res.c_node = optimize_acc_expr(res.c_node)
        return res
    else:
        res = c.Expr(dest_obj.c_node, value_obj.c_node, op="=")
        res = optimize_acc_expr(res)
        return ExprObj(
            xy_node=expr_node,
            c_node=res,
            inferred_type=value_obj.inferred_type
        )

def move_out(obj: ExprObj, cast, cfunc, ctx):
    if is_tmp_expr(obj) or not is_lvalue(obj):
        return obj

    tmp_obj = copy_to_temp(obj, cast, cfunc, ctx)
    if is_tmp_expr(tmp_obj):
        tmp_obj.compiled_obj.needs_dtor = False
    # break the connection between the temp and the value as once we move out
    # there is no longer a connection. Note this is different to copying to a tmp
    # value as argument evaluation order doesn't guarantee lack of incompatable
    # aliasing. Moving out does b/c we reset the value.
    tmp_obj.compiled_obj = None
    reset_obj(obj, cast, cfunc, ctx)
    return tmp_obj

def is_lvalue(obj: ExprObj):
    return isinstance(obj, IdxObj) or isinstance(obj.compiled_obj, (VarObj, IdxObj))

def reset_obj(obj: ExprObj, cast, cfunc, ctx):
    if isinstance(obj, IdxObj):
        def_value_obj = ExprObj(
            xy_node=obj.xy_node,
            c_node=obj.inferred_type.init_value,
            inferred_type=obj.inferred_type
        )
        obj = idx_set(obj, def_value_obj, cast, cfunc, ctx)
        if not isinstance(obj.c_node, c.Id):
            cfunc.body.append(obj.c_node)
    elif isinstance(obj.inferred_type, ArrTypeObj):
        cfor = create_loop_over_array(obj, cast, cfunc, ctx)
        elem_obj = copy(obj)
        elem_obj.inferred_type = obj.inferred_type.base_type_obj
        elem_obj.c_node = c.Index(obj.c_node, index=c.Id(cfor.inits[0].name))
        reset_obj(elem_obj, cast, cfor, ctx)
        cfunc.body.append(cfor)
    else:
        c_reset = c.Expr(obj.c_node, obj.inferred_type.init_value, op="=")
        cfunc.body.append(c_reset)

def create_loop_over_array(obj, cast, cfunc, ctx: CompilerContext):
    tmp_i = ctx.create_tmp_var(ctx.size_obj, "i", obj.xy_node)
    cfor = c.For(
        [tmp_i.c_node],
        c.Expr(c.Id(tmp_i.c_node.name), c.Const(obj.inferred_type.dims[0]), op="<"),
        [c.UnaryExpr(c.Id(tmp_i.c_node.name), op="++", prefix=True)]
    )
    return cfor

def optimize_acc_expr(c_expr):
    if (isinstance(c_expr, c.Expr) and c_expr.op == "=" and
        isinstance(c_expr.arg2, c.Expr) and c_expr.arg1 == c_expr.arg2.arg1):
        return c.Expr(c_expr.arg1, c_expr.arg2.arg2, op=c_expr.arg2.op+"=")
    return c_expr

def optimize_cbinop(c_expr):
    if (isinstance(c_expr, c.Expr) and c_expr.op == "-" and
        isinstance(c_expr.arg1, c.Const) and c_expr.arg1.value == 0):
        return c.UnaryExpr(c_expr.arg2, op="-", prefix=True)
    return c_expr

def optimize_cast(c_expr):
    assert isinstance(c_expr, c.Cast)
    if c_expr.to[-1] == "*" and isinstance(c_expr.what, c.Cast) and c_expr.what.to[-1] == "*":
        # remove double cast
        c_expr = c.Cast(c_expr.what.what, c_expr.to)
    if c_expr.to == "char*" and isinstance(c_expr.what, c.Const) and isinstance(c_expr.what.value, str):
        # remove cast to char* for string literals
        c_expr = c_expr.what
    return c_expr

def optimize_if(c_if: c.If):
    if is_c_false(c_if.cond):
        return c_if.else_body
    elif is_c_true(c_if.cond):
        return c_if.body
    return c_if

def is_c_false(c_node):
    return isinstance(c_node, c.Const) and not c_node.value

def is_c_true(c_node):
    return isinstance(c_node, c.Const) and c_node.value

def is_tmp_expr(obj: ExprObj):
    c_name = obj.c_node.name if isinstance(obj.c_node, (c.Id, c.VarDecl)) else ""
    return (
        c_name.startswith("tmp") and '_' in c_name
    )

def maybe_deref(obj: CompiledObj, deref: bool, cast, cfunc, ctx):
    if not deref:
        return obj
    if not isinstance(obj, IdxObj):
        return obj
    return idx_get(obj, cast, cfunc, ctx)

def idx_get(idx_obj: IdxObj, cast, cfunc, ctx: CompilerContext):
    obj = idx_get_once(idx_obj, cast, cfunc, ctx)
    while isinstance(obj, IdxObj):
        obj = idx_get_once(obj, cast, cfunc, ctx)
    return obj

def idx_decay_to_ptr_or_val(idx_obj: IdxObj, cast, cfunc, ctx: CompilerContext):
    while isinstance(idx_obj, IdxObj) and not is_ptr_type(idx_obj.idx.inferred_type, ctx):
        idx_obj = idx_get_once(idx_obj, cast, cfunc, ctx)
    return idx_obj

def idx_get_once(idx_obj: IdxObj, cast, cfunc, ctx: CompilerContext):
    try:
        return do_idx_get_once(idx_obj, cast, cfunc, ctx)
    except CompilationError as e:
        raise CompilationError(
            f"Cannot decay '{idx_obj.container.inferred_type.name}[ "
            f"{idx_obj.idx.inferred_type.name} ]' "\
            f"because: {e.error_message}", e.xy_node,
            notes=e.notes
        )

def do_idx_get_once(idx_obj: IdxObj, cast, cfunc, ctx: CompilerContext):
    # reference to a field
    if isinstance(idx_obj.idx, VarObj):
        return ExprObj(
            c_node=idx_obj.c_node,
            xy_node=idx_obj.xy_node,
            inferred_type=idx_obj.idx.type_desc,
            compiled_obj=idx_obj
        )

    # ptr's get simply dereferenced
    if is_ptr_type(idx_obj.idx.inferred_type, ctx):
        idx_to_obj = idx_obj.idx.inferred_type.tags.get("to", None)
        if idx_to_obj is None:
            raise CompilationError("Cannot deref untagged pointer", idx_obj.idx.xy_node)
        return ExprObj(
            c_node=c.UnaryExpr(idx_obj.idx.c_node, op='*', prefix=True),
            xy_node=idx_obj.xy_node,
            inferred_type=idx_to_obj,
            compiled_obj=idx_obj,
        )

    idx_chain = idx_flatten_chain(idx_obj, cast, cfunc, ctx)
    arg_objs = ArgList(idx_chain)
    get_fobj = maybe_find_func_obj("get", arg_objs, cast, cfunc, ctx, idx_obj.xy_node)
    if get_fobj is None:
        shortened_idx = idx_find_widest_get(idx_obj, cast, cfunc, ctx)
        if shortened_idx is None:
            # call find_func_obj just to generate a nice error message
            find_func_obj("get", arg_objs, cast, cfunc, ctx, idx_obj.xy_node)
            raise CompilationError("Should not be reached", idx_obj.xy_node)
        return idx_get(shortened_idx, cast, cfunc, ctx)
    else:
        args_prepared = ArgList([
            maybe_move_to_temp(arg, cast, cfunc, ctx) for arg in arg_objs.args[:-1]
        ])
        #if get_fobj.move_args_to_temps:
        #    args_prepared.args.append(maybe_move_to_temp(arg_objs.args[-1], cast, cfunc, ctx))
        #else:
        #    args_prepared.args.append(arg_objs.args[-1])
        args_prepared.args.append(arg_objs.args[-1])
        return do_compile_fcall(
            idx_obj.xy_node,
            get_fobj,
            arg_exprs=args_prepared,
            cast=cast, cfunc=cfunc, ctx=ctx
        )

def idx_set(idx_obj: IdxObj, val_obj: CompiledObj, cast, cfunc, ctx: CompilerContext):
    try:
        return do_idx_set(idx_obj, val_obj, cast, cfunc, ctx)
    except CompilationError as e:
        raise CompilationError(
            f"Cannot set '{idx_obj.container.inferred_type.name}"
            f"[{idx_obj.idx.inferred_type.name}]' "\
            f"because: {e.error_message}", e.xy_node,
            notes=e.notes
        )

def do_idx_set(idx_obj: IdxObj, val_obj: CompiledObj, cast, cfunc, ctx: CompilerContext):
    if isinstance(idx_obj.idx, VarObj):
        return ExprObj(
            c_node=c.Expr(idx_obj.c_node, val_obj.c_node, op="="),
            xy_node=idx_obj.xy_node,
            inferred_type=idx_obj.idx.type_desc,
            compiled_obj=idx_obj
        )

    if is_ptr_type(idx_obj.idx.inferred_type, ctx):
        return ExprObj(
            c_node=c.Expr(
                c.UnaryExpr(idx_obj.idx.c_node, op='*', prefix=True),
                val_obj.c_node,
                op="="
            ),
            xy_node=idx_obj.xy_node,
            inferred_type=idx_obj.idx.inferred_type.tags["to"]
        )

    idx_chain = idx_flatten_chain(idx_obj, cast, cfunc, ctx)
    idx_chain.append(val_obj)
    arg_objs = ArgList(idx_chain)
    set_fobj = maybe_find_func_obj("set", arg_objs, cast, cfunc, ctx, idx_obj.xy_node)
    if set_fobj is None:
        shortened_idx = idx_find_widest_get(idx_obj, cast, cfunc, ctx)
        if not isinstance(shortened_idx, IdxObj):
            raise CompilationError(f"Can neither set nor decay {fmt_idx_typename(idx_obj)}", idx_obj.xy_node)
        if shortened_idx is None:
            raise CompilationError("Cannot set index", idx_obj.xy_node)
        return idx_set(shortened_idx, val_obj, cast, cfunc, ctx)
    else:
        args_prepared = ArgList([
            maybe_move_to_temp(arg, cast, cfunc, ctx) for arg in arg_objs.args[:-1]
        ])
        if set_fobj.move_args_to_temps:
            args_prepared.args.append(maybe_move_to_temp(arg_objs.args[-1], cast, cfunc, ctx))
        else:
            args_prepared.args.append(arg_objs.args[-1])
        return do_compile_fcall(
            idx_obj.xy_node,
            set_fobj,
            arg_exprs=args_prepared,
            cast=cast, cfunc=cfunc, ctx=ctx
        )

def fmt_idx_typename(idx_obj: IdxObj):
    res = ""
    if idx_obj.container is not None:
        res = idx_obj.container.inferred_type.name
    res += "["
    while getattr(idx_obj, 'idx', None) is not None:
        if res[-1] != "[":
            res += ", "
        res += idx_obj.idx.inferred_type.name
        idx_obj = idx_obj.idx
    res += "]"
    return res

def idx_flatten_chain(idx_obj: IdxObj, cast, cfunc, ctx):
    if is_ptr_type(idx_obj.idx.inferred_type, ctx):
        return [idx_obj]
    res = [idx_obj.idx]
    idx_obj = idx_obj.container
    while isinstance(idx_obj, IdxObj) and not is_ptr_type(idx_obj.idx.inferred_type, ctx):
        res.append(idx_obj.idx)
        idx_obj = idx_obj.container
    if isinstance(idx_obj, IdxObj) and is_ptr_type(idx_obj.idx.inferred_type, ctx):
        res.append(idx_obj)
    if not isinstance(idx_obj, IdxObj) and idx_obj is not global_memory and idx_obj is not param_container:
        res.append(idx_obj)
    return res[::-1]

def idx_iter(idx_obj: IdxObj):
    while (idx_obj, IdxObj):
        yield idx_obj
        idx_obj = idx_obj.container

def idx_find_widest_get(idx_obj: IdxObj, cast, cfunc, ctx: CompilerContext):
    # XXX This entire function is hot garbage
    chain = idx_flatten_chain(idx_obj, cast, cfunc, ctx)
    prev_chain = []
    for i, chain_idx in zip(range(len(chain)-1), idx_iter(idx_obj)):
        arg_objs = ArgList(chain[:len(chain)-i])
        if isinstance(arg_objs.args[-1], VarObj):
            res = ExprObj(
                c_node=chain_idx.c_node,
                xy_node=chain_idx.xy_node,
                inferred_type=arg_objs.args[-1].type_desc,
                compiled_obj=chain_idx
            )
        else:
            get_fobj = maybe_find_func_obj("get", arg_objs, cast, cfunc, ctx, idx_obj.xy_node)
            if get_fobj is None:
                prev_chain.append(chain_idx)
                continue
            res = idx_get(chain_idx, cast, cfunc, ctx)
        for j, prev_idx in zip(range(i, 0, -1), prev_chain[::-1]):
            res = IdxObj(
                xy_node=idx_obj.xy_node,
                container=res,
                idx=chain[len(chain)-j],
                inferred_type=prev_idx.inferred_type
            )
            #res = idx_setup(res, cast, cfunc, ctx)
        return res
    return None

def idx_setup(idx_obj: IdxObj, cast, cfunc, ctx: CompilerContext):
    if idx_obj.inferred_type is not None:
        return idx_obj
    if isinstance(idx_obj.idx.inferred_type, FuncTypeObj):
        # calling a callback is easy to know the return type
        idx_obj.inferred_type = idx_obj.idx.inferred_type.func_obj.rtype_obj
    else:
        # Don't decay container if it is already an idx obj allowing for long idx chians
        if not isinstance(idx_obj.container, IdxObj):
            idx_obj.container = maybe_move_to_temp(idx_obj.container, cast, cfunc, ctx)
        idx_obj.idx = maybe_move_to_temp(idx_obj.idx, cast, cfunc, ctx)

        tmp_names = ctx.tmp_names
        ctx.tmp_names = TmpNames()
        deidx_obj = idx_get(idx_obj, c.Ast(), c.Block(), ctx)
        idx_obj.inferred_type = deidx_obj.inferred_type
        ctx.tmp_names = tmp_names

    return idx_obj

def field_set(obj: CompiledObj, field: VarObj, val: CompiledObj, cast, cfunc, ctx: CompilerContext):
    if isinstance(obj, VarObj):
        obj = ExprObj(
            xy_node=obj.xy_node,
            c_node=c.Id(obj.c_node.name),
            inferred_type=obj.type_desc,
        )

    if isinstance(obj, IdxObj):
        # TODO implement chaining
        obj = idx_get(obj, cast, cfunc, ctx)

    if not field.is_pseudo:
        val_type = val.inferred_type
        is_arr_assign = isinstance(val_type, ArrTypeObj)
        if is_arr_assign:
            tmp_obj = ctx.create_tmp_var(val_type)
            tmp_obj.c_node.value = val.c_node
            cfunc.body.append(tmp_obj.c_node)
            cast.includes.append(c.Include("string.h"))
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
        idx_obj = IdxObj(
            container=obj,
            idx=field.default_value_obj,
            xy_node=val.xy_node,
        )
        return idx_set(idx_obj, val, cast, cfunc, ctx)

def field_get(obj: CompiledObj, field_obj: VarObj, cast, cfunc, ctx: CompilerContext):
    if field_obj.xy_node.is_pseudo:
        idx_obj = IdxObj(
            container=obj,
            idx=field_obj.default_value_obj,
            xy_node=obj.xy_node,
            compiled_obj=field_obj,
        )
        return idx_setup(idx_obj, cast, cfunc, ctx)

    # TODO REMOVE THAT, Only refs should have a c_node
    obj_c_node = obj.c_node
    if isinstance(obj, IdxObj):
        # TODO how to we chain fields if obj doesn't decay to a reference
        obj_c_node = idx_get(obj, cast, cfunc, ctx).c_node
    res = c_deref(obj_c_node, field=c.Id(field_obj.c_node.name))
    return IdxObj(
        container=obj,
        idx=field_obj,
        xy_node=obj.xy_node,
        compiled_obj=field_obj,
        c_node=res,
        inferred_type=field_obj.type_desc
    )

def is_ptr_type(type_obj, ctx):
    if isinstance(type_obj, TypeExprObj):
        type_obj = type_obj.type_obj
    return type_obj is ctx.ptr_obj or type_obj.base_type_obj is ctx.ptr_obj

def is_global_type(type_obj, ctx):
    if isinstance(type_obj, TypeExprObj):
        type_obj = type_obj.type_obj
    return type_obj is ctx.global_obj or type_obj.base_type_obj is ctx.global_obj

def ptr_type_to(type_obj, ctx):
    ptr_type = copy(ctx.ptr_obj)
    ptr_type.base_type_obj = ctx.ptr_obj
    ptr_type.tags = {}
    ptr_type.tags["to"] = type_obj
    return ptr_type

def tag_get(expr, obj, tag_label, ctx, default_value_node: xy.Node = None):
    if isinstance(obj.compiled_obj, (TypeObj, TypeExprObj)):
        obj = obj.compiled_obj
    else:
        obj = obj.inferred_type


    if tag_label not in obj.tags:
        if default_value_node is not None:
            return ctx.eval(default_value_node)
        available_tags = "Available Tags:" + "    \n".join(obj.tags.keys())
        if len(obj.tags) == 0:
            available_tags = "Tag list is empty"
        raise CompilationError(
            f"No tag '{tag_label}'. {available_tags}", expr,
        )
    tag_obj = obj.tags[tag_label]
    return tag_obj

def compile_struct_literal(expr: xy.StructLiteral, cast, cfunc, ctx: CompilerContext):
    if expr.name is None:
        raise CompilationError("Anonymous struct literals are not supported", expr)

    type_obj = ctx.eval(expr.name)
    var_obj = None
    if not isinstance(type_obj, (TypeObj, TypeExprObj)):
        var_obj = compile_expr(expr.name, cast, cfunc, ctx)
        type_obj = var_obj.inferred_type

    if not is_obj_visible(type_obj, ctx):
        raise CompilationError(f"Struct '{type_obj.name}' is not visible", expr.name)

    tmp_obj = None
    if var_obj is not None and not isinstance(var_obj.compiled_obj, (TypeObj, TypeExprObj)):
        tmp_obj = ctx.create_tmp_var(type_obj, xy_node=expr)
        tmp_obj.c_node.value = c.Id(var_obj.c_node.name) if isinstance(var_obj, VarObj) else var_obj.c_node
        cfunc.body.append(tmp_obj.c_node)

    return do_compile_struct_literal(expr, type_obj, tmp_obj, cast, cfunc, ctx)

def do_compile_struct_literal(expr, type_obj, tmp_obj, cast, cfunc, ctx: CompilerContext):
    fully_compile_type(type_obj, cast, None, ctx)

    expr_args = expr.args

    # map positional and named fields
    name_to_pos = {}
    num_real_fields = 0
    for fname, fobj in type_obj.fields.items():
        if not fobj.xy_node.is_pseudo:
            name_to_pos[fname] = num_real_fields
            num_real_fields += 1
    field_objs = list(type_obj.fields.values())

    # loop once in order to see if there are any non-trivial args and
    # do early error checking
    already_set_fields = set()
    any_named = False
    any_init_funcs = False
    first_non_trivial_idx = len(expr_args)
    for i, arg in enumerate(expr_args):
        is_init_func = isinstance(arg, xy.FuncCall) and arg.inject_context
        if any_init_funcs and not is_init_func:
            raise CompilationError("Mixing init funcs and named or positional arguments is NYI", arg)
        elif is_init_func:
            field_obj = None
            any_init_funcs = True
        elif isinstance(arg, xy.BinExpr) and arg.op in {"=", "=<"}:
            # named field
            any_named = True
            name = None
            if isinstance(arg.arg1, xy.Id):
                # just for error handling
                name = arg.arg1.name
                if name not in type_obj.fields:
                    raise CompilationError(f"No field named '{name}'", arg.arg1)
                if name in already_set_fields:
                    raise CompilationError(f"Field {name} already set", arg.arg1)
                already_set_fields.add(name)
            field_obj = type_obj.fields.get(name, None)
        else:
            # positional field
            if any_named:
                raise CompilationError("Cannot mix named and positional arguments", arg)
            if i >= len(field_objs):
                raise CompilationError(
                    f"Too many positional value in struct literal. Provided '{len(expr_args)}' but type has only '{len(field_objs)}' fields",
                    arg
                )
            already_set_fields.add(field_objs[i].xy_node.name)
            field_obj = field_objs[i]

        if field_obj is not None and field_obj.type_desc is recursive_pseudo_field_type_obj:
            raise CompilationError(f"Cannot set value for pseudo field `{field_objs[i].xy_node.name}`. Pseudo fields cannot initialize other pseudo fields.", expr)

        if (field_obj is None or field_obj.xy_node.is_pseudo):
            first_non_trivial_idx = min(first_non_trivial_idx, i)

    # iterate a second time to compute values
    pos_objs = [None] * num_real_fields
    expr_objs = []
    init_func_calls = []
    for i, arg in enumerate(expr_args):
        if isinstance(arg, xy.FuncCall) and arg.inject_context:
            init_func_calls.append(arg)
        elif isinstance(arg, xy.BinExpr) and arg.op in {"=", "=<"}:
            # named field
            name = getattr(arg.arg1, 'name', None)
            val_obj = compile_expr(arg.arg2, cast, cfunc, ctx)
            if arg.op == "=<":
                val_obj = move_out(val_obj, cast, cfunc, ctx)
            expr_objs.append((arg.arg1, val_obj))
            field_obj = type_obj.fields.get(name, None)
            field_i = name_to_pos.get(name, -1)
        else:
            val_obj = compile_expr(arg, cast, cfunc, ctx)
            expr_objs.append((xy.Id(field_objs[i].xy_node.name, src=arg.src, coords=arg.coords), val_obj))
            field_obj = field_objs[i]
            field_i = i

        if field_obj is not None and not field_obj.xy_node.is_pseudo:
            check_type_compatibility(arg, field_obj, val_obj, ctx)

        if i < first_non_trivial_idx:
            pos_objs[field_i] = val_obj

    # create tmp if needed
    injected_tmp = False
    if tmp_obj is None and (first_non_trivial_idx < len(expr_args) or any_init_funcs):
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

    c_args = copy(type_obj.init_value.args) if not type_obj.is_init_value_zeros else []
    for i in range(len(c_args), len(pos_objs)):
        c_args.append(field_objs[i].type_desc.init_value)
    if tmp_obj is None or injected_tmp:
        for i, obj in enumerate(pos_objs):
            if obj is not None:
                c_args[i] = obj.c_node

    if injected_tmp:
        expr_objs = expr_objs[first_non_trivial_idx:]

        if len(c_args) > 0:
            tmp_obj.c_node.value = c.CompoundLiteral(
                name=type_obj.c_name,
                args=c_args,
            )
        else:
            tmp_obj.c_node.value = type_obj.init_value

    if tmp_obj is None:
        # creating a new struct
        if len(pos_objs) != 0:
            ctypename = type_obj.c_name
            res = c.CompoundLiteral(
                name=ctypename,
                args=c_args,
            )
        else:
            res = type_obj.init_value
    else:
        # creating a new struct from an existing one
        tmp_expr_obj = tmp_obj
        if isinstance(tmp_expr_obj, VarObj):
            res = c.Id(tmp_obj.c_node.name)
            tmp_expr_obj = ExprObj(
                xy_node=tmp_expr_obj.xy_node,
                c_node=res,
                inferred_type=type_obj
            )
        else:
            res = tmp_obj.c_node

        for expr, fval_obj in expr_objs:
            if isinstance(expr, xy.Id):
                obj = field_set(tmp_obj, type_obj.fields[expr.name], fval_obj, cast, cfunc, ctx)
            else:
                f_obj = do_compile_field_get_rec(tmp_expr_obj, expr, cast, cfunc, ctx)
                obj = idx_set(f_obj, fval_obj, cast, cfunc, ctx)
            if not isinstance(obj.c_node, c.Id):
                cfunc.body.append(obj.c_node)

        ctx.push_ctx_obj(tmp_expr_obj)
        for init_fcall in init_func_calls:
            obj = compile_fcall(init_fcall, cast, cfunc, ctx)
            cfunc.body.append(obj.c_node)
        ctx.pop_ctx_obj()

    # optimize the resulting expression
    if type_obj.builtin and isinstance(res, c.CompoundLiteral) and len(res.args) == 1:
        val = res.args[0]
        if isinstance(val, c.Cast) and val.to == res.name:
            res = val
        else:
            res = c.Cast(val, res.name)

    return ExprObj(
        xy_node=expr,
        c_node=res,
        inferred_type=type_obj,
        compiled_obj=tmp_obj,
    )

def should_pass_by_ref(param: xy.VarDecl, type_obj):
    if isinstance(type_obj, TypeExprObj):
        type_obj = type_obj.type_obj
    return not isinstance(type_obj, ArrTypeObj) and param.mutable

def c_deref(c_node, field=None):
    if isinstance(c_node, c.UnaryExpr) and c_node.op == "*" and c_node.prefix:
        return c.Expr(c_node.arg, field, op='->')
    return c.Expr(c_node, field, op='.')

def c_getref(arg: ExprObj):
    c_node = arg.c_node
    if isinstance(arg.inferred_type, ArrTypeObj):
        return c_node
    if isinstance(c_node, c.UnaryExpr) and c_node.op == "*" and c_node.prefix:
        return c_node.arg
    return c.UnaryExpr(c_node, op='&', prefix=True)

def do_infer_type(expr, cast, ctx):
    if isinstance(expr, xy.StructLiteral):
        return ctx.get_compiled_type(expr.name)
    try:
        throw_away = c.Func("throw_away")
        return compile_expr(expr, cast, throw_away, ctx).inferred_type
    except CompilationError as e:
        raise CompilationError(
            f"Cannot infer type because: {e.error_message}", e.xy_node,
            notes=e.notes
        )

def compile_strlit(expr, cast, cfunc, ctx: CompilerContext):
    parts = []
    for p in expr.parts:
        to_append = p
        if isinstance(p, xy.ExternalCommand):
            if len(p.command) != 2 and p.command[0] != "cat":
                raise CompilationError("Only cat'ing a single file is currently supported", p)
            with open(os.path.join(ctx.module_path, p.command[1])) as f:
                to_append = xy.Const(escape_str(f.read()))
        if is_str_const(to_append) and len(parts) > 0 and is_str_const(parts[-1]):
            parts[-1].value += to_append.value
            parts[-1].value_str += to_append.value_str
        else:
            parts.append(to_append)

    if expr.prefix == "inlinec":
        return compile_inlinec(expr, parts, cast, cfunc, ctx)

    if expr.prefix not in ctx.str_prefix_reg:
        raise CompilationError(
            f"No string constructor registered for prefix \"{expr.prefix}\"",
            expr
        )
    func_desc: FuncObj = ctx.str_prefix_reg[expr.prefix]

    interpolation = ("interpolation" in func_desc.tags["xyStr"].kwargs and
                     ct_isTrue(func_desc.tags["xyStr"].kwargs["interpolation"]))
    if not interpolation:
        is_error = len(parts) > 1
        if not is_error and len(parts) == 1:
            is_error = not isinstance(parts[0], xy.Const)
        if is_error:
            raise CompilationError(
                f"Interpolation is not enabled for prefix \"{expr.prefix}\"",
                expr
            )

    if not interpolation:
        str_const, str_len = to_cstr(
            parts[0] if len(parts) else expr,
            parts[0].value if len(parts) else ""
        )
        args = ArgList(
            args=[
                ExprObj(
                    expr, c.Cast(c.Const(f'"{str_const}"'), to="int8_t*"),
                    ctx.ptr_to_byte_obj
                ),
                ExprObj(
                    expr, c.Const(str_len), ctx.size_obj
                )
            ]
        )
        return do_compile_fcall(expr, func_desc, args, cast, cfunc, ctx)
    else:
        builder_tmpvar = ctx.create_tmp_var(func_desc.rtype_obj, f"{expr.prefix}str", xy_node=expr)
        cfunc.body.append(builder_tmpvar.c_node)
        ctx.ns[builder_tmpvar.c_node.name] = builder_tmpvar
        builder_tmpvar_id = ExprObj(
            xy_node=expr,
            c_node=c.Id(builder_tmpvar.c_node.name),
            inferred_type=func_desc.rtype_obj
        )
        full_str, full_str_len = to_cstr(expr, expr.full_str)
        builder_tmpvar.c_node.value = do_compile_fcall(
            expr=expr,
            func_obj=func_desc,
            arg_exprs=ArgList([
                ConstObj(c_node=c.Cast(c.Const(f'"{full_str}"'), to="int8_t*"), value=""),
                ConstObj(c_node=c.Const(full_str_len), value=0)
            ]),
            cast=cast,
            cfunc=cfunc,
            ctx=ctx
        ).c_node
        for part in parts:
            if is_str_const(part):
                part_value, part_value_len = to_cstr(part, part.value)
                append_call = find_and_call(
                    "append",
                    ArgList([
                        builder_tmpvar_id,
                        ExprObj(
                            c_node=c.Cast(c.Const('"' + part_value + '"'), to="int8_t*"),
                            inferred_type=ctx.ptr_to_byte_obj
                        ),
                        ExprObj(c_node=c.Const(part_value_len), inferred_type=ctx.size_obj),
                    ]),
                    cast,
                    cfunc,
                    ctx,
                    xy_node=expr,
                )
                if append_call.c_node is not None: cfunc.body.append(append_call.c_node)
            else:
                assert isinstance(part, xy.Args)
                if part.is_introspective:
                    part_str = part.args[0].src.code[part.args[0].coords[0]:part.args[0].coords[1]] + "="
                    part_str, part_str_len = to_cstr(part, part_str)
                    append_call = find_and_call(
                        "append",
                        ArgList([
                            builder_tmpvar_id,
                            ExprObj(
                                c_node=c.Cast(c.Const('"' + part_str + '"'), to="int8_t*"),
                                inferred_type=ctx.ptr_to_byte_obj
                            ),
                            ExprObj(c_node=c.Const(part_str_len), inferred_type=ctx.size_obj),
                        ]),
                        cast,
                        cfunc,
                        ctx,
                        xy_node=expr,
                    )
                    if append_call.c_node is not None: cfunc.body.append(append_call.c_node)
                gen_fcall = xy.FuncCall(
                    xy.Id("append", src=part.src, coords=part.coords),
                    args=[xy.Id(builder_tmpvar.c_node.name, src=part.src, coords=part.coords)] + part.args,
                    kwargs=part.kwargs,
                    src=part.src,
                    coords=part.coords
                )
                append_call = compile_fcall(gen_fcall, cast, cfunc, ctx)
                if append_call.c_node is not None: cfunc.body.append(append_call.c_node)

        to_obj = func_desc.tags["xyStr"].kwargs.get("to", None)
        if to_obj is not None:
            return find_and_call(
                "to",
                ArgList([
                    builder_tmpvar_id,
                    ExprObj(
                        c_node=c.Id(to_obj.c_node.name),
                        inferred_type=to_obj
                    )
                ]),
                cast,
                cfunc,
                ctx,
                xy_node=expr
            )
        else:
            return builder_tmpvar_id

def compile_unstring(lhs_expr, rhs_expr, cast, cfunc, ctx: CompilerContext):
    assert isinstance(lhs_expr, xy.StrLiteral)
    rhs_obj = compile_expr(rhs_expr, cast, cfunc, ctx)
    rhs_obj = move_to_temp(rhs_obj, cast, cfunc, ctx)
    unstr_ctor: FuncObj = ctx.unstr_prefix_reg[lhs_expr.prefix]
    unstr_obj = do_compile_fcall(lhs_expr, unstr_ctor, ArgList([rhs_obj]), cast, cfunc, ctx)
    unstr_iter = ctx.create_tmp_var(unstr_obj.inferred_type, "unstr", lhs_expr)
    unstr_iter.c_node.value = unstr_obj.c_node
    cfunc.body.append(unstr_iter.c_node)
    unstr_obj = var_to_expr_obj(lhs_expr, unstr_iter, cast, cfunc, ctx, deref=False)

    for part in lhs_expr.parts:
        assert isinstance(part, xy.Args)
        if not isinstance(part.args[0], xy.VarDecl):
            raise CompilationError("Only var decls must be present in a unstring expression", part)
        decl = part.args[0]
        if decl.value is not None:
            raise CompilationError("Cannot do assignment in unstring expression", decl.value)
        var_obj = compile_vardecl(decl, cast, cfunc, ctx)
        cfunc.body.append(var_obj.c_node)

        val_obj = var_to_expr_obj(decl, var_obj, cast, cfunc, ctx, deref=False)
        arg_list = ArgList([rhs_obj, unstr_obj, val_obj])
        for arg in part.args[1:]:
            arg_list.args.append(compile_expr(arg, cast, cfunc, ctx))
        for name, arg in part.kwargs.items():
            arg_list.kwargs[name] = compile_expr(arg, cast, cfunc, ctx)
        read_obj = find_and_call("read", arg_list, cast, cfunc, ctx, part)
        cfunc.body.append(read_obj.c_node)

    return rhs_obj

def compile_inlinec(expr, parts, cast, cfunc, ctx):
    inlinec = ""
    for p in parts:
        if is_str_const(p):
            inlinec += p.value.replace("\\{", "{").replace('\\"', '"')
        else:
            assert isinstance(p, xy.Args)
            assert len(p.args) == 1
            assert len(p.kwargs) == 0
            obj = compile_expr(p.args[0], cast, cfunc, ctx, deref=True)
            if not isinstance(obj.c_node, c.Id):
                raise CompilationError("NYI. Only variabled can be used for inlinec interpolation", p)
            inlinec += obj.c_node.name

    res = c.InlineCode(inlinec)
    return ExprObj(
        c_node=res,
        xy_node=expr,
        inferred_type=c_symbol_type
    )

def escape_str(s: str):
    return s.translate(str.maketrans({"\n": "\\n", '"': '\\"', '\\': '\\\\'}))

def is_str_const(node: xy.Node) -> bool:
    return isinstance(node, xy.Const) and isinstance(node.value, str)

def get_c_int_val(c_node) -> int:
    if isinstance(c_node, c.Const) and isinstance(c_node.value, int):
        return c_node.value
    return None

def ct_isTrue(obj: CompiledObj):
    if isinstance(obj, ConstObj) and isinstance(obj.value, bool):
        return obj.value
    raise CompilationError(
        "Should be true or false",
        obj.xy_node
    )

def to_cstr(xy_node, s: str):
    c_esc_seq = {'a', 'b', 'f', 'n', 'r', 't', 'v', '\\', '"'}
    c_esc_codes = {ord(c) for c in c_esc_seq}

    def allowed_c_char(c):
        return c >= 32 and c <= 126

    def is_num(c):
        return c >= ord('0') and c <= ord('9')

    res = []
    res_len = 0
    bstr = s.encode("utf-8")
    i = 0
    while i < len(bstr):
        if bstr[i] == ord('\\'):
            if i+1 >= len(bstr):
                raise CompilationError("Invalid escape sequence in string", xy_node)
            if bstr[i+1] in c_esc_codes:
                res.extend((chr(bstr[i]), chr(bstr[i+1])))
                res_len += 1
                i += 2
            elif bstr[i+1] == ord('{'):
                res.append(chr(bstr[i+1]))
                res_len += 1
                i += 2
            elif is_num(bstr[i+1]):
                if not (i+3 < len(bstr) and is_num(bstr[i+1]) and is_num(bstr[i+2])):
                    raise CompilationError("Invalid escape sequence. Required exactly 3 numbers needed in escape", xy_node)
                res.extend((chr(bstr[i]), chr(bstr[i+1]), chr(bstr[i+2]), chr(bstr[i+3])))
                res_len += 1
                i += 4
            elif bstr[i+1] == ord("x"):
                cp = cstr_hexadecimal(xy_node, bstr, i+2, 2)
                i += 4
                res.append(byte_to_cstr(cp))
                res_len += 1
            elif bstr[i+1] == ord("u"):
                cp = cstr_hexadecimal(xy_node, bstr, i+2, 4)
                i += 6
                res_len += codepoint_to_bytes(cp, res)
            elif bstr[i+1] == ord("U"):
                if i+2 < len(bstr) and bstr[i+2] == ord("+"):
                    cp, n_parsed = cstr_varlen_hexadecimal(xy_node, bstr, i+3, 6)
                    i += 3 + n_parsed
                    res_len += codepoint_to_bytes(cp, res)
                else:
                    cp = cstr_hexadecimal(xy_node, bstr, i+2, 8)
                    i += 10
                    res_len += codepoint_to_bytes(cp, res)
            elif bstr[i+1] == ord("\n"):
                res.append("\\\n")
                i += 2
                res_len += 2
            else:
                raise CompilationError(f"Invalid escape sequence in string '{chr(bstr[i+1])}'", xy_node)
        else:
            if allowed_c_char(bstr[i]):
                res.append(chr(bstr[i]))
            else:
                res.append(byte_to_cstr(bstr[i]))
            res_len += 1
            i += 1
    return "".join(res), res_len

def cstr_hexadecimal(expr, bstr, i, required):
    if (i + required - 1) >= len(bstr):
        raise CompilationError(f"Invalid escape sequence. Required exactly {required} symbols in the range 0-F", expr)
    hd_str = ""
    for j in range(required):
        hd_str = hd_str + chr(bstr[i+j])
    return int(hd_str, base=16)

def cstr_varlen_hexadecimal(expr, bstr, i, max_digits):
    if i >= len(bstr):
        raise CompilationError(f"Atleast one hex digit needed to specify a code point")
    hd_str = ""
    for j in range(max_digits):
        if i + j >= len(bstr):
            break
        bt = bstr[i+j]
        valid_hex = (
            bt >= ord('0') and bt <= ord('9') or
            bt >= ord('A') and bt <= ord('F') or
            bt >= ord('a') and bt <= ord('f')
        )
        if not valid_hex:
            break
        hd_str = hd_str + chr(bstr[i+j])
    return int(hd_str, base=16), j


def codepoint_to_bytes(cp, res):
    res_len = 0
    for byte in chr(cp).encode("utf-8"):
        res.append(byte_to_cstr(byte))
        res_len += 1
    return res_len

def byte_to_cstr(byte):
    return "\\" + ("00" + oct(byte)[2:])[-3:]

def compile_fselect(expr: xy.FuncSelect, cast, cfunc, ctx: CompilerContext):
    arg_inferred_types = ArgList(
        args=[ctx.eval_to_type(arg) for arg in expr.args],
        kwargs={k: ctx.eval_to_type(t) for k, t in expr.kwargs},
    )

    if not expr.multiple:
        if expr.name is not None:
            fspace = ctx.eval_to_fspace(expr.name)
            if fspace is None:
                call_sig = fcall_sig(ctx.eval_to_id(expr.name), arg_inferred_types, expr.inject_args)
                raise CompilationError(f"Cannot find function {call_sig}", expr.name)
            if isinstance(fspace, ExtSpace):
                raise CompilationError("No suitable callbacks found", expr)

            if ctx.compiling_header:
                for fobj in fspace._funcs:
                    compile_func_prototype(fobj, cast, ctx)

            func_obj: FuncObj = fspace.find(expr, arg_inferred_types, ctx, partial_matches=False)
        else:
            func_obj = None
            candidates: list[FuncObj] = fselect_unnamed(expr, arg_inferred_types, ctx, partial_matches=False)
            required_tags = ctx.eval_tags(expr.tags, cast=cast)
            for cand in candidates:
                if has_required_tags(cand.tags, required_tags):
                    func_obj = cand
                    break
            if func_obj is None:
                func_obj = candidates[0]

        ensure_func_decl(func_obj, cast, cfunc, ctx)

        params = func_obj.param_objs
        c_typename = create_fptr_type(params, func_obj.rtype_obj, cast, ctx)

        return ExprObj(
            xy_node=expr,
            c_node=c.Id(func_obj.c_name),
            inferred_type=FuncTypeObj(c_typename=c_typename, xy_node=expr, func_obj=func_obj),
            compiled_obj=func_obj
        )
    else:
        # select multiple
        assert expr.name is None
        candidates: list[FuncObj] = fselect_unnamed(expr, arg_inferred_types, ctx, partial_matches=False)

        res_objs = []
        required_tags = ctx.eval_tags(expr.tags, cast=cast)
        for cand in candidates:
            if has_required_tags(cand.tags, required_tags):
                ensure_func_decl(cand, cast, cfunc, ctx)

                params = cand.param_objs
                c_typename = create_fptr_type(params, cand.rtype_obj, cast, ctx)

                res_objs.append(FuncTypeObj(c_typename=c_typename, xy_node=expr, func_obj=cand))

        return ExprObj(
            xy_node=expr,
            c_node=c.Id("REPORT_IF_YOU_SEE_ME"),
            compiled_obj=res_objs,
            inferred_type=fselection_type_obj,
        )

def has_required_tags(base_tags, required_tags):
    for tag_name, tag_value in required_tags.items():
        if tag_value != base_tags.get(tag_name, None):
            return False

    return True

def fselect_unnamed(expr, arg_types: ArgList, ctx: CompilerContext, partial_matches=True):
    res = []
    namespaces_vals = [ns.values() for ns in ctx.func_namespaces[::-1]]
    for obj in itertools.chain(*namespaces_vals):
        if isinstance(obj, FuncSpace):
            res.extend(obj.findAll(expr, arg_types, ctx, partial_matches))
    return res

def compile_fcall(expr: xy.FuncCall, cast, cfunc, ctx: CompilerContext):
    arg_exprs = ArgList()
    if expr.inject_context and len(ctx.ctx_obj_stack) > 0:
        arg_exprs.args.append(ctx.ctx_obj_stack[-1])
    expr_to_move_idx = None
    for i in range(len(expr.args)):

        dummy_func = c.Func("dummy")
        ctx.push_ns()
        obj = compile_expr(expr.args[i], cast, dummy_func, ctx, deref=False)
        ns = ctx.ns
        if isinstance(obj, ExprObj):
            obj.tmp_var_names.update(ns.keys())
        ctx.pop_ns()
        ctx.ns.update(ns)

        if isinstance(obj, IdxObj):
            obj = idx_decay_to_ptr_or_val(obj, cast, dummy_func, ctx)
        if len(dummy_func.body):
            if expr_to_move_idx is not None:
                arg_exprs[expr_to_move_idx] = maybe_move_to_temp(
                    arg_exprs[expr_to_move_idx], cast, cfunc, ctx
                )
                expr_to_move_idx = None
            obj = maybe_move_to_temp(obj, cast, dummy_func, ctx)
            obj.redact_cfunc = cfunc
            obj.first_cnode_idx = len(cfunc.body)
            cfunc.body.extend(dummy_func.body)
            obj.num_cnodes = len(cfunc.body) - obj.first_cnode_idx

        if cfunc is not None and not is_simple_cexpr(obj.c_node):
            if expr_to_move_idx is not None:
                tmp_obj = move_to_temp(arg_exprs[expr_to_move_idx], cast, cfunc, ctx)
                arg_exprs[expr_to_move_idx] = tmp_obj

            if type_needs_dtor(obj.inferred_type):
                # immediatelly move if a dtor is required
                obj = maybe_move_to_temp(obj, cast, cfunc, ctx)
                expr_to_move_idx = None
            else:
                # defer move to tmp for as long as possible
                expr_to_move_idx = i
        elif type_needs_dtor(obj.inferred_type) and isinstance(obj.c_node, c.CompoundLiteral):
            if expr_to_move_idx is not None:
                tmp_obj = move_to_temp(arg_exprs[expr_to_move_idx], cast, cfunc, ctx)
                arg_exprs[expr_to_move_idx] = tmp_obj

            # immediatelly move if a dtor is required
            obj = move_to_temp(obj, cast, cfunc, ctx)
            expr_to_move_idx = None

        arg_exprs.args.append(obj)
    if len(expr.kwargs) > 0 and expr_to_move_idx is not None:
        arg_exprs[expr_to_move_idx] = maybe_move_to_temp(
            arg_exprs[expr_to_move_idx], cast, cfunc, ctx
        )
        expr_to_move_idx = None
    for pname, pexpr in expr.kwargs.items():
        obj = compile_expr_for_arg(pexpr, cast, cfunc, ctx)
        arg_exprs.kwargs[pname] = obj

    arg_inferred_types = ArgList(
        args=[arg.inferred_type for arg in arg_exprs.args],
        kwargs={key: arg.inferred_type for key, arg in arg_exprs.kwargs.items()}
    )
    # select the corrent function
    fspace = ctx.eval(expr.name, is_func=True)
    if fspace is None:
        call_sig = fcall_sig(ctx.eval_to_id(expr.name), arg_inferred_types, expr.inject_args)
        raise CompilationError(f"Cannot find function {call_sig}", expr.name)

    if isinstance(fspace, ExtSymbolObj):
        fspace = ExtSpace(fspace.symbol)

    if isinstance(fspace, IdxObj):
        fspace = idx_get(fspace, cast, cfunc, ctx)

    if not isinstance(fspace, ExtSpace):
        for arg in arg_exprs.args:
            assert_has_type(arg)
        for arg in arg_exprs.kwargs.values():
            assert_has_type(arg)

    caller_ctx = ctx
    if isinstance(fspace, (FuncSpace, ExtSpace)):
        if ctx.compiling_header:
            for fobj in fspace._funcs:
                compile_func_prototype(fobj, cast, ctx)
        if isinstance(expr.name, xy.CallerContextExpr):
            # if we have a func space from a parent  space then we do the
            # func selection as if we are in that context
            caller_ctx = ctx.get_caller_context()
        func_obj = fspace.find(expr, arg_inferred_types, caller_ctx, partial_matches=expr.inject_args)
    else:
        if isinstance(fspace, (VarObj, ExprObj)):
            inferred_type = fspace.inferred_type if isinstance(fspace, ExprObj) else fspace.type_desc
            if not isinstance(inferred_type, FuncTypeObj):
                raise CompilationError("Not a callback", expr)
            func_obj = copy(fspace.inferred_type.func_obj)
            func_obj.c_node = fspace.c_node
        else:
            raise CompilationError("Not a function or callback", expr)


    if expr_to_move_idx is not None and func_obj.move_args_to_temps and not is_builtin_func(func_obj, "to"):
        # the not is_builtin_func(func_obj, "to") is simply an optimization to produce slighly better code
        arg_exprs[expr_to_move_idx] = maybe_move_to_temp(
            arg_exprs[expr_to_move_idx], cast, cfunc, ctx
        )
        expr_to_move_idx = None
    if expr_to_move_idx is not None and isinstance(arg_exprs[expr_to_move_idx], IdxObj):
        arg_exprs[expr_to_move_idx] = idx_get(
            arg_exprs[expr_to_move_idx], cast, cfunc, ctx
        )
        expr_to_move_idx = None

    return do_compile_fcall(expr, func_obj, arg_exprs, cast, cfunc, caller_ctx)

def compile_expr_for_arg(arg: xy.Node, cast, cfunc, ctx: CompilerContext):
    expr_obj = compile_expr(arg, cast, cfunc, ctx)
    return maybe_move_to_temp(expr_obj, cast, cfunc, ctx)

def maybe_move_to_temp(expr_obj, cast, cfunc, ctx):
    if isinstance(expr_obj, (ExprObj, IdxObj)) and cfunc is not None and not is_simple_cexpr(expr_obj.c_node):
        return move_to_temp(expr_obj, cast, cfunc, ctx)
    else:
        return expr_obj

def move_to_temp(expr_obj, cast, cfunc, ctx):
    original_expr_obj = expr_obj
    if isinstance(expr_obj, IdxObj):
        expr_obj = idx_decay_to_ptr_or_val(expr_obj, cast, cfunc, ctx)
        if isinstance(expr_obj, IdxObj):
            # decay to ptr
            get_obj = idx_get(expr_obj, cast, cfunc, ctx)
            if is_simple_cexpr(get_obj.c_node):
                return get_obj
            tmp_obj = ctx.create_tmp_var(expr_obj.idx.inferred_type, "ref", expr_obj.xy_node)
            tmp_obj.c_node.value = get_obj.c_node.arg
            cfunc.body.append(tmp_obj.c_node)
            get_obj.c_node = c.UnaryExpr(arg=c.Id(tmp_obj.c_node.name), op="*", prefix=True)
            get_obj.compiled_obj = expr_obj
            return get_obj

    res = copy_to_temp(expr_obj, cast, cfunc, ctx)
    # XXX we need a way to preserve the history of that object even if it is the result of moving to a temp of another one
    res.compiled_obj = original_expr_obj if original_expr_obj.compiled_obj is None else original_expr_obj.compiled_obj
    return res

def copy_to_temp(expr_obj, cast, cfunc, ctx):
    if isinstance(expr_obj, IdxObj):
        # TODO not tested
        get_obj = idx_get(expr_obj, cast, cfunc, ctx)
        tmp_obj = ctx.create_tmp_var(expr_obj.inferred_type, "ref", expr_obj.xy_node)
        tmp_obj.c_node.value = get_obj.c_node
        cfunc.body.append(tmp_obj.c_node)
        get_obj.c_node = c.Id(tmp_obj.c_node.name)
        return get_obj

    tmp_obj = ctx.create_tmp_var(expr_obj.inferred_type, name_hint="arg", xy_node=expr_obj.xy_node)
    if isinstance(expr_obj.inferred_type, ArrTypeObj):
        tmp_obj.c_node.value = expand_array_to_init_list(expr_obj)
    else:
        tmp_obj.c_node.value = expr_obj.c_node
    if expr_obj.num_cnodes > 0:
        assert len(cfunc.body) == expr_obj.first_cnode_idx + expr_obj.num_cnodes
    cfunc.body.append(tmp_obj.c_node)
    return ExprObj(
        xy_node=expr_obj.xy_node,
        c_node=c.Id(tmp_obj.c_node.name),
        inferred_type=expr_obj.inferred_type,
        tags=expr_obj.tags,
        compiled_obj=tmp_obj,
        first_cnode_idx=expr_obj.first_cnode_idx if expr_obj.num_cnodes > 0 else len(cfunc.body)-1,
        num_cnodes=expr_obj.num_cnodes + 1 if expr_obj.num_cnodes > 0 else 1,
        tmp_var_names={tmp_obj.c_node.name},
        from_lazy_ctx=expr_obj.from_lazy_ctx,
    )

def is_simple_cexpr(expr):
    if isinstance(expr, (c.Id, c.Const, c.InlineCode)):
        return True
    if isinstance(expr, c.Expr):
        return is_simple_cexpr(expr.arg1) and is_simple_cexpr(expr.arg2)
    if isinstance(expr, c.UnaryExpr):
        return is_simple_cexpr(expr.arg)
    if isinstance(expr, c.CompoundLiteral):
        return all(is_simple_cexpr(e) for e in expr.args)
    if isinstance(expr, c.Index):
        return is_simple_cexpr(expr.expr) and is_simple_cexpr(expr.index)
    if isinstance(expr, c.Cast):
       return is_simple_cexpr(expr.what)
    return False


def find_and_call(name: str, arg_objs, cast, cfunc, ctx, xy_node):
    fobj = find_func_obj(name, arg_objs, cast, cfunc, ctx, xy_node)

    return do_compile_fcall(
        xy_node,
        fobj,
        arg_exprs=arg_objs,
        cast=cast, cfunc=cfunc, ctx=ctx
    )

def maybe_find_func_obj(name: str, arg_objs, cast, cfunc, ctx, xy_node):
    fspace = ctx.eval_to_fspace(
        xy.Id(name, src=xy_node.src, coords=xy_node.coords),
    )
    if fspace is None:
        return None

    return fspace.find(
        xy.FuncCall(xy.Id(name), src=xy_node.src, coords=xy_node.coords),
        ArgList([obj.inferred_type for obj in arg_objs]),
        ctx,
        return_no_matches=True,
    )

def find_func_obj(name: str, arg_objs, cast, cfunc, ctx, xy_node):
    return ctx.eval_to_fspace(
        xy.Id(name, src=xy_node.src, coords=xy_node.coords),
        msg=f"Cannot find function {name}",
    ).find(
        xy.FuncCall(xy.Id(name), src=xy_node.src, coords=xy_node.coords),
        ArgList([obj.inferred_type for obj in arg_objs]),
        ctx
    )

def do_compile_fcall(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    if is_builtin_func(func_obj, "get"):
        if is_global_type(arg_exprs[0].inferred_type, ctx):
            return compile_global_get(expr, func_obj, arg_exprs, cast, cfunc, ctx)
        else:
            return compile_builtin_get(expr, func_obj, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "set"):
        if len(arg_exprs) == 2 and is_global_type(arg_exprs[0].inferred_type, ctx):
            return compile_global_set(expr, func_obj, arg_exprs, cast, cfunc, ctx)
        assert len(arg_exprs) == 3
        get_obj = compile_builtin_get(
            expr, func_obj, ArgList(args=arg_exprs.args[:2]), cast, cfunc, ctx
        )
        return ExprObj(
            xy_node=expr,
            c_node=c.Expr(
                get_obj.c_node,
                arg_exprs[2].c_node,
                op="="
            ),
            inferred_type=ctx.void_obj,
        )
    elif is_builtin_func(func_obj, "typeEqs"):
        return typeEqs(expr, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "to"):
        what = arg_exprs[0].c_node
        to = arg_exprs[1].c_node.name
        if isinstance(what, c.Cast) and what.to == to:
            res = what  # eliminate double cast to the same time in rare cases
        else:
            res = c.Cast(what=what, to=to)
        return ExprObj(
            xy_node=expr,
            c_node=res,
            inferred_type=arg_exprs[1].inferred_type
        )
    elif is_builtin_func(func_obj, "iter"):
        return IdxObj(
            container=arg_exprs[0],
            idx=ExprObj(
                xy_node=expr,
                c_node=c.Const(0),
                inferred_type=func_obj.rtype_obj
            ),
            inferred_type=arg_exprs[0].inferred_type.base_type_obj,
            xy_node=expr,
        )
    elif is_builtin_func(func_obj, "valid"):
        return ExprObj(
            xy_node=expr,
            c_node=c.Expr(
                arg1=arg_exprs[1].c_node,
                arg2=c.Const(arg_exprs[0].inferred_type.dims[0]),
                op="<"
            ),
            inferred_type=ctx.bool_obj,
        )
    elif is_builtin_func(func_obj, "next"):
        return ExprObj(
            xy_node=expr,
            c_node=c.UnaryExpr(
                arg=arg_exprs[1].c_node,
                op="++",
                prefix=True,
            ),
            inferred_type=ctx.void_obj,
        )
    elif (is_builtin_func(func_obj, "and") or is_builtin_func(func_obj, "or")) and arg_exprs[0].inferred_type is ctx.bool_obj and arg_exprs[1].inferred_type is ctx.bool_obj:
        redact_code(arg_exprs[1], cast, cfunc, ctx)
        dummy_func = c.Func("dummy")
        ctx.push_ns()
        defered_expr = compile_expr(arg_exprs[1].xy_node, cast, dummy_func, ctx, deref=True)
        defered_ns = ctx.ns
        ctx.pop_ns()
        c_op = "&&" if is_builtin_func(func_obj, "and") else "||"
        non_empty_body_nodes = [n for n in dummy_func.body if not isinstance(n, c.Empty)]
        if len(non_empty_body_nodes) == 0:
            cfunc.body.extend(dummy_func.body)  # TODO really?
            res = c.Expr(arg_exprs[0].c_node, defered_expr.c_node, op=c_op)
            return ExprObj(
                xy_node=expr,
                c_node=res,
                inferred_type=func_obj.rtype_obj
            )
        else:
            tmp_obj = ctx.create_tmp_var(ctx.bool_obj, name_hint="shortcircuit", xy_node=expr)
            tmp_obj.c_node.value = arg_exprs[0].c_node
            cfunc.body.append(tmp_obj.c_node)

            res = c.If(c.Id(tmp_obj.c_node.name))
            if c_op == "||":
                res.cond = c.UnaryExpr(res.cond, op="!", prefix=True)

            res.body.extend(dummy_func.body)
            res.body.append(c.Expr(c.Id(tmp_obj.c_node.name), defered_expr.c_node, op="="))
            cfunc.body.append(res)
            call_dtors(defered_ns, cast, res, ctx)
            return ExprObj(
                xy_node=expr,
                c_node=c.Id(tmp_obj.c_node.name),
                inferred_type=func_obj.rtype_obj
            )
    elif is_builtin_func(func_obj, "not"):
        if not arg_exprs[0].inferred_type.name.startswith("Bits"):
            c_res = c.UnaryExpr(arg_exprs[0].c_node, op="!", prefix=True)
        else:
            c_res = c.UnaryExpr(arg_exprs[0].c_node, op="~", prefix=True)
            bit_len = int(arg_exprs[0].inferred_type.name[len("Bits"):])
            if bit_len < 32:
                c_res = c.Cast(c_res, func_obj.rtype_obj.c_name)
        return ExprObj(
            xy_node=expr,
            c_node=c_res,
            inferred_type=func_obj.rtype_obj
        )
    elif is_builtin_func(func_obj, "ashiftr"):
        signed_ctype = arg_exprs[0].inferred_type.c_node.name[1:]
        c_res = c.Cast(arg_exprs[0].c_node, to=signed_ctype)

        # try to remove the & if a constant
        bit_len = int(arg_exprs[0].inferred_type.name[len("Bits"):])
        c_arg2_val = get_c_int_val(arg_exprs[1].c_node)
        if c_arg2_val is None or c_arg2_val < 0 or c_arg2_val >= bit_len:
            c_arg2 = c.Expr(arg_exprs[1].c_node, c.Const(hex(bit_len-1)), op='&')
        else:
            c_arg2 = arg_exprs[1].c_node
        c_res = c.Expr(c_res, c_arg2, op=">>")

        # Always explicitly cast back to the unsigned type in order to avoid
        # the c-compiler mistakingly thinking its a siged type
        c_res = c.Cast(c_res, func_obj.rtype_obj.c_name)

        return ExprObj(
            xy_node=expr,
            c_node=c_res,
            inferred_type=func_obj.rtype_obj
        )
    elif len(arg_exprs) == 2 and (is_builtin_func(func_obj, "min") or is_builtin_func(func_obj, "max")):
        op = '<' if func_obj.xy_node.name.name == "min" else '>'
        return ExprObj(
            xy_node=expr,
            c_node=c.TernaryExpr(
                c.Expr(arg_exprs[0].c_node, arg_exprs[1].c_node, op=op),
                arg_exprs[0].c_node,
                arg_exprs[1].c_node,
            ),
            inferred_type=func_obj.rtype_obj,
        )
    elif is_builtin_func(func_obj, "cmp"):
        if arg_exprs[0].inferred_type is not arg_exprs[1].inferred_type:
            ## nice error message for mixed type comparison
            if ctx.is_int(arg_exprs[0].inferred_type) and not isinstance(arg_exprs[0].c_node, c.Const):
                report_mixed_signed(expr, arg_exprs, ctx)
            if ctx.is_int(arg_exprs[1].inferred_type) and not isinstance(arg_exprs[1].c_node, c.Const):
                report_mixed_signed(expr, arg_exprs, ctx)
        return ExprObj(
            xy_node=expr,
            c_node=c.TernaryExpr(
                c.Expr(arg_exprs[0].c_node, arg_exprs[1].c_node, op='>'),
                c.Const(1),
                c.TernaryExpr(
                    c.Expr(arg_exprs[0].c_node, arg_exprs[1].c_node, op='=='),
                    c.Const(0),
                    c.Const(-1),
                ),
            ),
            inferred_type=func_obj.rtype_obj,
        )
    elif func_obj.builtin and len(arg_exprs) == 2 and arg_exprs[0].inferred_type.builtin and arg_exprs[1].inferred_type.builtin:
        if len(func_obj.xy_node.in_guards) > 0:
            ## the only builtin funcs with in-guards are the exceptions for Int
            if ctx.is_int(arg_exprs[0].inferred_type) and not isinstance(arg_exprs[0].c_node, c.Const):
                report_mixed_signed(expr, arg_exprs, ctx)
            if ctx.is_int(arg_exprs[1].inferred_type) and not isinstance(arg_exprs[1].c_node, c.Const):
                report_mixed_signed(expr, arg_exprs, ctx)
        func_to_op_map = {
            "add": '+',
            "sub": '-',
            "mul": '*',
            "div": '/',
            "mod": '%',
            "or": "||",
            "and": "&&",
            "shiftl": "<<",
            "shiftr": ">>",
            "cmpEq": "==",
            "cmpNe": "!=",
            "cmpGt": ">",
            "cmpGe": ">=",
            "cmpLt": "<",
            "cmpLe": "<=",
        }
        c_arg1 = arg_exprs[0].c_node
        c_arg2 = arg_exprs[1].c_node
        c_op = func_to_op_map[func_obj.xy_node.name.name]

        bit_len = None
        if arg_exprs[0].inferred_type.name.startswith("Bits"):
            if c_op == '-':
                c_op = '^'
            elif c_op in {"&&", "||"}:
                c_op = c_op[1:]
            elif c_op in {"<<", ">>"}:
                bit_len = int(arg_exprs[0].inferred_type.name[len("Bits"):])
                c_arg2_val = get_c_int_val(c_arg2)
                if c_arg2_val is None or c_arg2_val < 0 or c_arg2_val >= bit_len:
                    c_arg2 = c.Expr(c_arg2, c.Const(hex(bit_len-1)), op='&')
        res = c.Expr(
            c_arg1, c_arg2, op=c_op,
        )
        if bit_len is not None and bit_len < 32:
            res = c.Cast(res, func_obj.rtype_obj.c_name)

        if not func_obj.xy_node.name.name.startswith("cmp"):
            inferred_type = func_obj.rtype_obj
            if is_ptr_type(arg_exprs[0].inferred_type, ctx):
                to_type = arg_exprs[0].inferred_type.tags.get("to", None)
                if to_type is None:
                    raise CompilationError("Cannot do arithmetic with untagged pointers", expr)
                if isinstance(inferred_type, TypeObj):
                    inferred_type = TypeExprObj(inferred_type.xy_node, inferred_type.c_node, inferred_type)
                else:
                    inferred_type = copy(inferred_type)
                inferred_type.tags["to"] = arg_exprs[0].inferred_type.tags["to"]
        else:
            if arg_exprs[0].inferred_type is not arg_exprs[1].inferred_type:
                if ctx.is_int(arg_exprs[0].inferred_type) and not isinstance(arg_exprs[0].c_node, c.Const):
                    report_mixed_signed(expr, arg_exprs, ctx)
                if ctx.is_int(arg_exprs[1].inferred_type) and not isinstance(arg_exprs[1].c_node, c.Const):
                    report_mixed_signed(expr, arg_exprs, ctx)
            inferred_type = ctx.bool_obj

        res = optimize_cbinop(res)
        return ExprObj(
            xy_node=expr,
            c_node=res,
            inferred_type=inferred_type,
        )
    elif is_builtin_func(func_obj, "len"):
        dims = arg_exprs[0].inferred_type.dims
        if len(dims) == 0:
            raise CompilationError("Cannot determine array size", expr)
        size = dims[0]
        res = c.Cast(c.Const(size), to="size_t")
        return ExprObj(
            c_node=res,
            xy_node=expr,
            inferred_type=ctx.size_obj
        )
    elif is_builtin_func(func_obj, "sizeof"):
        if arg_exprs[0].num_cnodes > 0:
            redact_code(arg_exprs[0], cast, cfunc, ctx)
            c_node = c.Id(arg_exprs[0].inferred_type.c_name)
        else:
            c_node = arg_exprs[0].c_node
        return ExprObj(
            c_node=c.FuncCall("sizeof", [c_node]),
            inferred_type=ctx.size_obj
        )
    elif is_builtin_func(func_obj, "offsetof"):
        field_obj = arg_exprs[0].compiled_obj
        is_field = not (isinstance(field_obj, VarObj) and field_obj.fieldof_obj is None)
        if not is_field:
            raise CompilationError(
                "Argument of offsetof is not a field in a struct", expr,
                notes=[("Not a field in a struct", arg_exprs[0].xy_node)]
            )
        return ExprObj(
            c_node=c.FuncCall("offsetof", [
                c.Id(field_obj.fieldof_obj.c_node.name),
                c.Id(field_obj.c_node.name),
            ]),
            inferred_type=ctx.size_obj,
        )
    elif is_builtin_func(func_obj, "alignof"):
        if not ctx.added_alignof_macro:
            ctx.added_alignof_macro = True
            cast.consts.append(
                c.Excerpt(
                    "#ifndef __XY_ALIGNOF\n" \
                    "#define __XY_ALIGNOF(type) ((size_t)&((struct { char c; type d; } *)0)->d)\n" \
                    "#endif"
                )
            )

        type_obj = arg_exprs[0].inferred_type
        return ExprObj(
            c_node=c.FuncCall("__XY_ALIGNOF", [
                c.Id(type_obj.c_node.name),
            ]),
            inferred_type=ctx.size_obj,
        )
    elif is_builtin_func(func_obj, "addrof"):
        return compile_builtin_addrof(expr, arg_exprs[0], cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "fieldsof"):
        if arg_exprs[0].inferred_type is any_type_obj:
            raise CompilationError("Cannot get fields of an unknown type", expr)
        return ExprObj(
            xy_node=expr,
            c_node=c.Id("REPORT_IF_YOU_SEE_ME"),
            inferred_type=fieldarray_type_obj,
            compiled_obj=arg_exprs[0],
        )
    elif is_builtin_func(func_obj, "nameof"):
        return compile_nameof(expr, func_obj, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "packageof"):
        return compile_packageof(expr, func_obj, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "fileof"):
        return compile_fileof(expr, func_obj, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "linenoof"):
        return compile_linenoof(expr, func_obj, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "srcof"):
        return compile_srcof(expr, func_obj, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "srclineof"):
        return compile_srclineof(expr, func_obj, arg_exprs, cast, cfunc, ctx)
    elif is_builtin_func(func_obj, "commentof"):
        comment = ""
        if arg_exprs[0].compiled_obj is not None:
            comment = arg_exprs[0].compiled_obj.xy_node.comment
        if not comment:
            comment = arg_exprs[0].xy_node.comment
        comment = fmt_comment(comment)  # delay parsing of comments because they may not be needed
        return compile_expr(
            xy.StrLiteral(
                parts=[xy.Const(comment)], full_str=comment,
                src=expr.src, coords=expr.coords,
            ),
            cast, cfunc, ctx
        )
    elif is_builtin_func(func_obj, "max"):
        name_to_lim = {
            "Byte": "INT8_MAX",
            "Ubyte": "UINT8_MAX",
            "Short": "INT16_MAX",
            "Ushort": "UINT16_MAX",
            "Int": "INT32_MAX",
            "Uint": "UINT32_MAX",
            "Long": "INT64_MAX",
            "Ulong": "UINT64_MAX",
            "Size": "SIZE_MAX",
        }
        if lim := name_to_lim.get(func_obj.rtype_obj.xy_node.name, False):
            return ExprObj(c_node=c.Id(lim), inferred_type=func_obj.rtype_obj)
        else:
            raise CompilationError("Report this to xy devs at TBD", expr)
    elif is_builtin_func(func_obj, "inc") or is_builtin_func(func_obj, "dec"):
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
            inferred_type=func_obj.rtype_obj
        )
    elif is_builtin_func(func_obj, "neg"):
        res = c.UnaryExpr(
            arg=arg_exprs[0].c_node,
            op='-',
            prefix=True,
        )
        return ExprObj(
            c_node=res,
            xy_node=expr,
            inferred_type=func_obj.rtype_obj
        )

    ensure_func_decl(func_obj, cast, cfunc, ctx)

    caller_ctx = ctx
    if func_obj.module_header is not None:
        callee_ctx = func_obj.module_header.ctx
    else:
        callee_ctx = ctx
    callee_ctx = copy(callee_ctx)  # make a shollow copy
    # deep copy only the fields that we need in the new context
    callee_ctx.data_namespaces = copy(callee_ctx.data_namespaces[:2]) # copy only the global and module namespaces. ignore local vars
    callee_ctx.func_namespaces = copy(callee_ctx.func_namespaces[:2])
    callee_ctx.caller_contexts = copy(callee_ctx.caller_contexts)
    callee_ctx.push_caller_context(caller_ctx)
    callee_ctx.tmp_names = caller_ctx.tmp_names
    callee_ctx.current_fobj = caller_ctx.current_fobj

    # XXX
    if hasattr(func_obj.c_node, 'name'):
        res = c.FuncCall(name=func_obj.c_name)
    else:
        res = c.FuncCall(name=func_obj.c_node)

    callee_ctx.push_ns()
    caller_ctx.push_ns()

    args_list = []  # list of all arguments in order of passing including injected ones
    args_writable = []

    for arg in arg_exprs.args:
        assert arg.c_node is not None
    for arg in arg_exprs.kwargs.values():
        assert arg.c_node is not None

    # add arguments
    if func_obj.xy_node is None:
        # add arguments to external c function
        for arg in arg_exprs:
            res.args.append(arg.c_node)
    if func_obj.xy_node is not None:
        # add arguments to a xy function
        for pobj, arg in zip(func_obj.param_objs, arg_exprs.args):
            args_list.append(arg)
            args_writable.append(False)
            caller_ctx.ns[pobj.xy_node.name] = LazyObj(
                xy_node=arg.xy_node, tags=arg.tags, compiled_obj=arg, inferred_type=arg.inferred_type,
            )
            callee_ctx.ns[pobj.xy_node.name] = arg
            if pobj.xy_node.is_callerContext:
                lazy_ctx = arg.from_lazy_ctx or caller_ctx
                callee_ctx.ns[pobj.xy_node.name] = LazyObj(
                    xy_node=xy.CallerContextExpr(arg.xy_node, src=arg.xy_node.src, coords=arg.xy_node.coords),
                    tags=arg.tags,
                    compiled_obj=arg, inferred_type=arg.inferred_type,
                    ctx=lazy_ctx,
                )
                redact_code(arg, cast, cfunc, ctx)
            arg.num_cnodes = 0  # the time for code redaction is over so lets disable it
            check_type_compatibility(arg.xy_node, pobj, arg, ctx, fcall_rules=True)
            if pobj.xy_node.is_pseudo:
                continue
            if pobj.passed_by_ref:
                args_writable[-1] = True
                res.args.append(c_getref(arg))
            else:
                res.args.append(arg.c_node)

        leftover_params = func_obj.param_objs[len(arg_exprs.args):]
        for i, pobj in enumerate(leftover_params):
            if pobj.xy_node.name not in arg_exprs.kwargs:
                try:
                    value_obj = None
                    if getattr(expr, 'inject_args', False):
                        # TODO maybe call compile_id
                        var_decl = ctx.lookup(pobj.xy_node.name, is_func=False)
                        if var_decl is not None and not isinstance(var_decl, VarObj):
                            raise CompilationError(f"'{pobj.xy_node.name}' is not a var", pobj.xy_node)
                        elif var_decl is not None and compatible_types(var_decl.inferred_type, pobj.type_desc):
                            if var_decl.xy_node.is_pseudo:
                                raise CompilationError(f"'{pobj.xy_node.name}' is a pseudo param", var_decl.xy_node)
                            value_obj = ExprObj(
                                c_node=c.Id(var_decl.c_node.name),
                                xy_node=pobj.xy_node,
                                inferred_type=var_decl.type_desc,
                            )
                    if value_obj is None:
                        if pobj.xy_node.value is None:
                            var_decl = ctx.lookup(pobj.xy_node.name, is_func=False)
                            notes = []
                            if isinstance(var_decl, VarObj):
                                notes = [(f"Variable '{pobj.xy_node.name}' has unsuitable type", var_decl.xy_node)]
                                notes.extend(cmp_types_updated(var_decl.inferred_type, pobj.type_desc, expr))
                            raise CompilationError(f"Cannot find var '{pobj.xy_node.name}' to auto inject", expr, notes=notes)
                        value_obj = compile_expr(pobj.xy_node.value, cast, cfunc, callee_ctx)
                    to_move = (
                        (i < len(leftover_params) - 1) or
                        isinstance(value_obj.c_node, c.InitList) or
                        (len(func_obj.xy_node.in_guards) > 0)
                    )
                    if to_move:
                        value_obj = maybe_move_to_temp(value_obj, cast, cfunc, ctx)
                    elif pobj.xy_node.is_pseudo:
                        # ensure pseudo parameters get executed
                        cfunc.body.append(value_obj.c_node)
                except CompilationError as e:
                    raise CompilationError(
                        f"Cannot compile default value for param '{pobj.xy_node.name}'", expr,
                        notes=[
                            (e.error_message, e.xy_node),
                            *(e.notes if e.notes is not None else [])
                        ]
                    )
            else:
                value_obj = arg_exprs.kwargs[pobj.xy_node.name]

            check_type_compatibility(value_obj.xy_node, pobj, value_obj, ctx, fcall_rules=True)
            args_list.append(value_obj)
            args_writable.append(False)
            if not pobj.xy_node.is_pseudo:
                if pobj.passed_by_ref:
                    res.args.append(c_getref(value_obj))
                else:
                    res.args.append(value_obj.c_node)
            callee_ctx.ns[pobj.xy_node.name] = value_obj

    # all arguments have been processed let's now check aliasing rules
    check_aliasing_rules(args_list, args_writable, ctx)

    # compile input guards if any
    in_guards = func_obj.xy_node.in_guards if func_obj.xy_node is not None else []
    out_guards = func_obj.xy_node.out_guards if func_obj.xy_node is not None else []
    if (len(in_guards) + len(out_guards)) > 0:
        cast.includes.append(c.Include("stdlib.h"))
    param_print_code = c.Block()
    for guard in in_guards:
        guard_obj = compile_expr(guard, cast, cfunc, callee_ctx)
        if not is_ct_true(guard_obj):
            on_guard_fail = []
            gen_guard_failed_code(guard, func_obj, cast, on_guard_fail, ctx, is_guard=True)
            if len(param_print_code.body) == 0:
                gen_print_params_code(cast, param_print_code, ctx)
            on_guard_fail.extend(param_print_code.body)

            if ctx.builder.abort_on_unhandled:
                on_guard_fail.append(c.FuncCall("abort"))
            else:
                on_guard_fail.append(c.FuncCall("exit", args=[c.Const(200)]))

            cfunc.body.append(c.If(
                cond=c.UnaryExpr(guard_obj.c_node, op="!", prefix=True),
                body=on_guard_fail
            ))

    rtype_obj = func_obj.rtype_obj
    cast_result = False
    if (func_obj.xy_node is not None and len(func_obj.xy_node.returns) > 0 and
        func_obj.has_calltime_tags
    ):
        # TODO optimize this by evaluating only the values that need it
        rtype_obj = copy(rtype_obj)

        eval_stored_value = callee_ctx.eval_calltime_exprs
        callee_ctx.eval_calltime_exprs = True
        rtype_obj.tags = callee_ctx.eval_tags(
            func_obj.xy_node.returns[0].type.tags,
            tag_specs=rtype_obj.base_type_obj.tag_specs,
        )
        callee_ctx.eval_calltime_exprs = eval_stored_value
        cast_result = True

    macro_expr_obj = None
    if func_obj.is_macro:
        body = func_obj.xy_node.body
        if isinstance(body, xy.Break):
            handle_static_break(expr, body, cast, cfunc, ctx)
        try:
            macro_expr_obj = compile_expr(body, cast, cfunc, callee_ctx, deref=False)
        except CompilationError as e:
            raise CompilationError(
                f"Failed to call macro '{ctx.eval_to_id(func_obj.xy_node.name)}'", expr,
                notes=[(e.error_message, e.xy_node), *(e.notes if e.notes else [])]
            )
        if isinstance(macro_expr_obj, TypeObj):
            raise CompilationError("Functions cannot return a type", expr)
        res = macro_expr_obj.c_node
        rtype_obj = macro_expr_obj.inferred_type
    elif (
        func_obj.xy_node is not None and
        (func_obj.etype_obj is not None or len(func_obj.xy_node.returns) > 1)
    ):
        # call a function that may error
        tmp_cid = None
        if func_obj.rtype_obj is not ctx.void_obj:
            tmp_obj = ctx.create_tmp_var(func_obj.rtype_obj, name_hint="res")
            cfunc.body.append(tmp_obj.c_node)
            tmp_cid = c.Id(tmp_obj.c_node.name)
            res.args.append(c.UnaryExpr(op='&', prefix=True, arg=tmp_cid))

            ret_name = func_obj.xy_node.returns[0].name
            callee_ctx.ns[ret_name] = tmp_obj

        if func_obj.etype_obj is not None:
            # error handling

            # first get the catch frame if any
            cf: CatchFrame = ctx.catch_frames[-1] if len(ctx.catch_frames) > 0 else None

            if cf is None:
                err_obj = ctx.create_tmp_var(func_obj.etype_obj, name_hint="err")
                err_obj.c_node.qtype.is_const = True
                err_obj.c_node.value = res
                cfunc.body.append(err_obj.c_node)
                err_obj_c_name = err_obj.c_node.name
            else:
                cf.ref_count += 1
                cfunc.body.append(c.Expr(
                    c.Id(cf.var_name), res, op="="
                ))
                err_obj_c_name = cf.var_name

            # TODO firgure out a way to remove this two expr_objs
            bool_expr_obj = ExprObj(
                xy_node=expr,
                c_node=c.Id(ctx.bool_obj.c_node.name),
                inferred_type=ctx.bool_obj,
                compiled_obj=ctx.bool_obj,
            )
            err_expr_obj = ExprObj(
                xy_node=expr,
                c_node=c.Id(err_obj_c_name),
                inferred_type=func_obj.etype_obj
            )
            check_error_fcall = find_and_call(
                "to",
                ArgList([err_expr_obj, bool_expr_obj]),
                cast, cfunc, callee_ctx, expr
            )

            check_if = c.If(
                cond=check_error_fcall.c_node,
            )
            if cf is not None:
                cf.inferred_type = func_obj.etype_obj
                check_if.body.append(c.Goto(c.Id(cf.err_label)))
            elif func_obj.etype_obj is ctx.current_fobj.etype_obj:
                call_all_dtors(cast, check_if, ctx)
                check_if.body.append(c.Return(c.Id(err_obj_c_name)))
            else:
                # call unhandled
                do_compile_unhandled_code(expr, err_expr_obj, cast, check_if, caller_ctx, callee_ctx, func_obj)
            cfunc.body.append(check_if)

        else:
            cfunc.body.append(res)

        res = tmp_cid
    else:
        # else if a call to a function that has no error handling
        # no need to do anything the res already has the needed c fcall
        # only cast the result if needed
        if cast_result:
            res = c.Cast(what=res, to=rtype_obj.c_name)

    # finally eval out_guards
    for guard in out_guards:
        guard_obj = compile_expr(guard, cast, cfunc, callee_ctx)
        if not is_ct_true(guard_obj):
            cfunc.body.append(c.If(
                cond=c.UnaryExpr(guard_obj.c_node, op="!", prefix=True),
                body=[c.FuncCall("abort")]
            ))

    if macro_expr_obj is not None:
        raw_fcall_obj = copy(macro_expr_obj)
        raw_fcall_obj.xy_node = expr
    else:
        raw_fcall_obj = ExprObj(
            c_node=res,
            xy_node=expr,
            inferred_type=rtype_obj,
        )

    if func_obj.xy_node is not None and len(func_obj.xy_node.returns) >= 1 and func_obj.xy_node.returns[0].is_index:
        if func_obj.xy_node.returns[0].is_based:
            refto_name = func_obj.xy_node.returns[0].index_in.name
            if refto_name not in callee_ctx.ns:
                raise CompilationError(f"No parameter {refto_name}", func_obj.xy_node.returns[0].index_in)
            base = callee_ctx.ns[refto_name]
        else:
            base = global_memory

        res_obj = idx_setup(
            IdxObj(
                container=base,
                idx=raw_fcall_obj,
                xy_node=expr,
                is_iter_ctor=is_iter_ctor_call(func_obj)
            ),
            cast, cfunc, ctx
        )
    else:
        res_obj = raw_fcall_obj

    callee_ctx.pop_ns()
    caller_ctx.pop_ns()

    return res_obj

def do_compile_field_get_rec(obj, compound_expr, cast, cfunc, ctx):
    res = obj
    if isinstance(compound_expr, xy.BinExpr) and  compound_expr.op == ".":
        res = do_compile_field_get_rec(res, compound_expr.arg1, cast, cfunc, ctx)
        compound_expr = compound_expr.arg2
    assert isinstance(compound_expr, xy.Id)
    return do_compile_field_get(res, compound_expr, cast, cfunc, ctx)

def do_compile_field_get(obj, field_node, cast, cfunc, ctx, deref=False, expr=None):
    if not isinstance(field_node, xy.Id):
        raise CompilationError("The right hand side of '.' must be an identifier", field_node)
    field_name = field_node.name
    struct_obj = obj.inferred_type
    if field_name not in struct_obj.fields:
        raise CompilationError(f"No such field in struct {struct_obj.name}", field_node)
    is_field_of_type = isinstance(obj.compiled_obj, TypeObj)
    if not is_field_of_type:
        # normal get of an object
        fget_obj = field_get(obj, struct_obj.fields[field_name], cast, cfunc, ctx)
        fget_obj.xy_node = expr or field_node
        return maybe_deref(fget_obj, deref, cast, cfunc, ctx)
    else:
        # getting a field of a type
        field_obj = struct_obj.fields[field_name]
        return field_obj.default_value_obj

def gen_guard_failed_code(expr, func_obj: FuncObj, cast, cbody, ctx: CompilerContext, is_guard=False):
    if not ctx.builder.rich_errors:
        return

    cast.includes.append(c.Include("stdio.h"))
    fn = os.path.relpath(expr.src.filename)
    cbody.append(c.FuncCall("fprintf", args=[
        c.Id("stderr"),
        c.Const(f"\"\\n{fn}:%d \""),
        c.Const(find_lineof(expr))
    ]))
    func_module_name = func_obj.module_header.module_name if func_obj.module_header else ctx.module_name
    func_fullname = func_module_name + "." + ctx.eval_to_id(func_obj.xy_node.name)
    general_message = f"\"Guard failed when calling {func_fullname}!\\n\""
    if not is_guard:
        general_message = f"\"When calling {func_fullname}!\\n\""
    cbody.append(c.FuncCall("fprintf", args=[c.Id("stderr"), c.Const(general_message)]))
    linesrc = escape_str(find_linesrc(expr))
    cbody.append(c.FuncCall("fprintf", args=[c.Id("stderr"), c.Const(f"\"| %s\\n\""), c.Const(f"\"{linesrc}\"")]))

def gen_print_params_code(cast, cfunc, ctx: CompilerContext):
    if not ctx.builder.rich_errors:
        return
    cfunc.body.append(c.FuncCall("fprintf", args=[c.Id("stderr"), c.Const("\"Arguments to Function are:\\n\"")]))
    for name, obj in ctx.ns.items():
        if not is_tmp_expr(obj):
            gen_print_var(name, obj, cast, cfunc, ctx)

def gen_print_var(name, obj: CompiledObj, cast, cfunc, ctx, ident=4, endl=True):
    fmt = []
    args = []

    decompose_obj_in_prints(obj, fmt, args, cast, cfunc, ctx)

    fmt = "".join(fmt)
    end = '\\n' if endl else ''
    cfunc.body.append(c.FuncCall("fprintf", args=[c.Id("stderr"), c.Const(f"\"{' ' * ident }%s={fmt}{end}\""), c.Const(f"\"{name}\""), *args]))

def decompose_obj_in_prints(obj, fmt, args, cast, cfunc, ctx: CompilerContext):
    if obj.c_node is None and isinstance(obj, LazyObj): obj = obj.compiled_obj
    if obj.c_node is None or obj.inferred_type is None:
        fmt.append("\"???\"")
    if isinstance(obj, VarObj):
        obj = var_to_expr_obj(obj.xy_node, obj, cast, cfunc, ctx, False)

    if isinstance(obj.c_node, c.VarDecl):
        return

    c_node = obj.c_node
    if isinstance(c_node, c.VarDecl):
        c_node = c.Id(c_node.name)

    type_obj = obj.inferred_type
    tags = type_obj.tags
    if isinstance(type_obj, TypeExprObj):
        type_obj = type_obj.type_obj

    if type_obj.builtin:
        specifier = {
            "Int": "%d",
            "Size": "%zu",
            "Ptr": "%p",
            "Uint": "%u",
            "Bool": "%d",
            "Float": "%f",
            "Double": "%f",
        }.get(type_obj.name, None)
        if specifier is not None:
            fmt.append(specifier)
            args.append(c_node)
        else:
            fmt.append("???")
    elif not type_obj.is_external:
        fmt.append(type_obj.name)
        fmt.append("{")
        trailing_comma = False
        for fname, field in type_obj.fields.items():
            if field.is_pseudo: continue
            if field.c_node is None: continue
            fmt.append(field.xy_node.name + "=")
            fget_obj = field_get(obj, field, None, None, ctx)
            decompose_obj_in_prints(fget_obj, fmt, args, cast, cfunc, ctx)
            fmt.append(", ")
            trailing_comma = True
        if trailing_comma: fmt.pop()
        fmt.append("}")
    if len(tags):
        fmt.append("~")
        fmt.append(escape_str(fmt_tags(tags, ctx)))

def fmt_tags(tags: dict, ctx: CompilerContext):
    res = ["["]
    for tag_name, tag_obj in tags.items():
        res.append(f"{tag_name}=")
        if isinstance(tag_obj, TypeExprObj):
            type_obj = tag_obj.type_obj
            res.append(type_obj.name)
        elif isinstance(tag_obj, TypeObj):
            res.append(tag_obj.name)
        else:
            res.append("???")
        res.append(",")
    if len(tags) > 0: res.pop()
    res.append("]")
    return "".join(res)

def compile_nameof(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    redact_code(arg_exprs[0], cast, cfunc, ctx)
    if isinstance(arg_exprs[0].compiled_obj, ArrTypeObj):
        name = arg_exprs[0].compiled_obj.base_type_obj.xy_node.name
        name += "[" + ",".join(str(d) for d in arg_exprs[0].compiled_obj.dims) + "]"
    elif isinstance(arg_exprs[0].compiled_obj, VarObj):
        name = arg_exprs[0].compiled_obj.xy_node.name
    elif isinstance(arg_exprs[0].compiled_obj, (TypeObj, TypeExprObj)):
        name = arg_exprs[0].compiled_obj.name
    elif isinstance(arg_exprs[0].compiled_obj, FuncTypeObj):
        if arg_exprs[0].compiled_obj.func_obj is not None:
            name = arg_exprs[0].compiled_obj.func_obj.xy_node.name
        else:
            name = "UNKNOWN"
    elif isinstance(arg_exprs[0].compiled_obj, FuncObj):
        name = arg_exprs[0].compiled_obj.xy_node.name.name
    else:
        raise CompilationError("Cannot determine name", expr)
    return compile_expr(
        xy.StrLiteral(
            parts=[xy.Const(name)], full_str=name,
            src=expr.src, coords=expr.coords,
        ),
        cast, cfunc, ctx
    )

def compile_packageof(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    redact_code(arg_exprs[0], cast, cfunc, ctx)
    obj = arg_exprs[0].compiled_obj
    if obj is None:
        obj = arg_exprs[0]
    obj_ctx = None
    if isinstance(obj, (FuncObj, TypeObj)) and obj.module_header is not None:
        obj_ctx = obj.module_header.ctx
    if obj_ctx is None:
        obj_ctx = ctx
    return compile_expr(
        xy.StrLiteral(
            parts=[xy.Const(obj_ctx.module_name)], full_str=obj_ctx.module_name,
            src=expr.src, coords=expr.coords,
        ),
        cast, cfunc, ctx
    )

def compile_fileof(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    if len(arg_exprs) > 0:
        redact_code(arg_exprs[0], cast, cfunc, ctx)
        obj = arg_exprs[0].compiled_obj
        if obj is None:
            obj = arg_exprs[0]
        xy_node = obj.xy_node
    else:
        xy_node = expr
    file = xy_node.src.filename
    file = os.path.relpath(file)
    return compile_expr(
        xy.StrLiteral(
            parts=[xy.Const(file)], full_str=file,
            src=expr.src, coords=expr.coords,
        ),
        cast, cfunc, ctx
    )

def compile_linenoof(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    if len(arg_exprs) > 0:
        redact_code(arg_exprs[0], cast, cfunc, ctx)
        obj = arg_exprs[0].compiled_obj
        if obj is None:
            obj = arg_exprs[0]
        xy_node = obj.xy_node
    else:
        xy_node = expr

    line_num = find_lineof(xy_node)

    return compile_expr(
        xy.Const(
            line_num, src=expr.src, coords=expr.coords, type="Uint",
        ),
        cast, cfunc, ctx
    )

def find_lineof(node):
    start = node.coords[0]
    line_num = 1 if start >= 0 else -1
    for i in range(start):
        if node.src.code[i] == "\n":
            line_num += 1
    return line_num

def find_linesrc(node):
    i = node.coords[0] - 1
    while i >= 0 and node.src.code[i] != "\n":
        i -= 1
    j = node.coords[1]
    while j < len(node.src.code) and node.src.code[j] != "\n":
        j += 1
    return node.src.code[i+1:j]

def compile_srcof(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    if len(arg_exprs) > 0:
        redact_code(arg_exprs[0], cast, cfunc, ctx)
        obj = arg_exprs[0].compiled_obj
        if obj is None:
            obj = arg_exprs[0]
        xy_node = obj.xy_node
    else:
        xy_node = expr
    src = xy_node.src.code[xy_node.coords[0]:xy_node.coords[1]]
    src = escape_str(src)
    return compile_expr(
        xy.StrLiteral(
            parts=[xy.Const(src)], full_str=src,
            src=expr.src, coords=expr.coords,
        ),
        cast, cfunc, ctx
    )

def compile_srclineof(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    if len(arg_exprs) > 0:
        redact_code(arg_exprs[0], cast, cfunc, ctx)
        obj = arg_exprs[0].compiled_obj
        if obj is None:
            obj = arg_exprs[0]
        xy_node = obj.xy_node
    else:
        xy_node = expr
    line = escape_str(find_linesrc(xy_node))
    return compile_expr(
        xy.StrLiteral(
            parts=[xy.Const(line)], full_str=line,
            src=expr.src, coords=expr.coords,
        ),
        cast, cfunc, ctx
    )

def compile_list_comprehension(expr: xy.ListComprehension, cast, cfunc, ctx: CompilerContext, is_assign=False):
    if len(expr.loop.over) != 1:
        raise CompilationError("List Comprehension with more than one loop is NYI", expr.loop)
    if isinstance(expr.loop.block.body, list):
        raise CompilationError("Array Comprehension expressions must have a single inlined expression as body")

    # determine len
    container_node = expr.loop.over[0].arg2
    iter_var_name = expr.loop.over[0].arg1
    container_obj = compile_expr(container_node, cast, cfunc, ctx)
    container_obj = maybe_move_to_temp(container_obj, cast, cfunc, ctx)

    dst_obj = None
    if expr.list_type is not None:
        dst_obj = compile_expr(expr.list_type, cast, cfunc, ctx, deref=False)
        if not is_assign:
            if not isinstance(dst_obj.compiled_obj, (TypeExprObj, TypeObj)):
                copy_obj = find_and_call("copy", ArgList([dst_obj]), cast, cfunc, ctx, expr)
            else:
                copy_obj = ExprObj(
                    expr, c_node=dst_obj.compiled_obj.init_value, inferred_type=dst_obj.inferred_type,
                )
            tmp_obj = ctx.create_tmp_var(copy_obj.inferred_type, "comp")
            tmp_obj.c_node.value = copy_obj.c_node
            cfunc.body.append(tmp_obj.c_node)
            dst_obj = ExprObj(
                expr,
                c_node=c.Id(tmp_obj.c_node.name),
                inferred_type=copy_obj.inferred_type,
                compiled_obj=tmp_obj,
            )

    if isinstance(container_obj.inferred_type, ArrTypeObj):
        arr_len = container_obj.inferred_type.dims[0]

        c_node = c.InitList()
        ctx.push_ns()
        for i in range(arr_len):
            ctx.ns[iter_var_name.name] = ExprObj(
                xy_node=iter_var_name,
                c_node=c.Index(expr=container_obj.c_node, index=c.Const(i)),
                inferred_type=container_obj.inferred_type.base_type_obj,
            )
            elem_obj = compile_expr(expr.loop.block.body, cast, cfunc, ctx)
            if dst_obj is None:
                c_node.elems.append(elem_obj.c_node)
            else:
                append_fcall = find_and_call_append(ArgList([dst_obj, elem_obj]), cast, cfunc, ctx, expr)
                cfunc.body.append(append_fcall.c_node)
        ctx.pop_ns()

        return dst_obj or ExprObj(
            xy_node=expr,
            c_node=c_node,
            inferred_type=container_obj.inferred_type
        )
    elif container_obj.inferred_type is fieldarray_type_obj:
        fields = container_obj.compiled_obj.inferred_type.fields
        arr_len = len(fields)
        elem_type_obj = None

        c_node = c.InitList()
        ctx.push_ns()
        for fname, f in fields.items():
            f_obj = field_get(container_obj.compiled_obj, f, cast, cfunc, ctx)
            ctx.ns[iter_var_name.name] = ExprObj(
                xy_node=iter_var_name,
                c_node=f_obj.c_node,
                inferred_type=f.type_desc,
                compiled_obj=f_obj.compiled_obj,
            )
            elem_obj = compile_expr(expr.loop.block.body, cast, cfunc, ctx)
            if dst_obj is None:
                c_node.elems.append(elem_obj.c_node)
            else:
                append_fcall = find_and_call_append(ArgList([dst_obj, elem_obj]), cast, cfunc, ctx, expr)
                cfunc.body.append(append_fcall.c_node)
            elem_type_obj = elem_obj.inferred_type
        ctx.pop_ns()

        res_inferred_type = ArrTypeObj(
            xy_node=expr, c_node=c_node, dims=[arr_len],
            base_type_obj=elem_type_obj
        )

        return dst_obj or ExprObj(
            xy_node=expr,
            c_node=c_node,
            inferred_type=res_inferred_type
        )
    elif container_obj.inferred_type is fselection_type_obj:
        func_type_objs: list[FuncTypeObj] = container_obj.compiled_obj
        arr_len = len(func_type_objs)

        c_node = c.InitList()
        ctx.push_ns()
        for func_type_obj in func_type_objs:
            ctx.ns[iter_var_name.name] = ExprObj(
                xy_node=iter_var_name,
                c_node=c.Id(func_type_obj.func_obj.c_node.name),
                inferred_type=func_type_obj,
                compiled_obj=func_type_obj.func_obj,
            )
            elem_obj = compile_expr(expr.loop.block.body, cast, cfunc, ctx)
            if dst_obj is None:
                c_node.elems.append(elem_obj.c_node)
            else:
                append_fcall = find_and_call_append(ArgList([dst_obj, elem_obj]), cast, cfunc, ctx, expr)
                cfunc.body.append(append_fcall.c_node)
            elem_type_obj = elem_obj.inferred_type
        ctx.pop_ns()

        if arr_len > 0:
            inferred_type = ArrTypeObj(
                xy_node=expr, c_node=c_node, dims=[arr_len],
                base_type_obj=elem_type_obj
            )
        else:
            inferred_type = TypeInferenceError(
                "Cannot infer type of empty array"
            )

        return dst_obj or ExprObj(
            xy_node=expr,
            c_node=c_node,
            inferred_type=inferred_type
        )
    else:
        raise CompilationError("List comprehension is supported only on arrays", container_obj.xy_node)

def check_aliasing_rules(arg_exprs, arg_writable, ctx: CompilerContext):
    assert len(arg_exprs) == len(arg_writable)
    toplevel = {}
    for i, expr in enumerate(arg_exprs):
        # first get the level
        expr_level = 0
        top_expr = expr if isinstance(expr, IdxObj) else expr.compiled_obj
        # print(fmt_err_msg("First", top_expr.xy_node))
        while isinstance(top_expr, IdxObj):
            expr_level += 1
            top_expr = top_expr.container
            # print(fmt_err_msg("Loop", top_expr.xy_node))
        top_expr = top_expr.compiled_obj if getattr(top_expr, 'compiled_obj', None) is not None else top_expr
        # if top_expr is not None:
        #     print(fmt_err_msg("End", top_expr.xy_node))

        prev_expr_i, prev_level = toplevel.get(id(top_expr), (None, expr_level))
        toplevel[id(top_expr)] = (i, expr_level)
        if expr_level != prev_level:
            if arg_writable[i] or arg_writable[prev_expr_i]:
                # mut param so error
                raise CompilationError(
                    "Cannot get a reference to a variable and an element of that "
                    "variable at the same time.", expr.xy_node,
                    notes=[
                        ("Previous reference acquired here", arg_exprs[prev_expr_i].xy_node)
                    ]
                )
            else:
                # not writable but if encountered again by a writable param it must be an invalid level
                toplevel[id(top_expr)] = (i, -1)

class NoCallerContextError(Exception):
    pass

def compile_caller_context_expr(expr: xy.CallerContextExpr, cast, cfunc, ctx: CompilerContext):
    if not ctx.has_caller_context():
        if not ctx.eval_calltime_exprs:
            # signal to the caller that this expr cannot be compiled at the moment
            raise NoCallerContextError
        raise CompilationError("No caller context", expr)
    return compile_expr(expr.arg, cast, cfunc, ctx.get_caller_context())

def ensure_func_decl(func_obj: FuncObj, cast, cfunc, ctx):
    if func_obj.module_header is not None:
        return # function in a different module
    if func_obj.xy_node is None:
        return # external c functions have declarations someplace else
    if func_obj.decl_visible:
        return
    func_obj.decl_visible = True
    if not func_obj.is_macro:
        cast.func_decls.append(func_obj.c_node)


def redact_code(obj: ExprObj, cast, cfunc, ctx):
    if obj.num_cnodes > 0:
        for idx in range(obj.first_cnode_idx, obj.first_cnode_idx + obj.num_cnodes):
            getattr(obj, 'redact_cfunc', cfunc).body[idx] = c.Empty()
        obj.num_cnodes = 0
    if isinstance(obj, ExprObj):
        for tmp_var_name in obj.tmp_var_names:
            for ns in ctx.data_namespaces[::-1]:
                if ns.pop(tmp_var_name, None) is not None:
                    break
        obj.tmp_var_names = set()
    if isinstance(obj.compiled_obj, ExprObj):
        for tmp_var_name in obj.compiled_obj.tmp_var_names:
            for ns in ctx.data_namespaces[::-1]:
                if ns.pop(tmp_var_name, None) is not None:
                    break
        obj.compiled_obj.tmp_var_names = set()

def compile_builtin_get(expr, func_obj, arg_exprs, cast, cfunc, ctx):
    assert len(arg_exprs) in range(1, 3)

    base_cnode = arg_exprs[0].c_node
    inferred_type = None
    if isinstance(arg_exprs[0].inferred_type, ArrTypeObj):
        if isinstance(base_cnode, c.InitList):
            # convert InitList to compuond literal to keep c happy
            base_type = c.Id(arg_exprs[0].inferred_type.base_type_obj.c_name)
            for dim in arg_exprs[0].inferred_type.dims:
                base_type = c.Index(base_type, c.Const(dim))
            base_cnode = c.CompoundLiteral(
                base_type,
                base_cnode.elems,
            )
        inferred_type=arg_exprs[0].inferred_type.base_type_obj
    else:
        assert is_ptr_type(arg_exprs[0].inferred_type, ctx)
        base_cnode = arg_exprs[0].c_node
        inferred_type=arg_exprs[0].inferred_type.tags["to"]

    if len(arg_exprs) == 1:
        res = c.UnaryExpr(arg=base_cnode, op="*", prefix=True)
    else:
        index_cnode = arg_exprs[1].c_node
        res = c.Index(base_cnode, index_cnode)

    return ExprObj(
        xy_node=expr,
        c_node=res,
        inferred_type=inferred_type
    )

def compile_builtin_addrof(expr, arg_obj, cast, cfunc, ctx: CompilerContext):
    if isinstance(arg_obj.compiled_obj, VarObj) and arg_obj.compiled_obj.c_node is not None:
        # Pointers in xy don't have any constness attached to them so
        # any const variables must be made non-const
        arg_obj.compiled_obj.c_node.qtype.is_const = False
    type_obj = arg_obj.inferred_type
    if isinstance(type_obj, ArrTypeObj):
        type_obj = type_obj.base_type_obj
        c_node=arg_obj.c_node
    else:
        arg_c_node = arg_obj.c_node
        if isinstance(arg_c_node, (c.Const, c.CompoundLiteral)):
            if isinstance(arg_obj.xy_node, (xy.Const, xy.StrLiteral)):
                raise CompilationError("Cannot get address of a const", expr)
            tmp_obj = ctx.create_tmp_var(type_obj, "addrof", expr)
            cfunc.body.append(tmp_obj.c_node)
            arg_c_node = c.Id(tmp_obj.c_node.name)

        c_node=c.UnaryExpr(arg=arg_c_node, op="&", prefix=True)

    return ExprObj(
        c_node=c_node,
        inferred_type=ptr_type_to(type_obj, ctx)
    )

def compile_global_get(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx):
    arg_obj = arg_exprs[0]
    to_type = arg_obj.inferred_type.tags.get("type", None)
    if not isinstance(to_type, (TypeObj, TypeExprObj)):
        raise CompilationError("Argument to 'global' must be a type", expr)
    ctx.register_global_type(to_type)

    ptr_type = TypeExprObj(
        xy_node=func_obj.xy_node.returns[0],
        c_node=func_obj.rtype_obj.c_node,
        type_obj=func_obj.rtype_obj.type_obj,
        tags={
            "to":  to_type,
        }
    )

    c_res = c.Cast(
        c.Index(
            c.Expr(c.Id("g__xy_global"), c.Id("stack"), op="->"),
            c.Id(mangle_type_id(to_type)),
        ),
        to=to_type.c_name + "*"
    )

    return IdxObj(
        xy_node=expr,
        container=global_memory,
        idx=ExprObj(
            c_node=c_res,
            xy_node=expr,
            inferred_type=ptr_type,
        ),
        inferred_type=to_type,  # TODO what about tags
    )

def compile_global_set(expr, func_obj, arg_exprs: ArgList, cast, cfunc, ctx: CompilerContext):
    val_obj = arg_exprs[1]
    new_cval = val_obj.c_node
    if not isinstance(new_cval, c.Id):
        new_cval = move_to_temp(val_obj, cast, cfunc, ctx).c_node

    stored_type = TypeExprObj(expr, type_obj=ctx.ptr_obj, tags={"to": val_obj.inferred_type})
    stored_obj = ctx.create_tmp_var(stored_type, "gstack", expr)
    stored_obj.needs_dtor = True
    stored_obj.is_stored_global = True
    stored_obj.c_node.value = c.Index(
        c.Expr(c.Id("g__xy_global"), c.Id("stack"), op="->"),
        c.Id(mangle_type_id(val_obj.inferred_type)),
    )
    cfunc.body.append(stored_obj.c_node)

    c_node = c.Expr(
        c.Index(
            c.Expr(c.Id("g__xy_global"), c.Id("stack"), op="->"),
            c.Id(mangle_type_id(val_obj.inferred_type)),
        ),
        c.UnaryExpr(new_cval, op="&", prefix=True),
        op="=",
    )
    return ExprObj(
        expr,
        c_node,
        ctx.void_obj,
    )

def restore_global(stored_obj, cast, cfunc, ctx):
    c_node = c.Expr(
        c.Index(
            c.Expr(c.Id("g__xy_global"), c.Id("stack"), op="->"),
            c.Id(mangle_type_id(stored_obj.inferred_type.tags["to"])),
        ),
        c.Id(stored_obj.c_node.name),
        op="=",
    )
    cfunc.body.append(c_node)

def is_builtin_func(func_obj, name):
    return func_obj.builtin and func_obj.xy_node.name.name == name

def handle_static_break(expr, brk, cast, cfunc, ctx):
    if isinstance(brk.loop_name, xy.StrLiteral):
        raise CompilationError(brk.loop_name.full_str, expr)
    else:
        raise CompilationError("Invalid 'break' expression. If you want to break compilation use a string", expr)

def report_mixed_signed(expr, arg_exprs, ctx):
    msg = "Mixed signedness arithmetic ("
    msg += arg_exprs[0].inferred_type.name
    msg += ", " + arg_exprs[1].inferred_type.name
    msg += "). Please cast one of the operands to a suitable type."
    raise CompilationError(msg, expr)

def typeEqs(expr, arg_exprs, cast, cfunc, ctx):
    assert len(arg_exprs) == 2
    for i in range(len(arg_exprs)):
        if not isinstance(arg_exprs[i].compiled_obj, TypeObj):
            raise CompilationError("Expected type", arg_exprs[i].xy_node)

    t1 = arg_exprs[0].compiled_obj
    t2 = arg_exprs[1].compiled_obj
    if t1 is t2:
        return ctx.trueObj(expr)

    if type(t1) is not type(t2):
        return ctx.falseObj(expr)

    if not typeEqs([t1.base_type_obj, t2.base_type_obj], cast, cfunc, ctx):
        return ctx.falseObj(expr)

    if t1.tags.keys() != t2.tags.keys():
        return ctx.falseObj(expr)

    if isinstance(t1, ArrTypeObj):
        if t1.dims != t2.dims:
            return ctx.falseObj(expr)

    return ctx.trueObj(expr)

def is_ct_true(obj):
    return isinstance(obj.c_node, c.Const) and obj.c_node.value == "true"

def compile_if(ifexpr, cast, cfunc, ctx):
    c_if = c.If()
    ctx.push_ns()
    cond_obj = compile_expr(ifexpr.cond, cast, cfunc, ctx)
    # TODO check type is bool
    c_if.cond = cond_obj.c_node

    # the first if in an if chain is handled seperately becase it should
    # provide the return type for the entire chain
    inferred_type = None
    c_res = None
    if_exp_obj = None
    if ifexpr.block.is_embedded:
        if_exp_obj = compile_expr(ifexpr.block.body, cast, c_if, ctx)
        inferred_type = if_exp_obj.inferred_type
    elif len(ifexpr.block.returns) > 0:
        if len(ifexpr.block.returns) > 1:
            raise CompilationError("Multiple results are NYI", ifexpr)
        inferred_type = find_type(ifexpr.block.returns[0].type, cast, ctx)
    else:
        inferred_type = ctx.void_obj

    # create tmp var if needed
    if_result_name = None
    result_var = None
    if inferred_type is not None and inferred_type is not ctx.void_obj:
        if_result_name = None
        if not ifexpr.block.is_embedded:
            if_result_name = ifexpr.block.returns[0].name
        if if_result_name is None:
            if_result_name = ifexpr.name
            if_result_name = ctx.eval_to_id(if_result_name) if if_result_name is not None else ""
        var_obj = ctx.create_tmp_var(inferred_type, name_hint=if_result_name)
        cfunc.body.append(var_obj.c_node)
        ctx.ns[if_result_name] = var_obj
        result_var = var_obj
        c_res = c.Id(var_obj.c_node.name)

    # compile if body
    ctx.push_ns()
    if if_exp_obj is None:
        compile_body(ifexpr.block.body, cast, c_if, ctx)
    elif inferred_type is not ctx.void_obj:
        res_assign = c.Expr(c_res, if_exp_obj.c_node, op='=')
        c_if.body.append(res_assign)
    else:
        c_if.body.append(if_exp_obj.c_node)
    ctx.pop_ns()

    # subsequent ifs
    next_if = ifexpr.else_node
    next_c_if = c_if
    while isinstance(next_if, xy.IfExpr):
        ctx.push_ns()
        gen_if = c.If()
        next_c_if.else_body = c.Block()
        gen_if.cond = compile_expr(next_if.cond, cast, next_c_if.else_body, ctx).c_node
        if not next_if.block.is_embedded:
            compile_body(next_if.block.body, cast, gen_if, ctx)
        elif next_if.block is not None:
            if_exp_obj = compile_expr(next_if.block.body, cast, gen_if, ctx)
            res_assign = c.Expr(c_res, if_exp_obj.c_node, op='=')
            # TODO compare types
            gen_if.body.append(res_assign)

        if len(next_c_if.else_body.body) > 0:
            next_c_if.else_body.body.append(gen_if)
        else:
            # optimize for else if chaines
            next_c_if.else_body = gen_if
        next_c_if = gen_if
        next_if = next_if.else_node
        ctx.pop_ns()

    ctx.pop_ns()

    # finaly the else if any
    assert isinstance(next_if, xy.Block) or next_if is None
    ctx.push_ns()
    if if_result_name:
        ctx.ns[if_result_name] = result_var
    if next_if is not None and not next_if.is_embedded:
        # normal else
        # XXX fix that
        hack_if = c.If()
        compile_body(next_if.body, cast, hack_if, ctx)
        next_c_if.else_body = hack_if.body
    elif next_if is not None:
        # else is direct result
        next_c_if.else_body = c.Block()
        else_exp_obj = compile_expr(next_if.body, cast, next_c_if.else_body, ctx)
        res_assign = c.Expr(c_res, else_exp_obj.c_node, op='=')
        # TODO compare types
        next_c_if.else_body.body.append(res_assign)
    ctx.pop_ns()

    c_if = optimize_if(c_if)
    if c_if is not None:
        if isinstance(c_if, list):
            cfunc.body.extend(c_if)
        else:
            cfunc.body.append(c_if)

    return ExprObj(
        xy_node=ifexpr,
        c_node=c_res,
        inferred_type=inferred_type
    )

def compile_while(xywhile: xy.WhileExpr, cast, cfunc, ctx: CompilerContext):
    cwhile = c.While()
    loop_data = ctx.push_ns(NamespaceType.Loop).data
    if xywhile.name:
        loop_data.loop_name = ctx.eval_to_id(xywhile.name)

    complex_cond = len(cfunc.body)
    cond_obj = compile_expr(xywhile.cond, cast, cfunc, ctx)
    complex_cond = len(cfunc.body) != complex_cond
    cwhile.cond = cond_obj.c_node

    # determine return type if any
    inferred_type = None
    res_c = None
    update_expr_obj = None

    # register loop variables
    for loop_vardecl in xywhile.block.returns:
        if loop_vardecl.name:
            value_obj = compile_expr(loop_vardecl.value, cast, cfunc, ctx) if loop_vardecl.value is not None else None
            type_desc = find_type(loop_vardecl.type, cast, ctx) if loop_vardecl.type is not None else None

            inferred_type = type_desc if type_desc is not None else value_obj.inferred_type
            name_hint = loop_vardecl.name
            tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
            ctx.ns[name_hint] = tmp_obj
            if value_obj is not None:
                tmp_obj.c_node.value = value_obj.c_node
            cfunc.body.append(tmp_obj.c_node)
            res_c = c.Id(tmp_obj.c_node.name)

    if xywhile.block.is_embedded:
        update_expr_obj = compile_expr(xywhile.block.body, cast, cwhile, ctx)
        inferred_type = update_expr_obj.inferred_type

    # create tmp var if needed
    if inferred_type is None:
        inferred_type = ctx.void_obj

    name_hint = None
    if inferred_type is not ctx.void_obj and res_c is None:
        if isinstance(xywhile.block, xy.Block):
            name_hint = xywhile.block.returns[0].name
        if name_hint is None:
            name_hint = ctx.eval_to_id(xywhile.name)
        tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
        ctx.data_ns[name_hint] = tmp_obj
        cfunc.body.append(tmp_obj.c_node)
        res_c = c.Id(tmp_obj.c_node.name)

    # generate label before the body
    if complex_cond:
        loop_data.continue_label_name = ctx.gen_tmp_label_name(name_hint or "")

    # compile body
    if update_expr_obj is None:
        compile_body(xywhile.block.body, cast, cwhile, ctx)
    else:
        cwhile.body.append(update_expr_obj.c_node)

    # reeval condition again if necessary
    if complex_cond:
        # in theory we can simply copy paste the already generate code
        # but that looks too hacky
        if loop_data.label_used:
            cwhile.body.append(c.Label(loop_data.continue_label_name))
        reeval_cond_obj = compile_expr(xywhile.cond, cast, cwhile, ctx)
        if is_tmp_expr(cond_obj):
            cwhile.body.append(c.Expr(cwhile.cond, reeval_cond_obj.c_node, op="="))

    cfunc.body.append(cwhile)
    ctx.pop_ns()

    return ExprObj(
        xy_node=xywhile,
        c_node=res_c,
        inferred_type=inferred_type,
    )

def compile_dowhile(xydowhile, cast, cfunc, ctx):
    cdowhile = c.DoWhile()
    loop_data = ctx.push_ns(NamespaceType.Loop).data
    if xydowhile.name:
        loop_data.loop_name = ctx.eval_to_id(xydowhile.name)

    # determine return type if any
    inferred_type = None
    res_c = None
    update_expr_obj = None

    # register loop variables
    for loop_vardecl in xydowhile.block.returns:
        if loop_vardecl.name:
            value_obj = compile_expr(loop_vardecl.value, cast, cfunc, ctx) if loop_vardecl.value is not None else None
            type_desc = find_type(loop_vardecl.type, cast, ctx) if loop_vardecl.type is not None else None

            inferred_type = type_desc if type_desc is not None else value_obj.inferred_type
            name_hint = loop_vardecl.name
            tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
            ctx.data_ns[name_hint] = tmp_obj
            if value_obj is not None:
                tmp_obj.c_node.value = value_obj.c_node
            cfunc.body.append(tmp_obj.c_node)
            res_c = c.Id(tmp_obj.c_node.name)

    # create tmp var if needed
    if inferred_type is None:
        inferred_type = ctx.void_obj

    name_hint = None
    if inferred_type is not ctx.void_obj and res_c is None:
        if isinstance(xydowhile.block, xy.Block):
            name_hint = xydowhile.block.returns[0].name
        if name_hint is None:
            name_hint = ctx.eval_to_id(xydowhile.name)
        tmp_obj = ctx.create_tmp_var(inferred_type, name_hint=name_hint)
        ctx.data_ns[name_hint] = tmp_obj
        cfunc.body.append(tmp_obj.c_node)
        res_c = c.Id(tmp_obj.c_node.name)

    # compile body
    if not xydowhile.block.is_embedded:
        compile_body(xydowhile.block.body, cast, cdowhile, ctx)

    # gen continue label
    loop_data.continue_label_name = ctx.gen_tmp_label_name(name_hint or "")
    cdowhile.body.append(c.Label(loop_data.continue_label_name))
    cnt_label_idx = len(cdowhile.body) - 1

    # compile cond
    if xydowhile.block.is_embedded:
        update_expr_obj = compile_expr(xydowhile.block.body, cast, cdowhile, ctx)
        inferred_type = update_expr_obj.inferred_type

    cond_obj = compile_expr(xydowhile.cond, cast, cdowhile, ctx)
    cdowhile.cond = cond_obj.c_node

    # Remove the label if it hasn't been used
    if not loop_data.label_used:
        cdowhile.body[cnt_label_idx] = c.Empty()

    cfunc.body.append(cdowhile)
    ctx.pop_ns()

    return ExprObj(
        xy_node=xydowhile,
        c_node=res_c,
        inferred_type=inferred_type,
    )

def compile_for(for_node: xy.ForExpr, cast, cfunc, ctx: CompilerContext):
    cfor = c.For()
    ctx.push_ns(NamespaceType.Loop)

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
                    (start_obj is None or ctx.is_prim_int(start_obj.inferred_type)) and
                    (end_obj is None or ctx.is_prim_int(end_obj.inferred_type)) and
                    (step_obj is None or ctx.is_prim_int(step_obj.inferred_type))
                )

                if is_prim_int:
                    # built-in case of a slice of only ints

                    if start_obj is not None:
                        iter_type = start_obj.inferred_type
                    elif end_obj is not None:
                        iter_type = end_obj.inferred_type
                    elif step_obj is not None:
                        iter_type = step_obj.inferred_type
                    else:
                        iter_type = ctx.uint_obj

                    # compile start
                    start_value = start_obj.c_node if start_obj is not None else iter_type.init_value
                    iter_var_decl = c.VarDecl(iter_name, c.QualType(iter_type.c_name, is_const=False), value=start_value)
                    ctx.ns[iter_name] = VarObj(xy_node=iter_node, c_node=iter_var_decl, type_desc=iter_type)
                    if for_outer_block is None and ctx.ns[iter_name].needs_dtor:
                        for_outer_block = c.Block()
                        no_for_vars = True

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
                if isinstance(collection_node, xy.Select):
                    gen = xy.FuncCall(
                        xy.Id("iter"),
                        [collection_node.base, *collection_node.args.args],
                        collection_node.args.kwargs,
                        src=collection_node.src, coords=collection_node.coords
                    )
                    ictor_obj = compile_fcall(gen, cast, cfunc, ctx)
                else:
                    collection_obj = compile_expr(collection_node, cast, for_outer_block if for_outer_block else cfunc, ctx, deref=False)
                    iter_arg_objs = []
                    if collection_obj.is_iter_ctor:
                        ictor_obj = collection_obj
                    else:
                        collection_obj = maybe_move_to_temp(collection_obj, cast, cfunc, ctx)
                        iter_arg_objs = [collection_obj]
                        ictor_obj = find_and_call("iter", ArgList(iter_arg_objs), cast, cfunc, ctx, collection_node)

                if not isinstance(ictor_obj, IdxObj):
                    raise CompilationError("Iter Ctors must return refs", ictor_obj.xy_node)
                original_ref = ictor_obj
                iter_arg_objs = [ictor_obj.container]
                if ictor_obj.container is global_memory:
                    iter_arg_objs = []
                ictor_obj = ictor_obj.idx

                # init
                iter_var_decl = ctx.create_tmp_var(ictor_obj.inferred_type, "iter")
                iter_var_decl.c_node.value = ictor_obj.c_node
                iter_obj = ExprObj(
                    xy_node=collection_node,
                    c_node=c.Id(iter_var_decl.c_node.name),
                    inferred_type=iter_var_decl.type_desc
                )
                ctx.ns[iter_var_decl.c_node.name] = iter_var_decl
                if for_outer_block is None and iter_var_decl.needs_dtor:
                    for_outer_block = c.Block()
                    no_for_vars = True

                if no_for_vars:
                    for_outer_block.body.append(iter_var_decl.c_node)
                else:
                    cfor.inits.append(iter_var_decl.c_node)

                # compile condition
                valid_obj = find_and_call("valid", ArgList([*iter_arg_objs, iter_obj]), cast, cfunc, ctx, collection_node)
                if cfor.cond is None:
                    cfor.cond = valid_obj.c_node
                else:
                    cfor.cond = c.Expr(cfor.cond, valid_obj.c_node, op="&&")

                # compile step
                next_obj = find_and_call("next", ArgList([*iter_arg_objs, iter_obj]), cast, cfunc, ctx, collection_node)
                cfor.updates.append(next_obj.c_node)

                # deref in for body
                # deidx_obj = find_and_call("get", ArgList([*iter_arg_objs, iter_obj]), cast, cfunc, ctx, collection_node)

                # val_cdecl = c.VarDecl(iter_name, c.QualType(deidx_obj.inferred_type.c_node.name), value=deidx_obj.c_node)
                # val_obj = VarObj(collection_node, val_cdecl, deidx_obj.inferred_type)
                # ctx.ns[iter_name] = val_obj
                # cfor.body.append(val_cdecl)

                new_ref = copy(original_ref)
                new_ref.c_node = None
                new_ref.idx = iter_obj
                idx_setup(new_ref, cast, cfunc, ctx)
                ctx.ns[iter_name] = new_ref
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

    ctx.push_ns()
    if for_node.block.is_embedded:
        update_expr = compile_expr(for_node.block.body, cast, cfor, ctx)
        cfor.body.append(update_expr.c_node)
    else:
        compile_body(for_node.block.body, cast, cfor, ctx)
    ctx.pop_ns() # for the body

    if len(return_objs) > 0:
        cfunc.body.append(cfor if for_outer_block is None else for_outer_block)

    call_dtors(ctx.ns, cast, cfunc if for_outer_block is None else for_outer_block, ctx)
    ctx.pop_ns() # for the loop

    if len(return_objs) > 0:
        c_res = c.Id(return_objs[0].c_node.name)
    elif for_outer_block is not None:
        c_res = for_outer_block
    else:
        c_res = cfor

    return ExprObj(
        xy_node=for_node,
        c_node=c_res,
        inferred_type=inferred_type,
    )

def is_iter_ctor_call(expr_obj: ExprObj):
    if isinstance(expr_obj, FuncObj):
        return "xyIter" in expr_obj.tags
    return False

def compile_break(xybreak, cast, cfunc, ctx):
    if xybreak.loop_name is not None:
        raise CompilationError("Breaking the outer loop is NYI", xybreak)

    for ns in reversed(ctx.data_namespaces):
        call_dtors(ns, cast, cfunc, ctx)
        if ns.data.type is NamespaceType.Loop:
            break

    return ExprObj(
        xy_node=xybreak,
        c_node=c.Break(),
        inferred_type=ctx.void_obj,
    )

def compile_continue(xycont, cast, cfunc, ctx):
    if xycont.loop_name:
        target_loop_name = ctx.eval_to_id(xycont.loop_name)
    else:
        target_loop_name = None

    df = None
    for ns in reversed(ctx.data_namespaces):
        call_dtors(ns, cast, cfunc, ctx)
        if ns.data.type is NamespaceType.Loop and target_loop_name == ns.data.loop_name:
            df = ns
            break

    if df is None:
        raise CompilationError("Continue outside of a loop is not permited", xycont)

    if df.data.continue_label_name is not None:
        c_res = c.Goto(c.Id(df.data.continue_label_name))
        df.data.label_used = True
    else:
        c_res = c.Continue()

    return ExprObj(
        xy_node=xycont,
        c_node=c_res,
        inferred_type=ctx.void_obj,
    )

def return_by_param(xy_func):
    return xy_func.etype is not None or len(xy_func.returns) > 1

def compile_return(xyreturn, cast, cfunc, ctx: CompilerContext):
    xy_func = ctx.current_fobj.xy_node
    if not return_by_param(xy_func):
        ret = c.Return()
        value_obj = None
        needs_dtor = False
        if xyreturn.value:
            value_obj = compile_expr(xyreturn.value, cast, cfunc, ctx)
            if isinstance(value_obj.compiled_obj, VarObj):
                # Don't destory the value we return
                needs_dtor = value_obj.compiled_obj.needs_dtor
                value_obj.compiled_obj.needs_dtor = False
            elif any_dtors(ctx):
                tmp_obj = ctx.create_tmp_var(value_obj.inferred_type, "res")
                tmp_obj.c_node.value = value_obj.c_node
                tmp_obj.needs_dtor = False
                cfunc.body.append(tmp_obj.c_node)
                value_obj = ExprObj(
                    xy_node=value_obj.xy_node,
                    c_node=c.Id(tmp_obj.c_node.name),
                    inferred_type=value_obj.inferred_type,
                )
                # it's a temporary value on the stack. So we need to copy it
            ret.value = value_obj.c_node

        call_all_dtors(cast, cfunc, ctx)
        if value_obj is not None and isinstance(value_obj.compiled_obj, VarObj):
            # restore value of needs_dtor for any other returns
            value_obj.compiled_obj.needs_dtor = needs_dtor

        if value_obj is not None:
            assert_rtype_match(value_obj, ctx.current_fobj, ctx)

        return ExprObj(
            xy_node=xyreturn,
            c_node=ret,
            inferred_type=value_obj.inferred_type if value_obj is not None else ctx.void_obj
        )
    else:
        # return by param(s)
        for iret, ret in enumerate(xy_func.returns):
            value_obj = compile_expr(xyreturn.value, cast, cfunc, ctx)
            if isinstance(value_obj.compiled_obj, VarObj):
                value_obj.compiled_obj.needs_dtor = False
            param_name = f"__{ret.name}" if ret.name else f"_res{iret}"
            cfunc.body.append(c.Expr(
                arg1=c.UnaryExpr(op="*", arg=c.Id(param_name), prefix=True),
                arg2=value_obj.c_node,
                op="="
            ))
            assert_rtype_match(value_obj, ctx.current_fobj, ctx)
        ret = c.Return()
        if xy_func.etype is not None:
            ret.value = ctx.current_fobj.etype_obj.init_value
        call_all_dtors(cast, cfunc, ctx)
        return ExprObj(
            xy_node=xyreturn,
            c_node=ret,
            inferred_type=None
        )

def assert_rtype_match(value_obj, fobj, ctx: CompilerContext):
    c_expr = isinstance(value_obj.inferred_type, TypeInferenceError) or value_obj.inferred_type is None
    if not c_expr and not compatible_types(value_obj.inferred_type, fobj.rtype_obj):
        if implicit_zero_conversion(value_obj, fobj.rtype_obj, ctx):
            return
        return_type_node = fobj.xy_node.returns[0] if len(fobj.xy_node.returns) else fobj.xy_node
        raise CompilationError(
            f"Return type mismatch. Tyring to return '{fmt_type(value_obj.inferred_type)}'", value_obj.xy_node,
            notes=[
                (f"From function returning '{fmt_type(fobj.rtype_obj)}'", return_type_node)
            ]
        )

def implicit_zero_conversion(value_obj, dest_type, ctx: CompilerContext):
    return (
        isinstance(value_obj.xy_node, xy.Const) and value_obj.xy_node.value == 0
        and value_obj.xy_node.type == "Int" and (ctx.is_prim_int(dest_type) or is_ptr_type(dest_type, ctx))
    )


def compile_error(xyerror, cast, cfunc, ctx: CompilerContext):
    assert xyerror.value is not None
    value_obj = compile_expr(xyerror.value, cast, cfunc, ctx)

    if ctx.current_fobj.etype_obj is None or \
        ctx.current_fobj.etype_obj is not value_obj.inferred_type:
        # error in function not returing an error
        value_obj = maybe_move_to_temp(value_obj, cast, cfunc, ctx)
        do_compile_unhandled_code(xyerror, value_obj, cast, cfunc, ctx, ctx, ctx.current_fobj)
        return ExprObj(
            xy_node=xyerror,
            c_node=c.Empty(),
            inferred_type=value_obj.inferred_type
        )

    # normal error
    ret = c.Return()
    ret.value = value_obj.c_node
    return ExprObj(
        xy_node=xyerror,
        c_node=ret,
        inferred_type=value_obj.inferred_type
    )

def do_compile_unhandled_code(expr, err_obj, cast, cfunc, caller_ctx, callee_ctx, func_obj):
    unhandled_args = ArgList(args=[err_obj])
    unhandled_ctx = caller_ctx
    unhandled_fobj = maybe_find_func_obj(
        "unhandled", unhandled_args, cast, cfunc, unhandled_ctx, expr
    )
    if unhandled_fobj is None and callee_ctx is not None:
        unhandled_ctx = callee_ctx
        unhandled_fobj = maybe_find_func_obj(
            "unhandled", unhandled_args, cast, cfunc, callee_ctx, expr
        )
    if unhandled_fobj is not None:
        unhandled_call_obj = do_compile_fcall(expr, unhandled_fobj, unhandled_args, cast, cfunc, unhandled_ctx)
        cfunc.body.append(unhandled_call_obj.c_node)
    elif not caller_ctx.builder.abort_on_unhandled:
        # uncaught error
        cast.includes.append(c.Include("stdio.h"))  # TODO remove that just use write(2)

        cfunc.body.append(c.FuncCall("fprintf", args=[c.Id("stderr"), c.Const(f"\"\\n\"")]))
        gen_print_var("Error", err_obj, cast, cfunc, unhandled_ctx, ident=0, endl=False)
        gen_guard_failed_code(expr, func_obj, cast, cfunc.body, callee_ctx, False)
        gen_print_params_code(cast, cfunc, callee_ctx)

    if not caller_ctx.stdlib_included:
        cast.includes.append(c.Include("stdlib.h"))
        caller_ctx.stdlib_included = True

    if caller_ctx.builder.abort_on_unhandled:
        cfunc.body.append(c.FuncCall("abort"))
    else:
        cfunc.body.append(c.FuncCall("exit", args=[c.Const(200)]))

def get_c_type(type_expr, cast, ctx):
    id_desc = find_type(type_expr, cast, ctx, required=True)
    return id_desc.c_name

def mangle_def(fdef: xy.FuncDef, param_objs: list[VarObj], ctx, expand=False):
    mangled = mangle_name(fdef.name.name, ctx.module_name)
    if expand:
        mangled = [mangled]
        for param_obj in param_objs:
            mangled.append("__")
            if isinstance(param_obj.type_desc.xy_node, xy.ArrayType):
                if len(param_obj.type_desc.xy_node.dims) > 0:
                    dim = param_obj.type_desc.xy_node.dims[0].value_str
                else:
                    dim = "0"
                mangled.append(dim)
                mangled.append(param_obj.type_desc.xy_node.base.name)
            else:
                mangled.append(param_obj.type_desc.name)
        mangled = "".join(mangled)
    return mangled

def mangle_fptr(param_objs: list[VarObj], rtype_obj: TypeObj, ctx):
    mangled = ["xy_fp"]
    for param_obj in param_objs:
        mangled.append("__")
        do_mangle_type_obj(mangled, param_obj.type_desc)
    mangled.append("__")
    do_mangle_type_obj(mangled, rtype_obj)

    mangled = "".join(mangled)
    return mangled

def create_fptr_type(param_objs: list[VarObj], rtype_obj: TypeObj, cast, ctx: CompilerContext):
    # TODO remove that func. It doesn't handle etypes
    c_typename = mangle_fptr(param_objs, rtype_obj, ctx)
    if c_typename not in ctx.defined_c_symbols:
        ctx.defined_c_symbols.add(c_typename)
        param_types = ', '.join(p.type_desc.c_name for p in param_objs)
        if len(param_types) == 0:
            param_types = "void"
        c_typedef = c.Typedef(
            f"{rtype_obj.c_name} (*{c_typename})({param_types})",
            "",
            unique_name=c_typename
        )
        cast.type_decls.append(c_typedef)
    return c_typename

def do_mangle_type_obj(mangled, type_desc):
    if isinstance(type_desc.xy_node, xy.ArrayType):
        if len(type_desc.xy_node.dims) > 0:
            dim = type_desc.xy_node.dims[0].value_str
        else:
            dim = "0"
        mangled.append(dim)
        mangled.append(type_desc.xy_node.base.name)
    else:
        mangled.append(type_desc.xy_node.name)

def mangle_field(field: xy.VarDecl):
    # mangle in order to prevent duplication with macros
    return f"m_{field.name}"

def mangle_struct(struct: xy.StructDef, ctx):
    return mangle_name(struct.name, ctx.module_name)

def mangle_define(name: str, module_name: str):
    return mangle_name(name, module_name).upper()

def mangle_name(name: str, module_name: str):
    return module_name.replace(".", "_") + "_" + name

def mangle_type_id(type_obj: TypeExprObj):
    return "XY_" + type_obj.c_node.name.upper() + "__ID"


class CompilationError(Exception):
    def __init__(self, msg, node, notes=None):
        self.notes = notes
        self.error_message = msg
        self.xy_node = node
        self.fmt_msg = fmt_err_msg(f"error: {msg}", node)

        if notes is not None and len(notes) > 0:
            self.fmt_msg += "".join(
                fmt_err_msg(f"note: {n[0]}", n[1]) for n in notes
            )


    def __str__(self):
        return self.fmt_msg

def fmt_err_msg(msg, node):
    if node is None:
        return msg + "\n"
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
    fmt_msg = f"{fn}:{line_num}:{loc - line_loc + 1}: {msg}\n"
    if loc >= 0:
        fmt_msg += f"| {src_line}\n"
        fmt_msg += "  " + (" " * (loc-line_loc)) + ("^" * loc_len) + "\n"
    return fmt_msg

def find_type(texpr, cast, ctx, required=True):
    if isinstance(texpr, xy.Id) and texpr.name == "struct":
        # Special case for struct
        return any_struct_type_obj
    elif isinstance(texpr, xy.Id) and texpr.name == "Any":
        # Special case for ?
        return any_type_obj
    elif isinstance(texpr, xy.Id):
        validate_name(texpr, ctx)
        res = ctx.eval(texpr, msg="Cannot find type")
        if isinstance(res, ExtSymbolObj):
            res = ext_symbol_to_type(res)
        return res
    elif isinstance(texpr, xy.ArrayType):
        base_type = find_type(texpr.base, cast, ctx)
        dims = []
        for d in texpr.dims:
            dims.append(ct_eval(d, ctx))
        return ArrTypeObj(xy_node=texpr, base_type_obj=base_type, dims=dims)
    elif isinstance(texpr, xy.FuncType):
        ctx.push_ns()
        c_func = c.Func("dummy")
        param_objs, _ = compile_params(texpr.params, cast, c_func, ctx)
        rtype_obj, etype_obj, _, _ = compile_ret_err_types(texpr, cast, c_func, ctx)
        ctx.pop_ns()

        c_typename = create_fptr_type(param_objs, rtype_obj, cast, ctx)
        return FuncTypeObj(
            c_typename=c_typename, xy_node=texpr,
            func_obj=FuncObj(
                param_objs=param_objs,
                rtype_obj=rtype_obj,
                etype_obj=etype_obj,
                move_args_to_temps=True,
                params_compiled = True,
                prototype_compiled = True,
                decl_visible = True,
            )
        )
    else:
        res = ctx.eval(texpr, msg="Cannot find type")
        if isinstance(res, ExtSymbolObj):
            res = ext_symbol_to_type(res)
        return res

def ct_eval(expr, ctx):
    if isinstance(expr, xy.Const):
        return expr.value
    raise CompilationError("Cannot Compile-Time Evaluate", expr)

def find_func(fcall, ctx):
    fspace = ctx.eval_to_fspace(fcall.name)
    return fspace.find(fcall, ctx)

def compile_binop(binexpr, cast, cfunc, ctx):
    fcall = rewrite_op(binexpr, ctx)
    return compile_expr(fcall, cast, cfunc, ctx)

operatorToFname = fname = {
    "+": "add",
    "-": "sub",
    "*": "mul",
    "/": "div",
    "||": "or",
    "&&": "and",
    "==": "cmpEq",
    "!=": "cmpNe",
    ">": "cmpGt",
    ">=": "cmpGe",
    "<": "cmpLt",
    "<=": "cmpLe",
}
def rewrite_op(binexpr, ctx):
    fname = operatorToFname.get(binexpr.op, None)
    if fname is not None:
        return xy.FuncCall(
            xy.Id(fname, src=binexpr.src, coords=binexpr.coords),
            args=[binexpr.arg1, binexpr.arg2],
            src=binexpr.src, coords=binexpr.coords)
    else:
        raise CompilationError(f"Unrecognized operator '{binexpr.op}'", binexpr)

def rewrite_unaryop(expr: xy.UnaryExpr, ctx):
    if expr.op == "++":
        fname = "inc"
    elif expr.op == "--":
        fname = "dec"
    elif expr.op == "!":
        fname = "not"
    elif expr.op == "-":
        return xy.BinExpr(
            arg1=xy.StructLiteral(
                name=xy.UnaryExpr(expr.arg, op="%", src=expr.src, coords=expr.coords),
                src=expr.src, coords=expr.coords
            ),
            arg2=expr.arg,
            op="-",
            src=expr.src, coords=expr.coords
        )
    else:
        raise CompilationError(f"Unrecognized operator '{expr.op}'", expr)
    return xy.FuncCall(
        xy.Id(fname, src=expr.src, coords=expr.coords),
        args=[expr.arg],
        src=expr.src, coords=expr.coords
    )

# def rewrite_select(select, ctx):
#     args = []
#     if select.base is not None:
#         args = [select.base]
#     args.extend(select.args.args)

#     fcall = xy.FuncCall(
#         xy.Id("get"), args=args,
#         kwargs=select.args.kwargs,
#         src=select.src,
#         coords=select.coords
#     )
#     return fcall

def compile_select(expr: xy.Select, cast, cfunc, ctx):
    if expr.base is not None:
        container_obj = compile_expr(expr.base, cast, cfunc, ctx, deref=False)
    else:
        container_obj = global_memory
    if len(expr.args.args) != 1:
        # TODO
        raise CompilationError("More than one arg in a [] expr is NYI", expr)
    assert len(expr.args.kwargs) == 0  # TODO
    idx_obj = compile_expr(expr.args.args[0], cast, cfunc, ctx, deref=False)

    idx_obj = IdxObj(xy_node=expr, container=container_obj, idx=idx_obj)
    idx_setup(idx_obj, cast, cfunc, ctx)
    return idx_obj

def compile_import(imprt, ctx: CompilerContext, ast, cast):
    compiled_tags = ctx.eval_tags(imprt.tags)
    import_obj = ImportObj(name=imprt.lib)
    if "xyc.lib" in compiled_tags:
        obj = compiled_tags["xyc.lib"]
        # TODO assert obj.xy_node.name.name == "Clib"
        headers = obj.kwargs.get("headers", ArrayObj())
        for header_obj in headers.elems:
            # TODO what if header_obj is an expression
            if len(header_obj.prefix) > 0:
                raise CompilationError("Only unprefixed strings are recognized", header_obj.xy_node)
            cast.includes.append(c.Include(header_obj.parts[0].value))

        defines = obj.kwargs.get("defines", ArrayObj())
        for def_obj in defines.elems:
            if len(def_obj.parts) == 0:
                raise CompilationError("Empty define", def_obj.xy_node)
            code: str = def_obj.parts[0].value
            if len(code.strip()) == 0:
                raise CompilationError("Empty define", def_obj.xy_node)
            name_idx = code.find("=")
            if name_idx > 0:
                code = code[0:name_idx] + " " + code[name_idx+1:]
            cast.defines.append(c.Define(code))
        import_obj.is_external = True
    else:
        if imprt.lib in ctx.imported_modules:
            # already imported nothing to do
            return
        ctx.imported_modules.add(imprt.lib)
        module_header = ctx.builder.import_module(imprt.lib, imprt)
        if module_header is None:
            raise CompilationError(f"Cannot find module '{imprt.lib}'", imprt)
        import_obj.module_header = module_header
        if imprt.in_name is None:
            ctx.global_data_ns.merge(module_header.data_namespace, ctx, module_header.module_name)
            ctx.global_func_ns.merge(module_header.func_namespace, ctx, module_header.module_name)
            for str_prefix, ctor_obj in module_header.str_prefix_reg.items():
                # str ctors are not sticky
                if ctor_obj.module_header.module_name == module_header.module_name:
                    ctx.str_prefix_reg[str_prefix] = ctor_obj
            for str_prefix, ctor_obj in module_header.unstr_prefix_reg.items():
                # str ctors are not sticky
                if ctor_obj.module_header.module_name == module_header.module_name:
                    ctx.unstr_prefix_reg[str_prefix] = ctor_obj

    if imprt.in_name:
        ctx.data_ns[imprt.in_name] = import_obj

def assert_has_type(obj: ExprObj):
    if obj.inferred_type is None:
        raise CompilationError("Cannot determine type of expression", obj.xy_node)
    if isinstance(obj.inferred_type, TypeInferenceError):
        raise CompilationError(obj.inferred_type.msg, obj.xy_node)

def maybe_add_main(ctx: CompilerContext, cast, has_global=False, uses_sys=False):
    if ctx.entrypoint_obj is not None:
        main = c.Func(
            name="main", rtype="int",
            params=[
                c.VarDecl("argc", c.QualType("int",)),
                c.VarDecl("argv", c.QualType("char**"))
            ], body=[]
        )
        if has_global:
            main.body.append(c.FuncCall("xy_global_init", args=[
                c.UnaryExpr(c.Id("g__xy_globalInstance"), op="&", prefix=True),
                c.UnaryExpr(c.Id("g__xy_globalInitData"), op="&", prefix=True),
            ]))
            main.body.append(c.Expr(
                c.Id("g__xy_global"),
                c.UnaryExpr(c.Id("g__xy_globalInstance"), op="&", prefix=True),
                op="="),
            )
        if has_global and uses_sys:
            main.body.append(
                c.InlineCode("((xy_sys_CmdArgs*)g__xy_global->stack[XY_XY_SYS_CMDARGS__ID])->m_argc = argc;")
            )
            main.body.append(
                c.InlineCode("((xy_sys_CmdArgs*)g__xy_global->stack[XY_XY_SYS_CMDARGS__ID])->m_argv = argv;")
            )

        ctx.current_fobj = FuncObj(
            xy_node=ctx.entrypoint_obj.xy_node,
            c_node=main,
            rtype_obj=ctx.int_obj,
            etype_obj=ctx.int_obj,
            prototype_compiled=True,
            params_compiled=True,
        )

        fcall_obj = do_compile_fcall(
            ctx.entrypoint_obj.xy_node, ctx.entrypoint_obj, ArgList(),
            cast, main, ctx
        )
        if fcall_obj.c_node is not None:
            main.body.append(fcall_obj.c_node)
        main.body.append(c.Return(c.Const(0)))

        cast.funcs.append(main)

def gen_global_stack(global_type_reg, cast: c.Ast):
    initDataStruct = c.Struct("xy_GlobalInitData")

    for i, type_obj in enumerate(global_type_reg.values()):
        cdef = c.Define("XY_" + type_obj.c_name.upper() + "__ID", value=c.Const(i))
        cast.consts.append(cdef)

        initDataStruct.fields.append(
            c.VarDecl(f"field{i}", qtype=c.QualType(c.Type(type_obj.c_name)))
        )

    cast.type_decls.append(c.Typedef("struct " + initDataStruct.name, initDataStruct.name))
    cast.structs.append(initDataStruct)

    xyGlobalStruct = c.Struct(
        "xy_Global",
        fields=[
            c.VarDecl("stack", c.QualType(c.Type("void*", dims=[len(global_type_reg)])))
        ]
    )
    cast.structs.append(xyGlobalStruct)
    cast.type_decls.append(c.Typedef("struct " + xyGlobalStruct.name, xyGlobalStruct.name))

    cast.globals.append(c.VarDecl(
       "g__xy_globalInitData", c.QualType(c.Type("xy_GlobalInitData"), is_const=False, is_threadLocal=True),
       value=c.InitList([
           type_obj.init_value for type_obj in global_type_reg.values()
       ])
    ))
    cast.globals.append(c.VarDecl(
        "g__xy_globalInstance", c.QualType(c.Type("xy_Global"), is_const=False, is_threadLocal=True)
    ))
    cast.globals.append(c.VarDecl(
        "g__xy_global", c.QualType(c.Type("xy_Global*"), is_const=False, is_threadLocal=True)
    ))

    init_func = c.Func(
        "xy_global_init", rtype="void",
        params=[
            c.VarDecl("global", c.QualType(c.Type("xy_Global*"))),
            c.VarDecl("data", c.QualType(c.Type("xy_GlobalInitData*")))
        ], body=[
            c.Expr(
                c.Index(c.Expr(c.Id("global"), c.Id("stack"), op="->"), c.Const(i)),
                c.UnaryExpr(
                    c.Expr(c.Id("data"), c.Id(f"field{i}"), op="->"),
                    op="&", prefix=True,
                ),
                op="=",
            )
            for i in range(len(global_type_reg))
        ]
    )
    cast.funcs.append(init_func)
    cast.func_decls.append(init_func)

def fmt_comment(comment):
    if len(comment) < 2:
        return comment
    if comment[:2] != ";;":
        return comment
    i = 2
    leading_blanks = 0
    while i < len(comment) and comment[i].isspace():
        i += 1
        leading_blanks += 1

    res = ""
    i = 2 + leading_blanks
    while i < len(comment):
        if comment[i] == "\n":
            res += "\\n"
            i += 1
            while i < len(comment) and comment[i].isspace():
                i += 1
        elif comment[i:i+2] == ";;":
            i += 2
            for _ in range(leading_blanks):
                if i < len(comment) and comment[i].isspace():
                    i += 1
        else:
            res += comment[i]
            i += 1
    return res