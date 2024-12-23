import os
from os import path
import subprocess
from xyc.ast import Source
from xyc.parser import parse_code
from xyc.compiler import compile_module, compile_ctti, compile_builtins
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
                 package_paths: list[str] = [], builtin_lib_path: str = None):
        self.input = input
        self.output = output
        self.project_name = path.splitext(path.basename(path.abspath(input)))[0]
        if not output:
            self.output = self.project_name
        self.module_cache = {}
        if builtin_lib_path is None:
            builtin_lib_path = path.join(path.dirname(__file__), "libs")
        self.builtin_lib_path = builtin_lib_path
        self.search_paths = package_paths + [builtin_lib_path]
        self.compile_only = compile_only
        self.work_dir = work_dir

    def build(self):
        module_name = path.basename(self.input)
        if "." in module_name:
            module_name = path.splitext(module_name)[0]

        self.compile_builtins()
        self.do_compile_module(module_name, self.input)
        self.do_build()

    def import_module(self, module_name: str):
        if module_name in self.module_cache:
            return self.module_cache[module_name].header
        
        if module_name == "xy.ctti":
            self.compile_ctti()
            return self.module_cache[module_name].header

        module_path = self.locate_module(module_name)
        header, _ = self.do_compile_module(module_name, module_path)

        return header
    
    def compile_builtins(self):
        builtins_module_name = "xy.builtins"
        module_path = path.join(self.builtin_lib_path, "xy", "builtins")
        if not path.exists(module_path):
            raise ValueError(f"Cannot locate the 'xy' library at {module_path}")
        module_ast = parse_module(module_path, builtins_module_name)

        header, c_srcs = compile_builtins(
            self, builtins_module_name, list(module_ast.values())[0]
        )

        self.module_cache[builtins_module_name] = CompiledModule(header, c_srcs)

    def compile_ctti(self):
        ctti_module_name = "xy.ctti"
        module_path = path.join(self.builtin_lib_path, "xy", "ctti")
        if not path.exists(module_path):
            raise ValueError(f"Cannot locate the 'xy' library at {module_path}")
        module_ast = parse_module(module_path, ctti_module_name)

        header, c_srcs = compile_ctti(
            self, ctti_module_name, list(module_ast.values())[0]
        )

        self.module_cache[ctti_module_name] = CompiledModule(header, c_srcs)

    def do_compile_module(self, module_name: str, module_path: str):
        module_ast = parse_module(module_path, module_name)
        assert len(module_ast) == 1
        header, c_srcs = compile_module(
            self, module_name, list(module_ast.values())[0]
        )
        self.module_cache[module_name] = CompiledModule(header, c_srcs)
        return header, c_srcs
    
    def locate_module(self, module_name: str):
        search_paths = self.search_paths
        for path in search_paths:
            module_path = os.path.join(path, *(module_name.split('.')))
            if os.path.exists(module_path):
                return module_path
        raise ValueError(f"Cannot find module {module_name}")
    
    def do_build(self):
        if self.compile_only:
            self.write_output(list(self.module_cache.values()), self.output)
        else:
            os.makedirs(self.work_dir, exist_ok=True)
            tmp_file = path.join(self.work_dir, f"{self.project_name}.c")
            self.write_output(list(self.module_cache.values()), tmp_file)
            self.run_cc([tmp_file], self.output)

    def run_cc(self, files, output):
        cc_proc = subprocess.run(
            ["clang", "-std=c99", "-Wall", *files, "-o", output],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if cc_proc.returncode != 0:
            print("Compilation failed with:")
            print(cc_proc.stdout)
            print("If you are calling any c method directly please review "
                  "your code. If you think it is a problem with the Xy compiler"
                  "please report it at TBD.")

    def write_output(self, modules: list[CompiledModule], output):
        # merge all into one big .c file
        big_ast = c.Ast()
        for module in modules:
            big_ast.merge(module.source)
        c_src = cstringifier.stringify(big_ast)
        with open(output, "wt") as f:
            f.write(c_src)

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
        for entry in os.scandir(input):
            if entry.name.endswith(".xy") and entry.is_file():
                asts.append(parse_file(entry.path))
        return {
            module_name: asts
        }


def parse_file(fn):
    code = open(fn, "rt").read()
    src = Source(fn, code)
    return parse_code(src)

def compile_project(project):
    # TODO remove that function
    print("Compiling...")
    res = {}
    builder = Builder("")
    builder.compile_builtins()
    for module_name, asts in project.items():
        header, c_srcs = compile_module(builder, module_name, asts)
        builder.module_cache[module_name] = CompiledModule(header, c_srcs)

    big_ast = c.Ast()
    for module in builder.module_cache.values():
        big_ast.merge(module.source)

    res[module_name + ".c"] = big_ast
    return res