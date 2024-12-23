import os
from xyc import ast as xy
from xyc import cast as c
from dataclasses import dataclass, field

@dataclass
class CompiledObj:
    tags: dict[str, 'CompiledObj'] = field(kw_only=True, default_factory=dict)

@dataclass
class TypeObj(CompiledObj):
    xy_node : any = None
    c_node : any = None
    builtin : bool = False

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None

@dataclass
class ArrTypeObj(CompiledObj):
    base : CompiledObj | None = None
    dims : list = field(default_factory=list)

    @property
    def c_name(self):
        self.base.c_name + "*"

@dataclass
class FuncObj(CompiledObj):
    xy_node: any = None
    c_node: any = None
    rtype_obj: TypeObj = None
    builtin: bool = False

    @property
    def c_name(self):
        if self.c_node is not None:
            return self.c_node.name
        return None

@dataclass
class VarObj(CompiledObj):
    xy_node: any = None
    c_node: any = None
    type_desc: TypeObj | None = None

class IdTable(dict):
    pass

class FuncSpace:
    def __init__(self):
        self._funcs = []

    def __len__(self):
        return len(self._funcs)
    
    def append(self, fdesc: FuncObj):
        self._funcs.append(fdesc)

    def __getitem__(self, i):
        return self._funcs[i]
    
    def find(self, node, ctx):
        if isinstance(node, xy.FuncCall):
            args_infered_types = [infer_type(arg, ctx) for arg in node.args]
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
class CompilerContext:
    module_name: str  # TODO maybe module_name should be a list of the module names
    id_table: IdTable = field(default_factory=IdTable)
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
    
    def get_func_space(self, name: xy.Id):
        if name.name not in self.id_table:
            raise CompilationError(f"Cannot find any functions named '{name.name}'", name)
        space = self.id_table[name.name]
        if not isinstance(space, FuncSpace):
            # TODO add notes here
            raise CompilationError(f"{name.name} is not a function.", name)
        return space

    def get_compiled_type(self, name: xy.Id):
        return self.id_table[name.name]

def compile_module(module_name, ast):
    ctx = CompilerContext(module_name)
    res = c.Ast()
    
    compile_header(ctx, ast, res)
    compile_funcs(ctx, ast, res)
    maybe_add_main(ctx, ast, res)

    return res

def compile_header(ctx: CompilerContext, ast, cast):
    import_builtins(ctx, cast)

    for node in ast:
        if isinstance(node, xy.StructDef):
            cstruct = c.Struct(name=mangle_struct(node, ctx))
            for field in node.fields:
                cfield = c.VarDecl(
                    name=field.name,
                    type=get_c_type(field.type, ctx)
                )
                cstruct.fields.append(cfield)

            ctx.id_table[node.name] = TypeObj(
                xy_node = node,
                c_node = cstruct,
            )
            cast.struct_decls.append(cstruct)
            cast.structs.append(cstruct)

    for node in ast:
        if isinstance(node, xy.FuncDef):
            func_space = ctx.ensure_func_space(node)
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
            for tag in node.tags.args:
                if isinstance(tag, xy.StructLiteral):
                    type_obj = ctx.get_compiled_type(tag.name)
                    # XXX Fix that
                    if type_obj.c_name == "StringCtor":
                        str_lit = tag.kwargs["prefix"]
                        prefix = str_lit.parts[0] if len(str_lit.parts) else ""
                        ctx.str_prefix_reg[prefix] = compiled
                elif isinstance(tag, xy.Id):
                    # XXX
                    compiled.tags["xi.entrypoint"] = ctx.id_table[tag.name]
                    # XXX
                    if tag.name == "EntryPoint":
                        ctx.entrypoint_obj = compiled

                else:
                    raise CompilationError("NYI", tag)

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
            func = xy.FuncDef(
                "add",
                params=[
                    xy.Param("x", xy.Type(type1)),
                    xy.Param("y", xy.Type(type2))
                ],
                rtype=xy.Type(rtype_name)
            )
            desc = register_func(func, ctx)
            desc.builtin = True
            desc.rtype_obj = ctx.id_table[rtype_name]
    
    select = xy.FuncDef(name="select", params=[
        xy.Param("arr", xy.ArrayType(base=None)),
        xy.Param("index", xy.Type("int")),
    ])
    select_obj = register_func(select, ctx)
    select_obj.builtin = True

    # string construction
    str_ctor = xy.StructDef(name="StrCtor", fields=[
        xy.VarDecl("prefix", type=None)
    ])
    str_obj = TypeObj(str_ctor, c.Struct("StringCtor"), builtin=True)
    ctx.id_table["StrCtor"] = str_obj

    entrypoint = xy.StructDef(name="EntryPoint")
    ep_obj = TypeObj(entrypoint, builtin=True)
    ctx.id_table["EntryPoint"] = ep_obj

