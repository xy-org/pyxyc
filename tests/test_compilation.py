import os.path
import pytest
import pathlib
from xyc import xyc
from xyc.cstringifier import stringify
from xyc.compiler import CompilationError

@pytest.fixture
def resource_dir(request):
    return pathlib.Path(os.path.dirname(request.path))


@pytest.mark.parametrize("filename", [
    "noop",
    "typeInferenceBasic",
    "typeInferenceAdvanced",
    "funcOverloadingSimple",
    "stringCtor",
    "entrypoint",
    "arrays",
    # "cimport",
])
def test_c_compilation(resource_dir, filename):
    project = xyc.parse_project(
        str(resource_dir / "xy_c_compile_resources" / f"{filename}.xy")
    )
    c_project = xyc.compile_project(project)
    assert len(c_project) == 1
    assert f"{filename}.c" in c_project
    c_act = stringify(c_project[f"{filename}.c"])

    c_exp = open(resource_dir / "xy_c_compile_resources" / f"{filename}.c").read()
    assert c_act == c_exp


code_ast = [
    ("""def main() -> void {
        arr: int[];
    }""",
    "Arrays must have a length known at compile time"),
    ("""def func(nums: int[]) -> void {
    }""",
    "Arrays must have a length known at compile time"),
]
@pytest.mark.parametrize("code, err_msg", code_ast)
def test_arrays_common_errors(code, err_msg, tmp_path):
    fn = tmp_path / "test.xy"
    fn.write_text(code)

    project = xyc.parse_project(str(fn))
    with pytest.raises(CompilationError, match=err_msg):
        xyc.compile_project(project)