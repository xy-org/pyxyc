import os
from os import path
from xyc.ast import Source
from xyc.parser import parse_code
from xyc.compiler import compile_module
import xyc.cstringifier as cstringifier
from dataclasses import dataclass
import xyc.cast as c

@dataclass
class CompiledModule:
    header: any = None
    source: c.Ast = None

class Builder:
    def __init__(self, input: str, output: str | None = None):
        self.input = input
        self.output = output
        if not output:
            self.output = path.splitext(
                path.basename(path.abspath(self.path))
            )[0]
        self.module_cache = {}
        self.search_paths = []

    def build(self):
        module_name = path.basename(self.input)
        if "." in module_name:
            module_name = path.splitext(module_name)[0]

        self.do_compile_module(module_name, self.input)
        self.write_output(list(self.module_cache.values()))

    def import_module(self, module_name: str):
        if module_name in self.module_cache:
            return self.module_cache[module_name].header

        module_path = self.locate_module(module_name)
        header, _ = self.do_compile_module(module_name, module_path)

        return header
    
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
        raise ValueError(f"Cannot find module {'.'.join(module_name)}")

    def write_output(self, modules: list[CompiledModule]):
        # merge all into one big .c file
        big_ast = c.Ast()
        for module in modules:
            big_ast.merge(module.source)
        c_src = cstringifier.stringify(big_ast)
        with open(self.output, "wt") as f:
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
    for module_name, asts in project.items():
        res[module_name + ".c"] = compile_module(None, module_name, asts)[1]
    return res