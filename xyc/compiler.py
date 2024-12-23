import os
from xyc import ast as xy
from xyc import cast as c
from dataclasses import dataclass, field

@dataclass
class TypeDesc:
    xy_struct : any = None
    c_struct : any = None
    c_name : str | None = None
    builtin : bool = False

@dataclass
class FuncDesc:
    xy_func: any = None
    c_func: any = None
    c_name : str | None = None
    rtype_desc: TypeDesc = None

@dataclass
class VarDesc:
    xy_node: any = None
    c_node: any = None
    type_desc: TypeDesc | None = None

class IdTable(dict):
    pass

class FuncSpace:
    def __init__(self):
        self._funcs = []

    def __len__(self):
        return len(self._funcs)
    
    def append(self, fdesc: FuncDesc):
        self._funcs.append(fdesc)

    def __getitem__(self, i):
        return self._funcs[i]
    
    def find(self, node, ctx):
        if isinstance(node, xy.FuncCall):
            args_infered_types = [infer_type(arg, ctx) for arg in node.args]
            for desc in self._funcs:
                if cmp_call_def(node, args_infered_types, desc.xy_func, ctx):
                    return desc
            fsig = node.name + "(" + \
                ", ".join(t.xy_struct.name for t in args_infered_types) + \
                ")"
            candidates = "\n    ".join((
                func_sig(f.xy_func) for f in self._funcs
            ))
            raise CompilationError(
                f"Cannot find function '{fsig}'", node,
                notes=[(f"Candidates are:\n    {candidates}", None)]
            )
        else:
            assert isinstance(node, xy.FuncDef)
            for desc in self._funcs:
                if desc.xy_func == node:
                    return desc
            raise "Cannot find func"

def cmp_call_def(fcall, fcall_args_types, fdef, ctx):
    # TODO what about kwargs
    if len(fcall.args) != len(fdef.params):
        return False
    for arg_type, param in zip(fcall_args_types, fdef.params):
        if arg_type.xy_struct.name != param.type.name:
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
                (f"Previous definition of '{name.name}'", candidate.xy_struct)
            ]
        )
    
    def get_func_space(self, name: xy.Id):
        if name.name not in self.id_table:
            raise CompilationError(f"Cannot find function '{name.name}", name)
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

            ctx.id_table[node.name] = TypeDesc(
                xy_struct = node,
                c_struct = cstruct,
                c_name=cstruct.name
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
                func_desc.c_name = mangle_def(
                    func_desc.xy_func, ctx, expand=True
                )
                func_desc.c_func.name = func_desc.c_name
            
            cname = mangle_def(node, ctx, expand=expand_name)
            rtype_compiled = ctx.get_compiled_type(node.rtype)
            rtype = rtype_compiled.c_name
            cfunc = c.Func(name=cname, rtype=rtype)
            for param in node.params:
                cparam = c.VarDecl(param.name, get_c_type(param.type, ctx))
                cfunc.params.append(cparam)
            cast.func_decls.append(cfunc)

            compiled = FuncDesc(node, cfunc, cname, rtype_desc=rtype_compiled)

            # compile tags
            for tag in node.tags.args:
                if isinstance(tag, xy.StructLiteral):
                    type_obj = ctx.get_compiled_type(tag.name)
                    # XXX Fix that
                    if type_obj.c_name == "StringCtor":
                        str_lit = tag.kwargs["prefix"]
                        prefix = str_lit.parts[0] if len(str_lit.parts) else ""
                        ctx.str_prefix_reg[prefix] = compiled
                else:
                    raise "NYI"

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
        ctx.id_table[xtype] = TypeDesc(
            xy_struct=xy.StructDef(name=xtype),
            c_name = ctype, builtin=True
        )


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
            desc.rtype_desc = ctx.id_table[rtype_name]

    str_ctor = xy.StructDef(name="StrCtor", fields=[
        xy.VarDecl("prefix", type=None)
    ])
    str_obj = TypeDesc(str_ctor, None, c_name="StringCtor", builtin=True)
    ctx.id_table["StrCtor"] = str_obj

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
    cfunc = fdesc.c_func
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
            type_desc = ctx.id_table[node.type.name] if node.type is not None else None
            if type_desc is None:
                if node.value is None:
                    raise CompilationError(
                        "Cannot create variable with no type and no value",
                        node
                    )
                type_desc = infer_type(node.value, ctx)
            cvar.type = type_desc.c_name
            ctx.id_table[node.name] = VarDesc(node, cvar, type_desc)

            if node.value is not None:
                cvar.value = compile_expr(node.value, cast, cfunc, ctx)

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
        res = c.Name(expr.name)
        return res
    elif isinstance(expr, xy.FuncCall):
        fspace = ctx.get_func_space(expr)
        c_name = fspace.find(expr, ctx).c_name
        res = c.FuncCall(name=c_name)
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
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)


def get_c_type(type_expr, ctx):
    id_desc = ctx.id_table[type_expr.name]
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
        return ctx.id_table[fdesc.xy_func.rtype.name]
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
        return func_desc.rtype_desc
    else:
        raise CompilationError("Cannot infer type", expr)


def register_func(fdef, ctx):
    fspace = ctx.ensure_func_space(fdef)
    res = FuncDesc(fdef)
    fspace.append(res)
    return res


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