def compile_funcs(ctx, ast, cast):
    for node in ast:
        if isinstance(node, xy.FuncDef):
            compile_func(node, ctx, ast, cast)
        elif isinstance(node, xy.Comment):
            pass
        elif not isinstance(node, xy.StructDef):
            raise CompilationError("NYI", node)

def compile_func(node, ctx, ast, cast):
    fspace = ctx.get_func_space(node)
    fdesc = fspace.find(node, ctx)
    cfunc = fdesc.c_node
    compile_body(node.body, cast, cfunc, ctx)
    cast.funcs.append(cfunc)

def compile_body(body, cast, cfunc, ctx):
    for node in body:
        if isinstance(node, xy.Return):
            ret = c.Return()
            if node.value:
                ret.value = compile_expr(node.value, cast, cfunc, ctx)
            cfunc.body.append(ret)
        elif isinstance(node, xy.VarDecl):
            cvar = c.VarDecl(name=node.name, type=None)
            type_desc = find_type(node.type, ctx) if node.type is not None else None
            if type_desc is None:
                if node.value is None:
                    raise CompilationError(
                        "Cannot create variable with no type and no value",
                        node
                    )
                type_desc = infer_type(node.value, ctx)
            if isinstance(type_desc, ArrTypeObj):
                cvar.type = type_desc.base.c_name
                cvar.dims = type_desc.dims
            else:
                cvar.type = type_desc.c_name
            ctx.id_table[node.name] = VarObj(node, cvar, type_desc)

            if node.value is not None:
                cvar.value = compile_expr(node.value, cast, cfunc, ctx)
            if node.value is None and isinstance(type_desc, ArrTypeObj):
                cvar.value = c.InitList()

            cfunc.body.append(cvar)
        else:
            raise CompilationError(f"Unknown xy ast node {type(node).__name__}", node)


def compile_expr(expr, cast, cfunc, ctx):
    if isinstance(expr, xy.Const):
        return c.Const(expr.value_str)
    elif isinstance(expr, xy.BinExpr):
        arg1 = compile_expr(expr.arg1, cast, cfunc, ctx)
        arg2 = compile_expr(expr.arg2, cast, cfunc, ctx)
        res = c.Expr(arg1, arg2, op=expr.op)
        return res
    elif isinstance(expr, xy.Id):
        res = c.Id(expr.name)
        return res
    elif isinstance(expr, xy.FuncCall):
        fspace = ctx.get_func_space(expr)
        func_obj = fspace.find(expr, ctx)

        if func_obj.builtin and func_obj.xy_node.name == "select":
            # TODO what if args is more numerous
            assert len(expr.args) == 2
            res = c.Index(
                compile_expr(expr.args[0], cast, cfunc, ctx),
                compile_expr(expr.args[1], cast, cfunc, ctx),
            )
            return res

        res = c.FuncCall(name=func_obj.c_name)
        for i in range(len(expr.args)):
            res.args.append(compile_expr(expr.args[i], cast, cfunc, ctx))
        return res
    elif isinstance(expr, xy.StructLiteral):
        ctypename = get_c_type(expr.name, ctx)
        res = c.StructLiteral(
            name=ctypename,
            args=[compile_expr(arg, cast, cfunc, ctx) for arg in expr.args]
        )
        # TODO what about kwargs
        return res
    elif isinstance(expr, xy.StrLiteral):
        if expr.prefix not in ctx.str_prefix_reg:
            raise CompilationError(
                f"No string constructor registered for prefix '{expr.prefix}'",
                expr
            )
        func_desc = ctx.str_prefix_reg[expr.prefix]

        str_const = expr.parts[0].value if len(expr.parts) else ""
        c_func = c.FuncCall(func_desc.c_name, args=[
            c.Const('"' + str_const + '"'),
            c.Const(len(str_const))
        ])
        return c_func
    elif isinstance(expr, xy.ArrayLit):
        res = c.InitList()
        for elem in expr.elems:
            res.elems.append(compile_expr(elem, cast, cfunc, ctx))
        return res
    elif isinstance(expr, xy.Select):
        rewritten = rewrite_select(expr, ctx)
        return compile_expr(rewritten, cast, cfunc, ctx)
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)


