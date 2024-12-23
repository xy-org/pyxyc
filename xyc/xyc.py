#!/usr/bin/env python3
import argparse
from xyc.builder import Builder

def main():
    parser = argparse.ArgumentParser(
        prog='xyc',
        description='The XY compiler',
    )
    parser.add_argument('path')
    parser.add_argument('-o', '--output', required=False)
    args = parser.parse_args()

    builder = Builder(input=parser.path, output=parser.output)
    builder.build()

if __name__ == '__main__':
    main()
