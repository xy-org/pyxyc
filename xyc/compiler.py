import os
from xyc import ast as xy
from xyc import cast as c
from dataclasses import dataclass


@dataclass
class CompilerContext:
    module_name: str  # TODO maybe module_name should be a list of the module names


def compile_module(module_name, ast):
    ctx = CompilerContext(module_name)
    res = c.Ast()
    res.includes.append(c.Include("stdint.h"))  # always include it as it is everywhere
    for node in ast:
        if isinstance(node, xy.FuncDef):
            name = mangle(node.name, ctx)
            rtype = get_c_type(node.rtype, ctx)
            cfunc = c.Func(name=name, rtype=rtype)
            res.funcs.append(cfunc)
            for param in node.params:
                cparam = c.VarDecl(param.name, get_c_type(param.type, ctx))
                cfunc.params.append(cparam)
            compile_body(node.body, res, cfunc, ctx)
        else:
            raise CompilationError("NYI", node)
    return res

def compile_body(body, cast, cfunc, ctx):
    for node in body:
        if isinstance(node, xy.Return):
            ret = c.Return()
            if node.value:
                ret.value = compile_expr(node.value, cast, cfunc, ctx)
            cfunc.body.append(ret)
        else:
            raise CompilationError(f"Unknown xy ast node {type(node).__name__}", node)


def compile_expr(expr, cast, cfunc, ctx):
    if isinstance(expr, xy.Const):
        return c.Const(expr.value)
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
    else:
        raise CompilationError(f"Unknown xy ast node {type(expr).__name__}", expr)


def get_c_type(type_expr, ctx):
    if type_expr.name == "int":
        return "int32_t"
    elif type_expr.name == "uint":
        return "uint32_t"
    elif type_expr.name == "long":
        return "int64_t"
    elif type_expr.name == "ulong":
        return "uint64_t"
    return type_expr.name

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
