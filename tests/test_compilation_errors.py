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
    get(?[], int) -> Ptr
    get(?[], uint) -> Ptr
    get(?[], Size) -> Ptr
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
    assert exp_err_msg == err_msg, f"Error\n{err_msg}\n"\
           f"Doesnt match pattern:\n {exp_err_msg}"
