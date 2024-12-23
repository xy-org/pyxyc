#!/usr/bin/env python3
import argparse
from os import path
from xyc.parser import parse_code
from xyc.compiler import compile_module
from xyc.ast import Source

def main():
    parser = argparse.ArgumentParser(
        prog='xyc',
        description='The XY compiler',
    )
    parser.add_argument('path')
    parser.add_argument('-o', '--output', required=False)
    args = parser.parse_args()
    
    parsed = parse_project(args.path)

    output = args.output
    if not output:
        output = path.splitext(path.basename(path.abspath(args.path)))[0]
    compile_project(parsed)
    # TODO write to output


def parse_project(input):
    if path.isfile(input):
        virtual_module = path.splitext(path.basename(input))[0]
        return {
            virtual_module: parse_file(input)  # TODO this should be a list
        }
    elif not path.exists(input):
        raise ValueError(f"Input {input} doesn't exist")
    raise ValueError("Compiling multi module projects is NYI")


def parse_file(fn):
    code = open(fn, "rt").read()
    src = Source(fn, code)
    return parse_code(src)

def compile_project(project):
    print("Compiling...")
    res = {}
    for module_name, ast in project.items():
        res[module_name + ".c"] = compile_module(module_name, ast)
    return res

if __name__ == '__main__':
    main()
