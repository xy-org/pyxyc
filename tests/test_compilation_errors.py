import re
import pytest
import xyc.xyc as xyc
from xyc.compiler import CompilationError

@pytest.mark.parametrize("input_src, exp_err_msg", [
    ("""
        def func(a: int) {
        }
        def func(a: int) {
        }
     """, """\
src.xy:4:13: error: Function with the same signature already exists: func(int)
|         def func(a: int) {
              ^^^^
src.xy:2:13: note: Previous definition is here
|         def func(a: int) {
              ^^^^
"""),
    ("""
        def func(a: int) {
        }
        def func(a: ubyte) -> int {
        }
        def main() {
            func(0.0);
        }
     """, """\
src.xy:7:13: error: Cannot find function 'func(double)'
|             func(0.0);
              ^^^^
note: Candidates are:
    in module src
        func(int) -> void
        func(ubyte) -> int
"""),
    ("""
        struct Array {
        }
        def main() {
            arr := Array{};
            a := arr[0];
        }
     """, """\
src.xy:6:21: error: Cannot decay 'in(Array) int' because: Cannot find function 'get(Array, int)'
|             a := arr[0];
                      ^
note: Candidates are:
    in module xy.builtins
        *get(Ptr) -> Ptr
        *get(Ptr, int) -> Ptr
        *get(Ptr, Size) -> Ptr
        *get(any[], int) -> Ptr
        *get(any[], uint) -> Ptr
        *get(any[], Size) -> Ptr
"""),
    ("""
        def func1(x: int) = x*2;
        def test() {
            a := &func1(10);
        }
     """, """\
src.xy:4:19: error: Expression doesn't evaluate to a ref
|             a := &func1(10);
                    ^^^^^
"""),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo any) -> Ptr~[arg'typeof] {
#             return ptr;
#         }
#      """, """
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo any) -> Ptr~[arg~[~int]] {
#             return ptr;
#         }
#      """, """
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo any) -> Ptr~[~arg'typeof] {
#             return ptr;
#         }
#      """, """
# """),
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo any) -> Ptr~[int] {
#             return ptr~[~arg];
#         }
#      """, """
# """),
# """),
#     ("""
#         def func(a: int) = ~a
#      """, """
# """),

# def func3(ptr: Ptr, arg: pseudo any) -> Ptr~[<< typeof(a)] {
#     return ptr;
# }

# using a any param in type expression

#     ("""
#         def func(arg: pseudo any, ptr: Ptr~[arg'typeof]) -> Ptr~[arg'typeof] {
#             return ptr;
#         }
#      """, """
# """),
#     ("""
#         def func() -> Ptr {
#             return &10;
#         }
#      """, """
# """),
    ("""
        import doesnt.exist;

        def test() {
        }
     """, """\
src.xy:2:9: error: Cannot find module 'doesnt.exist'
|         import doesnt.exist;
          ^^^^^^^^^^^^^^^^^^^
"""),
    ("""
        def test(arg := func()) {
        }
     """, """\
src.xy:2:25: error: Cannot infer type because: Cannot find function func()
|         def test(arg := func()) {
                          ^^^^
"""),
    ("""
        def parse(args: pseudo struct) -> void {
        }
     """, """\
src.xy:2:19: error: function parameters cannot be of type struct.
|         def parse(args: pseudo struct) -> void {
                    ^^^^
"""),
    ("""
        def parse(args := sys.argc()) -> void {
        }
     """, """\
src.xy:2:27: error: Cannot infer type because: Cannot find symbol
|         def parse(args := sys.argc()) -> void {
                            ^^^
"""),
    ("""
        import xy.ctti;
        struct Desc {
            size: Size;
        }
        def parse(args: pseudo any, desc := @[for(f in args'fieldsof) Desc{f'sizeof}]) -> void {
        }
     """, """\
src.xy:6:61: error: Cannot infer type because: Cannot get fields of an unknown type
|         def parse(args: pseudo any, desc := @[for(f in args'fieldsof) Desc{f'sizeof}]) -> void {
                                                              ^^^^^^^^
"""),
    ("""
        import libc~[CLib{headers=@["string.h", "stdio.h"]}] in c;
        def func(a: int) a;
        def test() {
            func(c.external());
        }
     """, """\
src.xy:5:18: error: Cannot determine type of expression
|             func(c.external());
                   ^^^^^^^^^^
"""),
    ("""
        import libc~[CLib{headers=@["string.h", "stdio.h"]}] in c;
        def func(a: int) a;
        def test() {
            func(c.argc);
        }
     """, """\
src.xy:5:18: error: The types of c symbols cannot be inferred. Please be explicit and specify the type.
|             func(c.argc);
                   ^^^^^^
"""),
    ("""
        struct Str {}
        def func() {
            s := Str~Missing{};
        }
""", """\
src.xy:4:22: error: Cannot find tag
|             s := Str~Missing{};
                       ^^^^^^^
"""),
    ("""
        def fun(a: int, b:long = 0) a;
        def fun(a: int, b:short = 0) b;
        def fun(a: double) a;
     
        def main() {
            fun(0);
        }
     """, """\
src.xy:7:13: error: Multiple function matches for 'fun(int)'
|             fun(0);
              ^^^
note: Candidates are:
    fun(int, [long]) -> int
    fun(int, [short]) -> short
"""),
    ("""
        struct Str {}
        def func() {
            s := Str~Missing{};
        }
     """, """\
src.xy:4:22: error: Cannot find tag
|             s := Str~Missing{};
                       ^^^^^^^
"""),
    ("""
        struct Test~[TagCtor{label="test"}] {}
        def func() {
            tests := @[for (f in $* ~Test()) f];
        }
     """, """\
src.xy:4:20: error: Cannot infer type of empty array
|             tests := @[for (f in $* ~Test()) f];
                     ^
"""),
    ("""
        def main1~EntryPoint() {}
        def main2~EntryPoint() {}
     """, """\
src.xy:3:13: error: Multiple entry points found.
|         def main2~EntryPoint() {}
              ^^^^^
src.xy:2:13: note: Previous entrypoint
|         def main1~EntryPoint() {}
              ^^^^^
"""),
    ("""
        struct Structure {}
        struct Structure {}
     """, """\
src.xy:3:16: error: Struct with same name already defined in module
|         struct Structure {}
                 ^^^^^^^^^
src.xy:2:16: note: Previous definition
|         struct Structure {}
                 ^^^^^^^^^
"""),
    ("""
        struct My_Structure {}
     """, """\
src.xy:2:16: error: Underscores are not allowed in names. For more info go to TBD
|         struct My_Structure {}
                 ^^^^^^^^^^^^
"""),
    ("""
        struct 0Struct {}
     """, """\
src.xy:2:16: error: Names should start with a letter
|         struct 0Struct {}
                 ^^^^^^^
"""),
    ("""
        struct 2Struct {}
     """, """\
src.xy:2:16: error: Names should start with a letter
|         struct 2Struct {}
                 ^^^^^^^
"""),
    ("""
        def my_func() {}
     """, """\
src.xy:2:13: error: Underscores are not allowed in names. For more info go to TBD
|         def my_func() {}
              ^^^^^^^
"""),
    ("""
        def func() {a_b := 10;}
     """, """\
src.xy:2:26: error: Underscores are not allowed in names. For more info go to TBD
|         def func() {a_b := 10;}
                           ^
"""),
    ("""
        def func(_:int=0) {}
     """, """\
src.xy:2:23: error: Underscores are not allowed in names. For more info go to TBD
|         def func(_:int=0) {}
                        ^
"""),
    ("""
import libxy.stdio;

def main~EntryPoint() {
    a := 0;
    print(f"{a}\\n");
}
     """, """\
src.xy:6:11: error: No string constructor registered for prefix "f"
|     print(f"{a}\\n");
            ^^^^^^^^
"""),
    (
        "def func(arg: pseudo ?) {}",
        """\
src.xy:1:22: error: Names should start with a letter
| def func(arg: pseudo ?) {}
                       ^
"""
    )
])
def test_compilation_errors_embedded(input_src, exp_err_msg, tmp_path, resource_dir):
    executable = tmp_path / "a.out"
    input_fn = str(tmp_path / "src.xy")
    with open(input_fn, "wt") as f:
        f.write(input_src)
    with pytest.raises(CompilationError) as err:
        builder = xyc.setup_builder([
            input_fn,
            "-L", str(resource_dir / "end_to_end_deps/"),
            "-o", str(executable),
            "-c",
        ])
        builder.build()
    err_msg = str(err.value)
    err_msg = err_msg.replace(input_fn[:-len("src.xy")], "")
    assert err_msg == exp_err_msg, f"Error\n{err_msg}\n"\
           f"Doesnt match pattern:\n {exp_err_msg}"

@pytest.mark.parametrize("package, exp_err_msg", [
    ("moduleVis", r".*Cannot find function 'func\(\)'.*"),
    ("packageVis/package2", r".*Cannot find function 'func\(\)'.*"),

    ("structModuleVis", r".*Struct 'Struct' is not visible.*"),
    ("structPackageVis/package2", r".*Struct 'Struct' is not visible.*"),

    ("memAliasing1.xy",
     r".*Cannot get a reference to a variable and an element of that variable"\
        " at the same time*"),
])
def test_compilation_errors_src(package, exp_err_msg, tmp_path, resource_dir):
    executable = tmp_path / "a.out"
    input_dir = str(resource_dir / "compile_errors_multi_src" / package)
    with pytest.raises(CompilationError) as err:
        builder = xyc.setup_builder([
            input_dir,
            "-L", str(resource_dir / "end_to_end_deps/"),
            "-o", str(executable),
            "-c",
        ])
        builder.build()
    err_msg = str(err.value)
    assert re.match(exp_err_msg, err_msg) is not None, err_msg
