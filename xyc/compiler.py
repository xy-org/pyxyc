import os
from xyc import ast as xy
from xyc import cast as c
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

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None

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
            fsig = node.name + "(" + \
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
    res = fdef.name + "(" + ", ".join(p.type.name for p in fdef.params) + ")"
    res += " -> " + fdef.rtype.name
    return res

@dataclass
class ModuleHeader:
    namespace: IdTable

@dataclass
class CompilerContext:
    builder: any
    module_name: str  # TODO maybe module_name should be a list of the module names
    id_table: IdTable = field(default_factory=IdTable)
    global_ns: IdTable = field(default_factory=IdTable)
    str_prefix_reg: dict[str, any] = field(default_factory=dict)
    entrypoint_obj: any = None

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
    
    def eval_to_fspace(self, name: xy.Node):
        space = self.eval(name)
        if space is None:
            raise CompilationError(f"Cannot find any functions named '{name.name}'", name)
        if not (isinstance(space, FuncSpace) or isinstance(space, ExtSpace)):
            # TODO add notes here
            raise CompilationError(f"Not a function.", name)
        return space
    
    def eval_to_var(self, name: xy.Node):
        var_obj = self.eval(name)
        if var_obj is None:
            raise CompilationError("Cannot find variable", name)
        if not isinstance(var_obj, VarObj):
            raise CompilationError(f"Not a function.", name)
        return var_obj

    def get_compiled_type(self, name: xy.Id):
        return self.id_table[name.name]
    
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
            # maybe instead of None we can return a special object
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
            raise CompilationError(
                "Cannot evaluate at compile time. "
                f"Unknown expression type '{type(node).__name__}'",
                node)
            

def compile_module(builder, module_name, asts):
    ctx = CompilerContext(builder, module_name)
    res = c.Ast()

    compile_header(ctx, asts, res)
    
    for ast in asts:
        compile_funcs(ctx, ast, res)
    
    maybe_add_main(ctx, res)

    return ModuleHeader(namespace=ctx.id_table), res

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
                        name=field.name,
                        type=field_type_obj.c_name
                    )
                    fields[field.name] = VarObj(
                        xy_node=field,
                        c_node=cfield,
                        type_desc=field_type_obj,
                    )
                    cstruct.fields.append(cfield)
                type_obj.fields = fields

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
                rtype_compiled = ctx.get_compiled_type(node.rtype)
                rtype = rtype_compiled.c_name
                cfunc = c.Func(name=cname, rtype=rtype)
                for param in node.params:
                    cparam = c.VarDecl(param.name, get_c_type(param.type, ctx))
                    cfunc.params.append(cparam)
                cast.func_decls.append(cfunc)

                compiled = FuncObj(node, cfunc, rtype_obj=rtype_compiled)

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

