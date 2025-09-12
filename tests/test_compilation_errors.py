import re
import pytest
import xyc.xyc as xyc
from xyc.compiler import CompilationError

@pytest.mark.parametrize("input_src, exp_err_msg", [
    ("""
        def func(a: Int) {
        }
        def func(a: Int) {
        }
     """, """\
src.xy:4:13: error: Function with the same signature already exists: func(Int)
|         def func(a: Int) {
              ^^^^
src.xy:2:13: note: Previous definition is here
|         def func(a: Int) {
              ^^^^
"""),
    ("""
        def func(a: Int) {
        }
        def func(a: Ubyte) -> Int {
            return 0;
        }
        def main() {
            func(0.0);
        }
     """, """\
src.xy:8:13: error: Cannot find function 'func(Float)' in src
|             func(0.0);
              ^^^^
note: Candidates are:
    in module src
        func(Int) -> void
        func(Ubyte) -> Int
"""),
    ("""
        struct Array {
        }
        def main() {
            arr := Array{};
            a := arr[0];
        }
     """, """\
src.xy:6:21: error: Cannot decay 'Array[ Int ]' because: Cannot find function 'get(Array, Int)' in src
|             a := arr[0];
                      ^
note: Candidates are:
    in module xy.builtins
        *get(Ptr) -> Ptr
        *get(Ptr, Byte) -> Ptr
        *get(Ptr, Ubyte) -> Ptr
        *get(Ptr, Short) -> Ptr
        *get(Ptr, Ushort) -> Ptr
        *get(Ptr, Int) -> Ptr
        *get(Ptr, Uint) -> Ptr
        *get(Ptr, Long) -> Ptr
        *get(Ptr, Ulong) -> Ptr
        *get(Ptr, Size) -> Ptr
        *get(Any[], Byte) -> Ptr
        *get(Any[], Ubyte) -> Ptr
        *get(Any[], Short) -> Ptr
        *get(Any[], Ushort) -> Ptr
        *get(Any[], Int) -> Ptr
        *get(Any[], Uint) -> Ptr
        *get(Any[], Long) -> Ptr
        *get(Any[], Ulong) -> Ptr
        *get(Any[], Size) -> Ptr
        *get(Global) -> Ptr
"""),
    ("""
        def func1(x: Int) = x*2;
        def test() {
            a := &func1(10);
        }
     """, """\
src.xy:4:19: error: Expression doesn't evaluate to a ref
|             a := &func1(10);
                    ^^^^^
"""),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo Any) -> Ptr~[arg'typeof] {
#             return ptr;
#         }
#      """, """
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo Any) -> Ptr~[arg~[~int]] {
#             return ptr;
#         }
#      """, """
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo Any) -> Ptr~[~arg'typeof] {
#             return ptr;
#         }
#      """, """
# """),
# """),
#     ("""
#         def func(ptr: Ptr~int, arg: pseudo Any) -> Ptr~[int] {
#             return ptr~[~arg];
#         }
#      """, """
# """),
# """),
#     ("""
#         def func(a: int) = ~a
#      """, """
# """),

# def func3(ptr: Ptr, arg: pseudo Any) -> Ptr~[<< typeof(a)] {
#     return ptr;
# }

# using a Any param in type expression

#     ("""
#         def func(arg: pseudo Any, ptr: Ptr~[arg'typeof]) -> Ptr~[arg'typeof] {
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
        def parse(args: pseudo Any, desc := @for(f in args'fieldsof) Desc{f'sizeof}) -> void {
        }
     """, """\
src.xy:6:60: error: Cannot infer type because: Cannot get fields of an unknown type
|         def parse(args: pseudo Any, desc := @for(f in args'fieldsof) Desc{f'sizeof}) -> void {
                                                             ^^^^^^^^
"""),
    ("""
        import libc~[Clib{headers=@{"string.h", "stdio.h"}}] in c;
        def func(a: Int) a;
        def test() {
            func(c.external());
        }
     """, """\
src.xy:5:18: error: Cannot determine type of expression
|             func(c.external());
                   ^^^^^^^^^^
"""),
    ("""
        import libc~[Clib{headers=@{"string.h", "stdio.h"}}] in c;
        def func(a: Int) a;
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
src.xy:4:22: error: Cannot find symbol
|             s := Str~Missing{};
                       ^^^^^^^
"""),
    ("""
        def fun(a: Int, b:Long = 0) a;
        def fun(a: Int, b:Short = 0) b;
        def fun(a: Double) a;

        def main() {
            fun(0);
        }
     """, """\
src.xy:7:13: error: Multiple function matches for 'fun(Int)'
|             fun(0);
              ^^^
note: Candidates are:
    fun(Int, [Long])
    fun(Int, [Short])
"""),
    ("""
        struct Str {}
        def func() {
            s := Str~Missing{};
        }
     """, """\
src.xy:4:22: error: Cannot find symbol
|             s := Str~Missing{};
                       ^^^^^^^
"""),
    ("""
        struct Test~[TagCtor{label="test"}] {}
        def func() {
            tests := @for (f in $* ~Test()) f;
        }
     """, """\
src.xy:4:13: error: Cannot infer type of empty array
|             tests := @for (f in $* ~Test()) f;
              ^^^^^
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
src.xy:2:21: error: Underscores are not allowed in names. For more info go to TBD
|         def func() {a_b := 10;}
                      ^^^
"""),
    ("""
        def func(_:Int=0) {}
     """, """\
src.xy:2:18: error: Underscores are not allowed in names. For more info go to TBD
|         def func(_:Int=0) {}
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
    ),
    (
        """def func(x: Int) {
            if (x > 10) {
                a := 10;
            } else {
                func(a);
            }
        }""",
        """\
src.xy:5:22: error: Cannot find variable 'a'
|                 func(a);
                       ^
"""
    ),
    (
        """def fun(x: Any) %x;""",
        """\
src.xy:1:17: error: Functions cannot return a type
| def fun(x: Any) %x;
                  ^
"""
    ),
    (
        """struct MyStruct {
            field: MyStruct;
        }""",
        """\
src.xy:2:13: error: Recursive structs are not possible
|             field: MyStruct;
              ^^^^^^^^^^^^^^^
"""
    ),
    (
        """struct MyStruct {
            field := MyStruct{};
        }""",
        """\
src.xy:2:13: error: Recursive structs are not possible
|             field := MyStruct{};
              ^^^^^
"""
    ),
    (
        """struct MyStruct {
            field : pseudo = MyStruct{0};

            value: Int;
        }""",
        """\
src.xy:2:39: error: Cannot set value for pseudo field `field`. Pseudo fields cannot initialize other pseudo fields.
|             field : pseudo = MyStruct{0};
                                        ^^^
"""
    ),
    (
        """struct MyStruct {
        }

        def f() {
            s := MyStruct{5};
        }
        """,
        """\
src.xy:5:27: error: Too many positional value in struct literal. Provided '1' but type has only '0' fields
|             s := MyStruct{5};
                            ^
"""
    ),
    (
        """struct MyStruct {
        }

        def f() {
            s := MyStruct{missing=5};
        }
        """,
        """\
src.xy:5:27: error: No field named 'missing'
|             s := MyStruct{missing=5};
                            ^^^^^^^
"""
    ),
    (
        """def test() {
            x := 0;
            x := 1;
        }
        """,
        """\
src.xy:3:13: error: Varaible 'x' already defined
|             x := 1;
              ^
src.xy:2:13: note: Previous definition
|             x := 0;
              ^
"""
    ),
    (
        """
        def func1() func2();
        def func2() -> MissingType {}
        """,
        """\
src.xy:3:24: error: Cannot find type 'MissingType'
|         def func2() -> MissingType {}
                         ^^^^^^^^^^^
"""
    ),
    (
        """
        def pointerFun(a: Ptr) -> Ptr {
            return a + 1;
        }
        """,
        """\
src.xy:3:20: error: Cannot do arithmetic with untagged pointers
|             return a + 1;
                     ^^^^^
"""
    ),
    (
        """
        def func() break "Don't call me";
        def main() {
            return func();
        }
        """,
        """\
src.xy:4:20: error: Don't call me
|             return func();
                     ^^^^
"""
    ),
    (
        """
        def test(a: Uint, b: Byte) -> Uint {
            return a + b;
        }
        """,
        """\
src.xy:3:20: error: Cannot find function 'add(Uint, Byte)' in src; Mixed signedness arithmetic is not allowed.
|             return a + b;
                     ^^^^^
"""
    ),
    (
        """
        def test(a: Uint, b: Int) -> Uint {
            return a + b;
        }
        """,
        """\
src.xy:3:20: error: Mixed signedness arithmetic (Uint, Int). Please cast one of the operands to a suitable type.
|             return a + b;
                     ^^^^^
"""
    ),
    (
        """
        def test(a: Uint, b: Int) -> Bool {
            return a > b;
        }
        """,
        """\
src.xy:3:20: error: Mixed signedness arithmetic (Uint, Int). Please cast one of the operands to a suitable type.
|             return a > b;
                     ^^^^^
"""
    ),
    (
        """
        def test() {
            a := 128b;
        }
        """,
        """\
src.xy:3:18: error: Integer constant overflows type 'Byte'
|             a := 128b;
                   ^^^^
"""
    ),
    (
        """
        def test() {
            a := 0x55bb()b;
        }
        """,
        """\
src.xy:3:18: error: Integer constant overflows type 'Byte'
|             a := 0x55bb()b;
                   ^^^^^^^^^
"""
    ),
    (
        """
        def test() {
            a := Int;
        }
        """,
        """\
src.xy:3:13: error: Cannot assign a type to a variable. Did you forget to instantiate it?
|             a := Int;
              ^
"""
    ),
    (
        """
        import c~[Clib{defines=@{""}}] in c;
        def test() {}
        """,
        """\
src.xy:2:34: error: Empty define
|         import c~[Clib{defines=@{""}}] in c;
                                   ^^
"""
    ),
    (
        """
        import c~[Clib{defines=@{" "}}] in c;
        def test() {}
        """,
        """\
src.xy:2:34: error: Empty define
|         import c~[Clib{defines=@{" "}}] in c;
                                   ^^^
"""
    ),
    (
        """
        def test() { 0'addrof; }
        """,
        """\
src.xy:2:24: error: Cannot get address of a const
|         def test() { 0'addrof; }
                         ^^^^^^
"""
    ),

    # mutating an immutable variable
    (
        """
        def fun(a: mut Int) {}

        def test() {
            a := 0;
            fun(a);
        }
        """,
        """\
src.xy:6:17: error: Passing immutable variable as a mutable argument
|             fun(a);
                  ^
src.xy:6:13: note: In call to function fun(Int)
|             fun(a);
              ^^^
"""
    ),
    # TODO test passing an immutable to a mutabale named param
    # TODO test passing a reference to an immutable to a mutable param

    # missing return/error
    (
        """
        def fun() -> void {}

        def test() -> Int {
            fun();
        }
        """,
        """\
src.xy:4:13: error: Missing 'return' or 'error' statement at end of non-void function
|         def test() -> Int {
              ^^^^
"""
    ),
    (
        """
        def test(cond1: Bool) -> Int {
            if (cond1) return 0;
        }
        """,
        """\
src.xy:2:13: error: Missing 'return' or 'error' statement at end of non-void function
|         def test(cond1: Bool) -> Int {
              ^^^^
"""
    ),
    (
        """
        def test(cond1: Bool) -> Int {
            if (cond1) {
                return 0;
            } else {
                # nothing
            }
        }
        """,
        """\
src.xy:2:13: error: Missing 'return' or 'error' statement at end of non-void function
|         def test(cond1: Bool) -> Int {
              ^^^^
"""
    ),

    # ignoring return results
    (
        """
        def func() -> Int {
            return 0;
        }
        def test() {
            func();
        }
        """,
        """\
src.xy:6:13: error: Discarding values is not allowed. Rewrite expression as '_ = <expr>' to ignore the value
|             func();
              ^^^^
note: Discarded value is of type 'Int'
"""
    ),

    # instantiating Any
    (
        """
        def func() {
            a: Any;
        }
        """,
        """\
src.xy:3:13: error: Cannot instantiate pseudo type 'Any'. It serves as a wildcard in func definitions and cannot be instantiated.
|             a: Any;
              ^^^^^^
"""
    ),
    (
        """
        def func() {
            a := Any{};
        }
        """,
        """\
src.xy:3:18: error: Cannot find variable 'Any'
|             a := Any{};
                   ^^^
"""
    ),
    (
        """
        struct Struct {}

        def dtor(s: Struct, num: Int) {}

        def test() {
            s: Struct;
        }
        """,
        """\
src.xy:2:16: error: Type appears to need a dtor by no matching dtor(Struct) found
|         struct Struct {}
                 ^^^^^^
"""
    ),
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
           f"Doesn't match pattern:\n {exp_err_msg}"

@pytest.mark.parametrize("package, exp_err_msg", [
    ("moduleVis", r".*Cannot find function 'func\(\)'.*"),
    ("packageVis/package2", r".*Cannot find function 'func\(\)'.*"),

    ("structModuleVis", r".*Struct 'Struct' is not visible.*"),
    ("structPackageVis/package2", r".*Struct 'Struct' is not visible.*"),

    ("memAliasing1.xy",
     r".*Cannot get a reference to a variable and an element of that variable"\
        " at the same time*"),
    ("memAliasing2.xy",
     r".*Cannot get a reference to a variable and an element of that variable"\
        " at the same time*"),
    ("memAliasing3.xy",
     r".*Cannot get a reference to a variable and an element of that variable"\
        " at the same time*"),
    ("memAliasing4.xy",
     r".*Cannot get a reference to a variable and an element of that variable"\
        " at the same time*"),
    ("memAliasing5.xy",
     r".*Cannot get a reference to a variable and an element of that variable"\
        " at the same time*"),

    ("failedGet.xy", r".*Cannot decay.*Cannot find function.*"),
    ("failedSet.xy", r".*Cannot set.*Can neither set nor decay MyStruct[Flag]*"),

    ("tags/mismatchedTags1.xy", r".*Cannot discard tag 'tag2'(.|\n)*mismatchedTags1.xy:8:20: note: Tag attached here.*"),
    ("tags/mismatchedTags2.xy", r".*Cannot discard tag 'tag2'.*"),
    ("tags/mismatchedTags3.xy", r".*Values for tag 'tag2' differ"),
    ("tags/mismatchedTags4.xy", r".*Values for tag 'tag' differ(.|\n)*mismatchedTags4.xy:6:18: note: Left tag attached here(.|\n)*mismatchedTags4.xy:10:27: note: Right tag attached here"),
    ("tags/mismatchedTags5.xy", r".*Values for tag 'tag' differ"),
    ("tags/mismatchedTags6.xy", r".*Values for tag 'tag' differ"),

    ("recursiveDeps", r".*Cyclical module dependency. Import loop begins here:.*"),
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
