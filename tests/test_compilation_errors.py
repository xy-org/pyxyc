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
src.xy:6:21: error: Cannot find function 'get(Array, int)'
|             a := arr[0];
                      ^
note: Candidates are:
    get(Ptr, int) -> Ptr
    get(Ptr, Size) -> Ptr
    get(?[], int) -> Ptr
    get(?[], uint) -> Ptr
    get(?[], Size) -> Ptr
"""),
    ("""
        def func1(x: int) = x*2
        def test() {
            a := &func1(10);
        }
     """, """\
src.xy:4:19: error: Expression doesn't evaluate to a ref
|             a := &func1(10);
                    ^^^^^
"""),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo ?) -> Ptr~[arg'typeof] {
#             return ptr;
#         }
#      """, """
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo ?) -> Ptr~[arg~[~int]] {
#             return ptr;
#         }
#      """, """
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo ?) -> Ptr~[~arg'typeof] {
#             return ptr;
#         }
#      """, """
# """),
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo ?) -> Ptr~[int] {
#             return ptr~[~arg];
#         }
#      """, """
# """),
# """),
#     ("""
#         def func(a: int) = ~a
#      """, """
# """),

# def func3(ptr: Ptr, arg: pseudo ?) -> Ptr~[<< typeof(a)] {
#     return ptr;
# }

# using a ? param in type expression

#     ("""
#         def func(arg: pseudo ?, ptr: Ptr~[arg'typeof]) -> Ptr~[arg'typeof] {
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
        import doesnt.exist

        def test() {
        }
     """, """\
src.xy:2:9: error: Cannot find module 'doesnt.exist'
|         import doesnt.exist
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
        import xy.ctti
        struct Desc {
            size: Size;
        }
        def parse(args: pseudo ?, desc := [for(f in args'fieldsof) Desc{f'sizeof}]) -> void {
        }
     """, """\
src.xy:6:58: error: Cannot infer type because: Cannot get fields of an unknown type
|         def parse(args: pseudo ?, desc := [for(f in args'fieldsof) Desc{f'sizeof}]) -> void {
                                                           ^^^^^^^^
"""),
    ("""
        import libc~[CLib{headers=["string.h", "stdio.h"]}] in c
        def func(a: int) a
        def test() {
            func(c.external());
        }
     """, """\
src.xy:5:18: error: Cannot determine type of expression
|             func(c.external());
                   ^^^^^^^^^^
"""),
    ("""
        import libc~[CLib{headers=["string.h", "stdio.h"]}] in c
        def func(a: int) a
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
])
def test_compilation_errors(input_src, exp_err_msg, tmp_path, resource_dir):
    executable = tmp_path / "a.out"
    input_fn = str(tmp_path / "src.xy")
    with open(input_fn, "wt") as f:
        f.write(input_src)
    with pytest.raises(CompilationError) as err:
        builder = xyc.setup_builder([
            input_fn,
            "-P", str(resource_dir / "end_to_end_deps/libxy"),
            "-o", str(executable),
            "-c",
        ])
        builder.build()
    err_msg = str(err.value)
    err_msg = err_msg.replace(input_fn[:-len("src.xy")], "")
    # err_msg = err_msg[err_msg.find("src.xy"):]
    assert err_msg == exp_err_msg, f"Error\n{err_msg}\n"\
           f"Doesnt match pattern:\n {exp_err_msg}"
