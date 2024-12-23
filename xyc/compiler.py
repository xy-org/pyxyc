import os
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
    builtin : bool = False
    fields: dict[str, 'VarObj'] = field(default_factory=list)
    init_value: any = None

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None
    
@dataclass
class TypeInferenceError:
    msg: str = ""

@dataclass
class ConstObj(CompiledObj):
    value: int | float | str | None = None

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
class ArrTypeObj(CompiledObj):
    base : CompiledObj | None = None
    dims : list = field(default_factory=list)

    @property
    def c_name(self):
        self.base.c_name + "*"

@dataclass
class ArrayObj(CompiledObj):
    elems: list[CompiledObj] = field(default_factory=list)

@dataclass
class InstanceObj(CompiledObj):
    type_obj: CompiledObj | None = None
    fields: dict[str, CompiledObj] = field(default_factory=dict)

@dataclass
class FuncObj(CompiledObj):
    rtype_obj: TypeObj = None
    etype_obj: TypeObj = None
    builtin: bool = False

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None

@dataclass
class VarObj(CompiledObj):
    type_desc: TypeObj | None = None

@dataclass
class ImportObj(CompiledObj):
    name: str | None = None
    is_external: bool = True  # XXX

@dataclass
class ExprObj(CompiledObj):
    infered_type: CompiledObj | str = "Cannot deduce type"

class IdTable(dict):
    def merge(self, other: 'IdTable'):
        for key, value in other.items():
            current = self.get(key, None)
            if current is None:
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

    def __len__(self):
        return len(self._funcs)
    
    def append(self, fdesc: FuncObj):
        self._funcs.append(fdesc)

    def __getitem__(self, i):
        return self._funcs[i]
    
    def find(self, node, args_infered_types, ctx):
        if isinstance(node, xy.FuncCall):
            for desc in self._funcs:
                if cmp_call_def(node, args_infered_types, desc.xy_node, ctx):
                    return desc
            fsig = ctx.eval_to_id(node.name) + "(" + \
                ", ".join(t.xy_node.name for t in args_infered_types) + \
                ")"
            candidates = "\n    ".join((
                func_sig(f.xy_node) for f in self._funcs
            ))
            raise CompilationError(
                f"Cannot find function '{fsig}'", node,
                notes=[(f"Candidates are:\n    {candidates}", None)]
            )
        else:
            assert isinstance(node, xy.FuncDef)
            for desc in self._funcs:
                if desc.xy_node == node:
                    return desc
            raise "Cannot find func"
        
class ExtSpace(FuncSpace):
    def __init__(self, ext_name: str):
        self.ext_name = ext_name

    def find(self, node, args_infered_types, ctx):
        return FuncObj(c_node=c.Func(name=self.ext_name, rtype=None))


def cmp_call_def(fcall, fcall_args_types, fdef, ctx):
    # TODO what about kwargs
    if len(fcall.args) != len(fdef.params):
        return False
    for arg_type, param in zip(fcall_args_types, fdef.params):
        # XXX
        if isinstance(arg_type, ArrTypeObj):
            continue
        if arg_type.xy_node.name != param.type.name:
            return False
    return True

def func_sig(fdef):
    name = fdef.name if isinstance(fdef.name, str) else fdef.name.name
    res = name + "(" + ", ".join(p.type.name for p in fdef.params) + ")"
    res += " -> "
    if len(fdef.returns) > 1:
        res += "("
    res += ",".join(r.type.name for r in fdef.returns)
    if len(fdef.returns) > 1:
        res += ")"
    return res

@dataclass
class ModuleHeader:
    namespace: IdTable
    str_prefix_reg: dict[str, any] = field(default_factory=dict)

