import os
import glob
from os import path
import subprocess
from xyc.ast import Source
from xyc.parser import parse_code
from xyc.compiler import compile_module, compile_ctti, compile_builtins, maybe_add_main, gen_global_stack, CompilationError
import xyc.cstringifier as cstringifier
from dataclasses import dataclass
import xyc.cast as c

@dataclass
class CompiledModule:
    header: any = None
    source: c.Ast = None

class Builder:
    def __init__(self, input: str, output: str | None = None,
                 compile_only=False, work_dir=".xyc_build",
                 library_path: list[str] = [], builtin_lib_path: str = None,
                 rich_errors=False, abort_on_unhandled=True):
        self.input = input
        self.output = output
        self.project_name = path.splitext(path.basename(path.abspath(input)))[0]
        if not output:
            self.output = self.project_name
        self.module_cache = {}
        self.rich_errors = rich_errors
        self.abort_on_unhandled = abort_on_unhandled

        package_paths = []
        for lib in library_path:
            package_paths.extend(glob.iglob(os.path.join(lib, "**")))

        if not path.isfile(input):
            current_package_path = path.dirname(path.abspath(input))
            package_paths = package_paths + [current_package_path]

        if builtin_lib_path is None:
            builtin_lib_path = path.join(path.dirname(__file__), "libs")
        self.builtin_lib_path = builtin_lib_path
        self.search_paths = package_paths + [builtin_lib_path]

        self.compile_only = compile_only
        self.work_dir = work_dir

        self.entrypoint_module_names = []
        self.entrypoint_priority = 0

        self.module_import_stack = []
        self.module_import_index = {}

        self.global_type_reg = dict()

    def build(self):
        module_name = path.basename(self.input)
        if "." in module_name:
            module_name = path.splitext(module_name)[0]

        self.compile_builtins()
        self.do_compile_module(module_name, self.input)
        self.do_build()

    def import_module(self, module_name: str, xy_node):
        if module_name in self.module_cache:
            return self.module_cache[module_name].header

        self.check_cyclical_imports(module_name, xy_node)
        self.module_import_index[module_name] = len(self.module_import_stack)
        self.module_import_stack.append(xy_node)

        if module_name == "xy.ctti":
            self.compile_ctti()
            return self.module_cache[module_name].header

        module_path = self.locate_module(module_name)
        if module_path is None:
            return None

        header, _ = self.do_compile_module(module_name, module_path)

        del self.module_import_index[module_name]
        self.module_import_stack.pop()

        return header

    def check_cyclical_imports(self, module_name, xy_node):
        idx = self.module_import_index.get(module_name, None)
        if idx is not None:
            notes = []
            while idx < len(self.module_import_stack):
                msg = "Which in turn imports"
                if len(notes) == 0:
                    msg = "Cyclical module dependency. Import loop begins here:"
                notes.append((msg, self.module_import_stack[idx]))
                idx = idx + 1
            notes.append(("Finally imports:", xy_node))
            raise CompilationError(*notes[0], notes=notes[1:])

    def compile_builtins(self):
        builtins_module_name = "xy.builtins"
        module_path = path.join(self.builtin_lib_path, "xy", "builtins")
        if not path.exists(module_path):
            raise ValueError(f"Cannot locate the 'xy' library at {module_path}")
        module_ast = parse_module(module_path, builtins_module_name)

        header, c_srcs = compile_builtins(
            self, builtins_module_name, list(module_ast.values())[0], module_path
        )

        self.module_cache[builtins_module_name] = CompiledModule(header, c_srcs)

    def compile_ctti(self):
        ctti_module_name = "xy.ctti"
        module_path = path.join(self.builtin_lib_path, "xy", "ctti")
        if not path.exists(module_path):
            raise ValueError(f"Cannot locate the 'xy' library at {module_path}")
        module_ast = parse_module(module_path, ctti_module_name)

        header, c_srcs = compile_ctti(
            self, ctti_module_name, list(module_ast.values())[0], module_path
        )

        self.module_cache[ctti_module_name] = CompiledModule(header, c_srcs)

    def do_compile_module(self, module_name: str, module_path: str):
        module_ast = parse_module(module_path, module_name)
        assert len(module_ast) == 1
        header, c_srcs = compile_module(
            self, module_name, list(module_ast.values())[0], module_path
        )
        self.module_cache[module_name] = CompiledModule(header, c_srcs)
        if header.ctx.entrypoint_obj is not None:
            if header.ctx.entrypoint_priority > self.entrypoint_priority:
                self.entrypoint_module_names = [module_name]
                self.entrypoint_priority = header.ctx.entrypoint_priority
            elif header.ctx.entrypoint_priority == self.entrypoint_priority:
                self.entrypoint_module_names.append(module_name)
        self.add_global_types(header.ctx.global_types)
        return header, c_srcs

    def locate_module(self, module_name: str):
        search_paths = self.search_paths
        for path in search_paths:
            module_path = os.path.join(path, *(module_name.split('.')))
            if os.path.exists(module_path):
                return module_path
        return None

    def do_build(self):
        if len(self.entrypoint_module_names) == 1:
            module = self.module_cache[self.entrypoint_module_names[0]]
            maybe_add_main(module.header.ctx, module.source, len(self.global_type_reg) > 0, "xy.sys" in self.module_cache)
        elif len(self.entrypoint_module_names) > 0:
            raise ValueError("Multiple entry points found")

        if len(self.global_type_reg) > 0:
            dummy_ast = c.Ast()
            gen_global_stack(self.global_type_reg, dummy_ast)
            self.module_cache["__XY__GLOBAL_STACK_AST"] = CompiledModule(None, dummy_ast)

        if self.compile_only:
            self.write_output(list(self.module_cache.values()), self.output)
        else:
            os.makedirs(self.work_dir, exist_ok=True)
            tmp_file = path.join(self.work_dir, f"{self.project_name}.c")
            self.write_output(list(self.module_cache.values()), tmp_file)
            self.run_cc([tmp_file], self.output)

    def run_cc(self, files, output):
        # Refer to https://clang.llvm.org/docs/DiagnosticsReference.html
        # for a detailed description on the warning messages
        cc_proc = subprocess.run(
            ["clang", "-std=c99",

             # turn on as much as (reasonably) possible
             "-Wall", "-pedantic", "-Wformat", "-Wextra", "-Wuninitialized",

             # TODO reenable these
             # "-Wsign-conversion", "-Wtautological-unsigned-zero-compare",
             "-Wno-sign-compare",

             # TODO reenable that
             "-Wno-format-pedantic",

             # The compiler may generate some unnecessary tmp vars
             "-Wno-unused-variable", "-Wno-unused-but-set-variable",

             # Not using a parameter is fine
             "-Wno-unused-parameter", "-Wno-unused-but-set-parameter",

             # That shouldn't be a thing
             "-Wno-missing-field-initializers",

             # code generated by xyc or inlined code should not emit any warnings
             "-Werror",

             *files, "-o", output],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if cc_proc.returncode != 0:
            print("C compilation failed with:")
            print(cc_proc.stdout)
            print("If you are calling any c functions directly please review "
                  "your code. If you think it is a problem with the Xy compiler"
                  "please report it at TBD.")
            raise ValueError(f"C compilation failed")

    def write_output(self, modules: list[CompiledModule], output):
        # merge all into one big .c file
        big_ast = c.Ast()
        for module in modules:
            big_ast.merge(module.source)
        c_src = cstringifier.stringify(big_ast)
        with open(output, "wt") as f:
            f.write(c_src)

    def add_global_types(self, global_types):
        for type in global_types:
            if type.c_name not in self.global_type_reg:
                self.global_type_reg[type.c_name] = type

def parse_module(input, module_name):
    # TODO remove the dict format
    if not path.exists(input):
        raise ValueError(f"Input {input} doesn't exist")
    elif path.isfile(input):
        return {
            module_name: [parse_file(input)]
        }
    else:
        asts = []
        for entry in sorted(os.scandir(input), key=lambda e: e.name):
            if entry.name.endswith(".xy") and entry.is_file():
                asts.append(parse_file(entry.path))
        return {
            module_name: asts
        }


def parse_file(fn):
    code = open(fn, "rt").read()
    src = Source(fn, code)
    return parse_code(src)

def compile_project(project, module_path, rich_errors=False, abort_on_unhandled=True):
    # TODO remove that function
    print("Compiling...")
    res = {}
    builder = Builder("", rich_errors=rich_errors, abort_on_unhandled=abort_on_unhandled)
    builder.compile_builtins()
    for module_name, asts in project.items():
        header, c_srcs = compile_module(builder, module_name, asts, module_path)
        builder.module_cache[module_name] = CompiledModule(header, c_srcs)
        if header.ctx.entrypoint_obj is not None:
            builder.entrypoint_module_names.append(module_name)
        builder.add_global_types(header.ctx.global_types)

    if len(builder.entrypoint_module_names) == 1:
        module = builder.module_cache[builder.entrypoint_module_names[0]]
        maybe_add_main(module.header.ctx, module.source, len(builder.global_type_reg) > 0, "xy.sys" in builder.module_cache)
    elif len(builder.entrypoint_module_names) > 0:
        raise ValueError("Multiple entry points found")

    if len(builder.global_type_reg) > 0:
        dummy_ast = c.Ast()
        gen_global_stack(builder.global_type_reg, dummy_ast)
        builder.module_cache["__XY__GLOBAL_STACK_AST"] = CompiledModule(None, dummy_ast)

    big_ast = c.Ast()
    for module in builder.module_cache.values():
        big_ast.merge(module.source)

    res[module_name + ".c"] = big_ast
    return res