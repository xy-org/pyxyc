#!/usr/bin/env python3
import argparse
from xyc.builder import Builder
from xyc.parser import ParsingError
from xyc.compiler import CompilationError

def main(cli_args=None):
    parser = argparse.ArgumentParser(
        prog='xyc',
        description='The XY compiler',
    )
    parser.add_argument('path')
    parser.add_argument('-o', '--output', required=False)
    parser.add_argument(
        '-C', '--compile-only', action='store_true', default=False,
        help="Run only the xy to c compilation, producing c source files"
    )
    args = parser.parse_args(args=cli_args)

    builder = Builder(
        input=args.path, output=args.output,
        compile_only=args.compile_only
    )
    try:
        builder.build()
    except (ParsingError, CompilationError) as e:
        print(e)

if __name__ == '__main__':
    main()