@dataclass
class CompilerContext:
    builder: any
    module_name: str  # TODO maybe module_name should be a list of the module names
    id_table: IdTable = field(default_factory=IdTable)
    global_ns: IdTable = field(default_factory=IdTable)
    str_prefix_reg: dict[str, any] = field(default_factory=dict)

    current_fobj: FuncObj | None = None
    tmp_var_i: int = 0

    entrypoint_obj: any = None
    void_obj: any = None

    def ensure_func_space(self, name: xy.Id):
        if name.name not in self.id_table:
            fspace = FuncSpace()
            self.id_table[name.name] = fspace
            return fspace
        candidate = self.id_table[name.name]
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
        res = self.id_table.get(symbol_name, None)
        if res is None:
            res = self.global_ns.get(symbol_name, None)

        if res is not None:
            return res
        raise CompilationError(f"Cannot find type '{name.name}'", name)
    
    def eval_tags(self, tags: xy.TagList):
        res = {}
        for xy_tag in tags.args:
            tag_obj = self.eval(xy_tag)
            if isinstance(tag_obj, TypeObj):
                if "xy.tag" not in tag_obj.tags:
                    raise CompilationError(
                        f"Missing default label for type '{tag_obj.xy_node.name}'",
                        xy_tag, notes=[("Please associate default label by adding the TagCtor tag: ~[TagCtor{label=\"default-label\"}]", None)])
                label = tag_obj.tags["xy.tag"].fields["label"].as_str()
            elif isinstance(tag_obj, InstanceObj):
                assert tag_obj.type_obj is not None
                if "xy.tag" not in tag_obj.type_obj.tags:
                    raise CompilationError(
                        f"Missing default label for type '{tag_obj.type_obj.xy_node.name}'",
                        xy_tag, notes=[("Please associate default label by adding the TagCtor tag: ~[TagCtor{label=\"default-label\"}]", None)])
                label = tag_obj.type_obj.tags["xy.tag"].fields["label"].as_str()
            elif tag_obj.primitive:
                raise CompilationError("Primitive types have to have an explicit label", xy_tag)
            else:
                raise CompilationError("Cannot determine label for tag", xy_tag)
            
            if label in res:
                raise CompilationError(f"Label '{label}' already filled by tag", res[label].xy_node)
            res[label] = tag_obj
        return res

    def lookup(self, name: str):
        if name in self.id_table:
            return self.id_table[name]
        else:
            return self.global_ns.get(name, None)

    def eval(self, node):
        if isinstance(node, xy.Id):
            return self.lookup(node.name)
        elif isinstance(node, xy.Const):
            return ConstObj(value=node.value, xy_node=node)
        elif isinstance(node, xy.StrLiteral):
            return StrObj(
                prefix=node.prefix,
                parts=[self.eval(p) for p in node.parts],
                xy_node=node
            )
        elif isinstance(node, xy.StructLiteral):
            instance_type = self.eval(node.name)
            obj = InstanceObj(type_obj=instance_type, xy_node=node)
            if len(node.args) > 0:
                raise CompilationError("Positional arguments are NYI", node.args[0])
            for name, value in node.kwargs.items():
                obj.fields[name] = self.eval(value)
            return obj
        elif isinstance(node, xy.ArrayLit):
            return ArrayObj(elems=[self.eval(elem) for elem in node.elems], xy_node=node)
        elif isinstance(node, xy.BinExpr):
            if node.op == ".":
                base = self.eval(node.arg1)
                assert isinstance(node.arg2, xy.Id)
                if not isinstance(base, ImportObj):
                    raise CompilationError("Selection is NYI")
                # XXX assume c library
                return ExtSpace(node.arg2.name)
        else:
            import pdb; pdb.set_trace()
            raise CompilationError(
                "Cannot evaluate at compile time. "
                f"Unknown expression type '{type(node).__name__}'",
                node)
        
    def create_tmp_var(self, type_obj, name_hint=""):
        tmp_var_name = f"__tmp{'_' if name_hint else ''}{name_hint}"
        tmp_var_name = f"{tmp_var_name}{self.tmp_var_i}"
        self.tmp_var_i += 1

        # TODO rewrite expression and call other func
        c_tmp = c.VarDecl(name=tmp_var_name, type=None, is_const=True)
        if isinstance(type_obj, ArrTypeObj):
            c_tmp.type = type_obj.base.c_name
            c_tmp.dims = type_obj.dims
        else:
            c_tmp.type = type_obj.c_name

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

    compile_header(ctx, asts, res)
    
    for ast in asts:
        compile_funcs(ctx, ast, res)
    
    maybe_add_main(ctx, res)

    return ModuleHeader(
        namespace=ctx.id_table, str_prefix_reg=ctx.str_prefix_reg
    ), res

