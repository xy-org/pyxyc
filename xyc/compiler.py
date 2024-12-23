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

class IdTable(dict):
    pass


@dataclass
class CompilerContext:
    module_name: str  # TODO maybe module_name should be a list of the module names
    id_table: IdTable = field(default_factory=IdTable)


def compile_module(module_name, ast):
    ctx = CompilerContext(module_name)
    res = c.Ast()
    
    compile_header(ctx, ast, res)
    compile_funcs(ctx, ast, res)

    return res

def compile_header(ctx, ast, cast):
    import_builtins(ctx, cast)

    for node in ast:
        if isinstance(node, xy.StructDef):
            cstruct = c.Struct(name=mangle(node.name, ctx))
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
            name = mangle(node.name, ctx)
            rtype = get_c_type(node.rtype, ctx)
            cfunc = c.Func(name=name, rtype=rtype)
            cast.funcs.append(cfunc)
            for param in node.params:
                cparam = c.VarDecl(param.name, get_c_type(param.type, ctx))
                cfunc.params.append(cparam)
            compile_body(node.body, cast, cfunc, ctx)
        elif isinstance(node, xy.Comment):
            pass
        elif not isinstance(node, xy.StructDef):
            raise CompilationError("NYI", node)
    return cast

def import_builtins(ctx, cast):
    # always include it as it is everywhere
    cast.includes.append(c.Include("stdint.h"))
    cast.includes.append(c.Include("stddef.h"))

    ctx.id_table["int"] = TypeDesc(c_name = "int32_t", builtin=True)
    ctx.id_table["uint"] = TypeDesc(c_name = "uint32_t", builtin=True)
    ctx.id_table["long"] = TypeDesc(c_name = "int64_t", builtin=True)
    ctx.id_table["ulong"] = TypeDesc(c_name = "uint64_t", builtin=True)
    ctx.id_table["float"] = TypeDesc(c_name = "float", builtin=True)
    ctx.id_table["double"] = TypeDesc(c_name = "double", builtin=True)
    ctx.id_table["void"] = TypeDesc(c_name = "void", builtin=True)
    ctx.id_table["Size"] = TypeDesc(c_name = "size_t", builtin=True)
    ctx.id_table["Ptr"] = TypeDesc(c_name="void*", builtin=True)

def compile_funcs(ctx, ast, cast):
    pass

def compile_body(body, cast, cfunc, ctx):
    for node in body:
        if isinstance(node, xy.Return):
            ret = c.Return()
            if node.value:
                ret.value = compile_expr(node.value, cast, cfunc, ctx)
            cfunc.body.append(ret)
        elif isinstance(node, xy.VarDecl):
            cvar = c.VarDecl(name=node.name, type=None)
            if node.type is None:
                if node.value is None:
                    raise CompilationError(
                        "Cannot create variable with no type and no value",
                        node
                    )
                type_desc = infer_type(node.value, ctx)
                cvar.type = type_desc.c_name
            else:
                cvar.type = get_c_type(node.type, ctx)
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
    elif isinstance(expr, xy.Var):
        res = c.Name(expr.name)
        return res
    elif isinstance(expr, xy.FuncCall):
        c_name = mangle(expr.name, ctx)
        res = c.FuncCall(name=c_name)
        for i in range(len(expr.args)-1, -1, -1):
            res.args.append(compile_expr(expr.args[i], cast, cfunc))
        return res
    elif isinstance(expr, xy.StructLiteral):
        ctypename = get_c_type(expr.name, ctx)
        res = c.StructLiteral(
            name=ctypename,
            args=[compile_expr(arg, cast, cfunc, ctx) for arg in expr.args]
        )
        # TODO what about kwargs
        return res
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)


def get_c_type(type_expr, ctx):
    id_desc = ctx.id_table[type_expr.name]
    return id_desc.c_name

def mangle(name, ctx):
    return ctx.module_name + "_" + name


class CompilationError(Exception):
    def __init__(self, msg, node):
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


    def __str__(self):
        return self.fmt_msg


def infer_type(expr, ctx):
    if isinstance(expr, xy.Const):
        return ctx.id_table[expr.type]
    elif isinstance(expr, xy.StructLiteral):
        return ctx.id_table[expr.name.name]
    else:
        raise CompilationError("Cannot infer type", expr)