def get_c_type(type_expr, ctx):
    id_desc = find_type(type_expr, ctx)
    return id_desc.c_name

def mangle_def(fdef: xy.FuncDef, ctx, expand=False):
    mangled = ctx.module_name + "_" + fdef.name
    if expand:
        mangled = [mangled, "__with__"]
        for param in fdef.params:
            mangled.append(param.type.name)
        mangled = "".join(mangled)
    return mangled

def mangle_struct(struct: xy.StructDef, ctx):
    return ctx.module_name + "_" + struct.name


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


def infer_type(expr, ctx):
    if isinstance(expr, xy.Const):
        return ctx.id_table[expr.type]
    elif isinstance(expr, xy.StructLiteral):
        return ctx.id_table[expr.name.name]
    elif isinstance(expr, xy.FuncCall):
        fdesc = find_func(expr, ctx)
        return ctx.id_table[fdesc.xy_node.rtype.name]
    elif isinstance(expr, xy.BinExpr):
        fcall = rewrite_op(expr, ctx)
        return infer_type(fcall, ctx)
    elif isinstance(expr, xy.Id):
        vardesc = ctx.id_table[expr.name]
        return vardesc.type_desc
    elif isinstance(expr, xy.StrLiteral):
        if expr.prefix not in ctx.str_prefix_reg:
            raise CompilationError(
                f"No string constructor registered for prefix '{expr.prefix}'",
                expr
            )
        func_desc = ctx.str_prefix_reg[expr.prefix]
        return func_desc.rtype_obj
    elif isinstance(expr, xy.ArrayLit):
        if len(expr.elems) <= 0:
            raise CompilationError("Cannot infer type of an empty array")
        base_type = infer_type(expr.elems[0], ctx)
        res = ArrTypeObj(base_type, dims=[len(expr.elems)])
        return res
    else:
        raise CompilationError("Cannot infer type", expr)


def register_func(fdef, ctx):
    fspace = ctx.ensure_func_space(fdef)
    res = FuncObj(fdef)
    fspace.append(res)
    return res

def find_type(texpr, ctx):
    if isinstance(texpr, xy.Id) or isinstance(texpr, xy.Type):
        return ctx.id_table[texpr.name]
    elif isinstance(texpr, xy.ArrayType):
        base_type = find_type(texpr.base, ctx)

        if len(texpr.dims) == 0:
            raise CompilationError("Arrays must have a length known at compile time", texpr)
        dims = []
        for d in texpr.dims:
            dims.append(ct_eval(d, ctx))
        
        return ArrTypeObj(base_type, dims=dims)
    else:
        raise CompilationError("Cannot determine type", texpr)

def ct_eval(expr, ctx):
    if isinstance(expr, xy.Const):
        return expr.value
    raise CompilationError("Cannot Compile-Time Evaluate", expr)

def find_func(fcall, ctx):
    fspace = ctx.get_func_space(fcall)
    return fspace.find(fcall, ctx)

def rewrite_op(binexpr, ctx):
    fname = {
        "+": "add",
        "*": "mult",
    }[binexpr.op]
    fcall = xy.FuncCall(fname, args=[
        binexpr.arg1, binexpr.arg2
    ], src=binexpr.src, coords=binexpr.coords)
    return fcall

def rewrite_select(select, ctx):
    fcall = xy.FuncCall(
        "select", args=[select.base, *select.args.args],
        kwargs=select.args.kwargs,
        src=select.src,
        coords=select.coords
    )
    return fcall

def maybe_add_main(ctx, ast, cast):
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