def compile_header(ctx: CompilerContext, asts, cast):
    import_builtins(ctx, cast)

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.Import):
                compile_import(node, ctx, ast, cast)

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.StructDef):
                cstruct = c.Struct(name=mangle_struct(node, ctx))
                type_obj = TypeObj(
                    xy_node = node,
                    c_node = cstruct,
                )
                ctx.id_table[node.name] = type_obj

                fields = {}
                for field in node.fields:
                    field_type_obj = find_type(field.type, ctx)
                    cfield = c.VarDecl(
                        name=mangle_field(field),
                        type=field_type_obj.c_name
                    )
                    fields[field.name] = VarObj(
                        xy_node=field,
                        c_node=cfield,
                        type_desc=field_type_obj,
                    )
                    cstruct.fields.append(cfield)
                type_obj.fields = fields
                type_obj.init_value = c.StructLiteral(
                    name=cstruct.name,
                    args=[
                        c.Const(0)
                    ]
                ) # TODO what about non zero fields

                cast.struct_decls.append(cstruct)
                cast.structs.append(cstruct)

    for ast in asts:
        for node in ast:
            if isinstance(node, xy.FuncDef):
                func_space = ctx.ensure_func_space(node.name)
                expand_name = len(func_space) > 0
                if len(func_space) == 1:
                    # Already present. Expand name.
                    func_desc = func_space[0]
                    func_desc.c_node.name = mangle_def(
                        func_desc.xy_node, ctx, expand=True
                    )
                
                cname = mangle_def(node, ctx, expand=expand_name)
                cfunc = c.Func(name=cname)
                for param in node.params:
                    if not param.is_pseudo:
                        cparam = c.VarDecl(param.name, get_c_type(param.type, ctx))
                        cfunc.params.append(cparam)

                etype_compiled = None
                if len(node.returns) > 1 or node.etype is not None:
                    # return through parameter
                    for iret, ret in enumerate(node.returns):
                        if ctx.eval(ret.type) is ctx.void_obj:
                            rtype_compiled = ctx.void_obj
                            assert len(node.returns) == 1
                            continue
                        param_name = f"__{ret.name}" if ret.name else f"_res{iret}"
                        retparam = c.VarDecl(param_name, get_c_type(ret.type, ctx) + "*")
                        cfunc.params.append(retparam)
                        rtype_compiled = ctx.get_compiled_type(ret.type)
                    if node.etype is not None:
                        etype_compiled = ctx.get_compiled_type(node.etype)
                elif len(node.returns) == 1:
                    rtype_compiled = ctx.get_compiled_type(node.returns[0].type)
                else:
                    rtype_compiled = ctx.void_obj

                cfunc.rtype = (etype_compiled.c_name
                               if etype_compiled is not None
                               else rtype_compiled.c_name)

                cast.func_decls.append(cfunc)
                compiled = FuncObj(node, cfunc, rtype_obj=rtype_compiled, etype_obj=etype_compiled)

                if node.etype is not None:
                    compiled.etype_obj = ctx.get_compiled_type(node.etype)

                # compile tags
                compiled.tags = ctx.eval_tags(node.tags)
                if "xy.string" in compiled.tags:
                    # TODO assert it is a StrCtor indeed
                    str_lit = compiled.tags["xy.string"].fields["prefix"]
                    prefix = str_lit.parts[0].value if len(str_lit.parts) else ""
                    ctx.str_prefix_reg[prefix] = compiled
                if "xy.entrypoint" in compiled.tags:
                    # TODO assert it is the correct type
                    ctx.entrypoint_obj = compiled

                func_space.append(compiled)

    return cast