def import_builtins(ctx, cast):
    # always include it as it is everywhere
    cast.includes.append(c.Include("stdint.h"))
    cast.includes.append(c.Include("stddef.h"))
    cast.includes.append(c.Include("stdbool.h"))

    num_types = [
       "int", "uint",
       "long", "ulong",
       "Size",
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
        ctx.id_table[xtype] = TypeObj(
            xy_node=xy.StructDef(name=xtype),
            c_node=c.Struct(name=ctype),
            builtin=True
        )

    # fill in base math operations
    for p1, type1 in enumerate(num_types):
        for p2, type2 in enumerate(num_types):
            types = {type1, type2}
            if "Size" in types and ("float" in types or "double" in types):
                continue
            rtype_name = type1 if p1 > p2 else type2
            for fname in ["add", "mul", "lt"]:
                func = xy.FuncDef(
                    fname,
                    params=[
                        xy.Param("x", xy.Id(type1)),
                        xy.Param("y", xy.Id(type2))
                    ],
                    rtype=xy.Id(rtype_name)
                )
                desc = register_func(func, ctx)
                desc.builtin = True
                desc.rtype_obj = ctx.id_table[rtype_name]
    
    select = xy.FuncDef(name="select", params=[
        xy.Param("arr", xy.ArrayType(base=None)),
        xy.Param("index", xy.Id("int")),
    ])
    select_obj = register_func(select, ctx)
    select_obj.builtin = True
    # XXX
    select_obj.rtype_obj = ctx.id_table["int"]

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
    ctx.id_table["StrCtor"] = str_obj

    # entry point
    entrypoint = xy.StructDef(name="EntryPoint")
    ep_obj = TypeObj(entrypoint, builtin=True)
    ep_obj.tags["xy.tag"] = InstanceObj(
        fields={
            "label": StrObj(parts=[ConstObj(value="xy.entrypoint")])
        }
    )
    ctx.id_table["EntryPoint"] = ep_obj

    # clib
    clib = xy.StructDef(name="CLib")
    clib_ojb = TypeObj(clib, builtin=True)
    clib_ojb.tags["xy.tag"] = InstanceObj(
        fields={
            "label": StrObj(parts=[ConstObj(value="xyc.lib")])
        }
    )
    ctx.id_table["CLib"] = clib_ojb

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
    for param in node.params:
        param_type = find_type(param.type, ctx)
        ctx.id_table[param.name] = VarObj(
            xy_node=param,
            type_desc=param_type
        )

    compile_body(node.body, cast, cfunc, ctx)
    cast.funcs.append(cfunc)

def compile_body(body, cast, cfunc, ctx):
    for node in body:
        if isinstance(node, xy.Return):
            ret = c.Return()
            if node.value:
                ret.value = compile_expr(node.value, cast, cfunc, ctx).c_node
            cfunc.body.append(ret)
        elif isinstance(node, xy.VarDecl):
            cvar = c.VarDecl(name=node.name, type=None)
            value_obj = compile_expr(node.value, cast, cfunc, ctx) if node.value is not None else None
            type_desc = find_type(node.type, ctx) if node.type is not None else None
            if type_desc is None:
                if value_obj is None:
                    raise CompilationError(
                        "Cannot create variable with no type and no value",
                        node
                    )
                type_desc = value_obj.infered_type
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
        elif isinstance(node, xy.FuncCall):
            compiled = compile_expr(node, cast, cfunc, ctx).c_node
            cfunc.body.append(compiled)
        else:
            expr_obj = compile_expr(node, cast, cfunc, ctx)
            if expr_obj.c_node is not None:
                cfunc.body.append(expr_obj.c_node)


def compile_expr(expr, cast, cfunc, ctx) -> ExprObj:
    if isinstance(expr, xy.Const):
        return ExprObj(
            c_node=c.Const(expr.value_str),
            infered_type=ctx.id_table[expr.type]
        )
    elif isinstance(expr, xy.BinExpr):
        if expr.op != '.':
            fcall = rewrite_op(expr, ctx)
            return compile_expr(fcall, cast, cfunc, ctx)
        else:
            arg1_obj = compile_expr(expr.arg1, cast, cfunc, ctx)
            assert isinstance(expr.arg2, xy.Id)
            field_name = expr.arg2.name
            res = c.Expr(arg1_obj.c_node, c.Id(field_name), op=expr.op)
            return ExprObj(
                c_node=res,
                infered_type=arg1_obj.infered_type.fields[field_name].type_desc
            )
    elif isinstance(expr, xy.Id):
        res = c.Id(expr.name)
        return ExprObj(
            c_node=res,
            infered_type=ctx.eval_to_var(expr).type_desc
        )
    elif isinstance(expr, xy.FuncCall):
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
        elif func_obj.builtin:
            assert len(expr.args) == 2
            func_to_op_map = {
                "add": '+',
                "mul": '*',
                "lt": '<',
                "lte": '<=',
                "gt": '>',
                "gte": ">="
            }
            res = c.Expr(
                arg_exprs[0].c_node, arg_exprs[1].c_node,
                op=func_to_op_map[expr.name.name]
            )
            return ExprObj(
                c_node=res,
                infered_type=func_obj.rtype_obj
            )

        res = c.FuncCall(name=func_obj.c_name)
        for arg in arg_exprs:
            res.args.append(arg.c_node)
        return ExprObj(
            c_node=res,
            infered_type=func_obj.rtype_obj
        )
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
                f"No string constructor registered for prefix '{expr.prefix}'",
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
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)

def compile_if(ifexpr, cast, cfunc, ctx):
    c_if = c.If()
    cond_obj = compile_expr(ifexpr.cond, cast, cfunc, ctx)
    # TODO check type is bool
    c_if.cond = cond_obj.c_node
    cfunc.body.append(c_if)

    body_to_compile = ifexpr.block
    if not isinstance(body_to_compile, list):
        body_to_compile = [body_to_compile]
    compile_body(body_to_compile, cast, c_if, ctx)

    if isinstance(ifexpr.else_block, list):
        # XXX fix that
        hack_if = c.If()
        compile_body(ifexpr.else_block, cast, hack_if, ctx)
        c_if.else_body = hack_if.body

    return ExprObj(
        xy_node=ifexpr,
        c_node=None,
        infered_type=find_type(xy.Id("void"), ctx)  # TODO remove this call to find type
    )

def get_c_type(type_expr, ctx):
    id_desc = find_type(type_expr, ctx)
    return id_desc.c_name

def mangle_def(fdef: xy.FuncDef, ctx, expand=False):
    mangled = ctx.module_name.replace(".", "_") + "_" + fdef.name.name
    if expand:
        mangled = [mangled, "__with__"]
        for param in fdef.params:
            mangled.append(param.type.name)
        mangled = "".join(mangled)
    return mangled

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
        
        self.error_message = msg
        self.fmt_msg = f"{fn}:{line_num}:{loc - line_loc + 1}: error: {msg}\n"
        if loc >= 0:
            self.fmt_msg += f"| {node.src.code[line_loc:line_end]}\n"
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

def find_type(texpr, ctx):
    if not isinstance(texpr, xy.ArrayType):
        return ctx.eval(texpr)
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
        "*": "mul",
        "<": "lt",
        ">": "gt",
        "<=": "lte",
        ">=": "gte"
    }[binexpr.op]
    fcall = xy.FuncCall(
        xy.Id(fname, src=binexpr.src, coords=binexpr.coords),
        args=[binexpr.arg1, binexpr.arg2],
        src=binexpr.src, coords=binexpr.coords)
    return fcall

def rewrite_select(select, ctx):
    fcall = xy.FuncCall(
        xy.Id("select"), args=[select.base, *select.args.args],
        kwargs=select.args.kwargs,
        src=select.src,
        coords=select.coords
    )
    return fcall

def compile_import(imprt, ctx, ast, cast):
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