def import_builtins(ctx: CompilerContext, cast):
    # always include it as it is everywhere
    cast.includes.append(c.Include("stdint.h"))
    cast.includes.append(c.Include("stddef.h"))
    cast.includes.append(c.Include("stdbool.h"))

    int_types = [
       "int", "uint",
       "long", "ulong",
       "Size", 
    ]
    num_types = [
       *int_types,
       "float", "double"
    ]

    ctype_map = {
        "int": "int32_t", "uint": "uint32_t",
        "long": "int64_t", "ulong": "uint64_t",
        "Size": "size_t",
        "float": "float", "double": "double",
        "Ptr": "void*", "bool": "bool",
        "void": "void",
    }

    for xtype, ctype in ctype_map.items():
        ctx.global_ns[xtype] = TypeObj(
            xy_node=xy.StructDef(name=xtype),
            c_node=c.Struct(name=ctype),
            builtin=True,
            init_value=c.Const(0)
        )
    ctx.void_obj = ctx.global_ns["void"]

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
                ("lt", "bool"), ("ltEqual", "bool"), ("gt", "bool"),
                ("gtEqual", "bool"), ("equal", "bool"), ("notEqual", "bool"),
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
                desc.rtype_obj = ctx.global_ns[rtype_name]

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
            desc.rtype_obj = ctx.global_ns["Ptr"]
    
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
            desc.rtype_obj = ctx.global_ns[rtype_name]
    
    select = xy.FuncDef(name="select", params=[
        xy.VarDecl("arr", xy.ArrayType(base=None)),
        xy.VarDecl("index", xy.Id("int")),
    ])
    select_obj = register_func(select, ctx)
    select_obj.builtin = True
    # XXX
    select_obj.rtype_obj = ctx.global_ns["int"]

    # string construction
    str_ctor = xy.StructDef(name="StrCtor", fields=[
        xy.VarDecl("prefix", type=None)
    ])
    str_obj = TypeObj(str_ctor, c.Struct("StringCtor"), builtin=True)
    str_obj.tags["xy.tag"] = InstanceObj(
        fields={
            "label": StrObj(parts=[ConstObj(value="xy.string")])
        }
    )
    ctx.global_ns["StrCtor"] = str_obj

    # entry point
    entrypoint = xy.StructDef(name="EntryPoint")
    ep_obj = TypeObj(entrypoint, builtin=True)
    ep_obj.tags["xy.tag"] = InstanceObj(
        fields={
            "label": StrObj(parts=[ConstObj(value="xy.entrypoint")])
        }
    )
    ctx.global_ns["EntryPoint"] = ep_obj

    # clib
    clib = xy.StructDef(name="CLib")
    clib_ojb = TypeObj(clib, builtin=True)
    clib_ojb.tags["xy.tag"] = InstanceObj(
        fields={
            "label": StrObj(parts=[ConstObj(value="xyc.lib")])
        }
    )
    ctx.global_ns["CLib"] = clib_ojb

def compile_funcs(ctx, ast, cast):
    for node in ast:
        if isinstance(node, xy.FuncDef):
            compile_func(node, ctx, ast, cast)
        elif isinstance(node, xy.Comment):
            pass
        elif not (isinstance(node, xy.StructDef) or isinstance(node, xy.Import)):
            import pdb; pdb.set_trace()
            raise CompilationError("NYI", node)

def compile_func(node, ctx, ast, cast):
    fspace = ctx.eval_to_fspace(node.name)
    fdesc = fspace.find(node, [], ctx)
    cfunc = fdesc.c_node

    param_objs = []
    for param, cparam in zip(node.params, cfunc.params):
        param_type = find_type(param.type, ctx)
        ctx.id_table[param.name] = VarObj(
            xy_node=param,
            c_node=cparam,
            type_desc=param_type
        )

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
            cvar = c.VarDecl(name=node.name, type=None, is_const=node.varying)
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
                cvar.type = type_desc.base.c_name
                cvar.dims = type_desc.dims
            else:
                cvar.type = type_desc.c_name
            ctx.id_table[node.name] = VarObj(node, cvar, type_desc)

            if node.value is not None:
                cvar.value = value_obj.c_node
            if node.value is None and isinstance(type_desc, ArrTypeObj):
                cvar.value = c.InitList()

            cfunc.body.append(cvar)
        else:
            expr_obj = compile_expr(node, cast, cfunc, ctx)
            if expr_obj.c_node is not None:
                cfunc.body.append(expr_obj.c_node)
    if is_func_body and ctx.current_fobj.etype_obj is not None:
        if len(body) == 0 or not isinstance(body[-1], xy.Return):
            cfunc.body.append(c.Return(ctx.current_fobj.etype_obj.init_value))
    ctx.exit_block()

c_symbol_type = TypeInferenceError(
    "The types of c symbols cannot be inferred. Please be explicit and specify the type."
)

def compile_expr(expr, cast, cfunc, ctx: CompilerContext) -> ExprObj:
    if isinstance(expr, xy.Const):
        return ExprObj(
            c_node=c.Const(expr.value_str),
            infered_type=ctx.get_compiled_type(expr.type)
        )
    elif isinstance(expr, xy.BinExpr):
        if expr.op not in {'.', '='}:
            fcall = rewrite_op(expr, ctx)
            return compile_expr(fcall, cast, cfunc, ctx)
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
            else:
                struct_obj = arg1_obj.infered_type
                if field_name not in struct_obj.fields:
                    raise CompilationError(f"No such field in struct {struct_obj.xy_node.name}", expr.arg2)
                field_obj = struct_obj.fields[field_name]
                res = c.Expr(arg1_obj.c_node, c.Id(field_obj.c_node.name), op=expr.op)
                return ExprObj(
                    c_node=res,
                    infered_type=field_obj.type_desc
                )
        else:
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx)
            arg2_obj = compile_expr(expr.arg2, cast, cfunc, ctx)
            res = c.Expr(arg1_obj.c_node, arg2_obj.c_node, op=expr.op)
            return ExprObj(
                c_node=res,
                infered_type=arg2_obj.infered_type
            )
    elif isinstance(expr, xy.UnaryExpr):
        fcall = rewrite_unaryop(expr, ctx)
        return compile_expr(fcall, cast, cfunc, ctx)
    elif isinstance(expr, xy.Id):
        var_obj = ctx.eval(expr)
        if var_obj is None:
            var_name = f" '{expr.name}'" if isinstance(expr, xy.Id) else ""
            raise CompilationError(f"Cannot find variable{var_name}", expr)
        if isinstance(var_obj, VarObj):
            return ExprObj(
                c_node=c.Id(var_obj.c_node.name),
                infered_type=var_obj.type_desc
            )
        elif isinstance(var_obj, TypeObj):
            return ExprObj(
                c_node=c.Id(var_obj.c_node.name),
                infered_type=var_obj
            )
        elif isinstance(var_obj, ImportObj):
            return ExprObj(
                c_node=None,
                xy_node=var_obj.xy_node,
                infered_type=var_obj
            )
        else:
            raise CompilationError("Invalid expression", expr)
    elif isinstance(expr, xy.FuncCall):
        return compile_fcall(expr, cast, cfunc, ctx)
    elif isinstance(expr, xy.StructLiteral):
        type_obj = find_type(expr.name, ctx)
        ctypename = type_obj.c_name
        res = c.StructLiteral(
            name=ctypename,
            args=[compile_expr(arg, cast, cfunc, ctx).c_node for arg in expr.args]
        )
        # TODO what about kwargs
        return ExprObj(
            c_node=res,
            infered_type=type_obj
        )
    elif isinstance(expr, xy.StrLiteral):
        if expr.prefix not in ctx.str_prefix_reg:
            raise CompilationError(
                f"No string constructor registered for prefix \"{expr.prefix}\"",
                expr
            )
        func_desc = ctx.str_prefix_reg[expr.prefix]

        str_const = expr.parts[0].value if len(expr.parts) else ""
        str_len = 0
        str_i = 0
        while str_i < len(str_const):
            str_len += 1
            if str_const[str_i] == '\\':
                str_i += 2
            else:
                str_i += 1

        c_func = c.FuncCall(func_desc.c_name, args=[
            c.Const('"' + str_const + '"'),
            c.Const(str_len)
        ])
        return ExprObj(
            c_node=c_func,
            infered_type=func_desc.rtype_obj
        )
    elif isinstance(expr, xy.ArrayLit):
        res = c.InitList()
        arr_type = "Cannot infer type of empty list"
        for elem in expr.elems:
            elem_expr = compile_expr(elem, cast, cfunc, ctx)
            res.elems.append(elem_expr.c_node)
            arr_type = elem_expr.infered_type
        return ExprObj(
            c_node=res,
            infered_type=ArrTypeObj(base=arr_type, dims=[len(expr.elems)])
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
    elif isinstance(expr, xy.Break):
        return compile_break(expr, cast, cfunc, ctx)
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)
    
def compile_fcall(expr: xy.FuncCall, cast, cfunc, ctx: CompilerContext):
    fspace = ctx.eval_to_fspace(expr.name)

    arg_exprs = [
        compile_expr(arg, cast, cfunc, ctx)
        for arg in expr.args
    ]
    arg_infered_types = [
        arg_expr.infered_type for arg_expr in arg_exprs
    ]
    
    func_obj = fspace.find(expr, arg_infered_types, ctx)

    if func_obj.builtin and func_obj.xy_node.name == "select":
        # TODO what if args is more numerous
        assert len(expr.args) == 2
        res = c.Index(
            arg_exprs[0].c_node,
            arg_exprs[1].c_node,
        )
        return ExprObj(
            c_node=res,
            infered_type=func_obj.rtype_obj
        )
    elif func_obj.builtin and len(expr.args) == 2:
        func_to_op_map = {
            "add": '+',
            "sub": '-',
            "mul": '*',
            "lt": '<',
            "ltEqual": '<=',
            "gt": '>',
            "gtEqual": ">=",
            "addEqual": "+=",
            "subEqual": "-=",
            "mulEqual": "*=",
            "divEqual": "/=",
            "equal": "==",
            "notEqual": "!=",
        }
        c_arg1 = arg_exprs[0].c_node
        if len(func_obj.xy_node.returns) == 1 and func_obj.xy_node.returns[0].type.name == "Ptr":
            # TODO what if Ptr has an attached type
            c_arg1 = c.Cast(c_arg1, to="int8_t*")
        res = c.Expr(
            c_arg1, arg_exprs[1].c_node,
            op=func_to_op_map[expr.name.name]
        )
        return ExprObj(
            c_node=res,
            infered_type=func_obj.rtype_obj
        )
    elif func_obj.builtin:
        assert len(expr.args) == 1
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
            infered_type=func_obj.rtype_obj
        )

    res = c.FuncCall(name=func_obj.c_name)
    if func_obj.xy_node is not None:
        for xy_param, arg in zip(func_obj.xy_node.params, arg_exprs):
            if not xy_param.is_pseudo:
                res.args.append(arg.c_node)
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
            err_obj.c_node.is_const = False
            err_obj.c_node.value = res
            cfunc.body.append(err_obj.c_node)

            check_error_fobj = ctx.eval_to_fspace(
                xy.Id("to", src=expr.src, coords=expr.coords),
                msg=f"Cannot handle error because there is no 'to' "
                f"function to convert {func_obj.etype_obj.xy_node.name} to bool"
            ).find(
                xy.FuncCall(xy.Id("to"), args=[xy.Id(""), xy.Id("")]),
                [func_obj.etype_obj, ctx.get_compiled_type(xy.Id("bool"))],
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

        return ExprObj(
            c_node=tmp_cid,
            xy_node=expr,
            infered_type=func_obj.rtype_obj
        )
    else:
        return ExprObj(
            c_node=res,
            infered_type=func_obj.rtype_obj
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
        ctx.id_table[name_hint] = var_obj
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
            ctx.id_table[name_hint] = tmp_obj
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
        ctx.id_table[name_hint] = tmp_obj
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
            ctx.id_table[name_hint] = tmp_obj
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
        ctx.id_table[name_hint] = tmp_obj
        cfunc.body.append(tmp_obj.c_node)
        res_c = c.Id(tmp_obj.c_node.name)
    else:
        inferred_type = ctx.void_obj


    # compile body
    if update_expr_obj is None:
        compile_body(xydowhile.block.body, cast, cdowhile, ctx)
    else:
        cdowhile.body.append(update_expr_obj.c_node)

    # finaly compile cond
    cond_obj = compile_expr(xydowhile.cond, cast, cfunc, ctx)
    cdowhile.cond = cond_obj.c_node

    cfunc.body.append(cdowhile)

    return ExprObj(
        xy_node=xydowhile,
        c_node=res_c,
        infered_type=inferred_type,
    )

def compile_break(xybreak, cast, cfunc, ctx):
    if xybreak.loop_name is not None:
        raise CompilationError("Breaking the outer loop is NYI", xybreak)
    return ExprObj(
        xy_node=xybreak,
        c_node=c.Break(),
        infered_type=ctx.void_obj,
    )

def compile_return(xyreturn, cast, cfunc, ctx: CompilerContext):
    xy_func = ctx.current_fobj.xy_node
    if xy_func.etype is None and len(xy_func.returns) <= 1:
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
        # return through argument
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


def compile_error(xyerror, cast, cfunc, ctx):
    ret = c.Return()
    if xyerror.value:
        value_obj = compile_expr(xyerror.value, cast, cfunc, ctx)
        ret.value = value_obj.c_node
    return ExprObj(
        xy_node=xyerror,
        c_node=ret,
        infered_type=value_obj.infered_type
    )

def get_c_type(type_expr, ctx):
    id_desc = find_type(type_expr, ctx, required=True)
    return id_desc.c_name

def mangle_def(fdef: xy.FuncDef, ctx, expand=False):
    mangled = ctx.module_name.replace(".", "_") + "_" + fdef.name.name
    if expand:
        mangled = [mangled, "__with"]
        for param in fdef.params:
            mangled.append("__")
            mangled.append(param.type.name)
        mangled = "".join(mangled)
    return mangled

def mangle_field(field: xy.VarDecl):
    # mangle in order to prevent duplication with macros
    return f"xy_{field.name}"

def mangle_struct(struct: xy.StructDef, ctx):
    return ctx.module_name.replace(".", "_") + "_" + struct.name


class CompilationError(Exception):
    def __init__(self, msg, node, notes=None):
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
    if not isinstance(texpr, xy.ArrayType):
        res = ctx.eval(texpr)
        if res is None:
            raise CompilationError("Cannot find type", texpr)
        return res
    else:
        if len(texpr.dims) == 0:
            raise CompilationError("Arrays must have a length known at compile time", texpr)

        base_type = find_type(texpr.base, ctx)
        dims = []
        for d in texpr.dims:
            dims.append(ct_eval(d, ctx))
        
        return ArrTypeObj(base=base_type, dims=dims)

def ct_eval(expr, ctx):
    if isinstance(expr, xy.Const):
        return expr.value
    raise CompilationError("Cannot Compile-Time Evaluate", expr)

def find_func(fcall, ctx):
    fspace = ctx.eval_to_fspace(fcall.name)
    return fspace.find(fcall, ctx)

def rewrite_op(binexpr, ctx):
    fname = {
        "+": "add",
        "-": "sub",
        "*": "mul",
        "/": "div",
        "<": "lt",
        ">": "gt",
        "<=": "ltEqual",
        ">=": "gtEqual",
        "+=": "addEqual",
        "-=": "subEqual",
        "*=": "mulEqual",
        "/=": "divEqual",
        "==": "equal",
        "!=": "notEqual",
    }.get(binexpr.op, None)
    if fname is None:
        raise CompilationError(f"Unrecognized operator '{binexpr.op}'", binexpr)
    fcall = xy.FuncCall(
        xy.Id(fname, src=binexpr.src, coords=binexpr.coords),
        args=[binexpr.arg1, binexpr.arg2],
        src=binexpr.src, coords=binexpr.coords)
    return fcall

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
        headers = obj.fields["headers"]
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
        ctx.id_table[imprt.in_name] = import_obj

def maybe_add_main(ctx, cast):
    if ctx.entrypoint_obj is not None:
        main = c.Func(
            name="main", rtype="int",
            params=[
                c.VarDecl("argc", "int"),
                c.VarDecl("argv", "char**")
            ], body=[
                c.VarDecl("res", "int", value=c.FuncCall(ctx.entrypoint_obj.c_name)),
                c.Return(c.Id("res")),
            ]
        )
        cast.funcs.append(main)
