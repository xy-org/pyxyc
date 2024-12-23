import os.path
import pytest
import pathlib
import xyc.builder as builder
from xyc.builder import Builder
from xyc.cstringifier import stringify
from xyc.compiler import CompilationError


@pytest.mark.parametrize("filename", [
    "noop",
    "typeInferenceBasic",
    "typeInferenceAdvanced",
    "funcOverloadingSimple",
    "stringCtor",
    "entrypoint",
    "arrays",
    "cimport",
    "ifs",
    "whiles",
    "dowhiles",
    "slices",
    "for1",
    "pointers",
    "pseudoParams",
    "errors",
    "nameCollisions",
    "opOverloading",
    "enums",
    "flags",
    "globalConstants",
    "funcs",
    "stringInterpolation",
    "namedArguments",
    "namedFields",
    "positionalTags",
    "pseudoFields",
    "guards",
    "refs",
    "refValue",
    "dtors1",
    "dtors2",
    "paramsVsArgs",
    # TODO "properties",
])
def test_c_compilation(resource_dir, filename):
    project = builder.parse_module(
        str(resource_dir / "xy_c_compile_resources" / f"{filename}.xy"),
        module_name=filename
    )
    c_project = builder.compile_project(project)
    assert len(c_project) == 1
    assert f"{filename}.c" in c_project
    c_act = stringify(c_project[f"{filename}.c"])

    c_exp = open(resource_dir / "xy_c_compile_resources" / f"{filename}.c").read()
    assert c_act == c_exp


code_ast = [
    ("""def main() -> void {
        arr: int[];
    }""",
    "Only pseudo params are allowed to have a length not known at compile time"),
    ("""def func(nums: int[]) -> void {
    }""",
    "Only pseudo params are allowed to have a length not known at compile time"),
]
@pytest.mark.parametrize("code, err_msg", code_ast)
def test_arrays_common_errors(code, err_msg, tmp_path):
    fn = tmp_path / "test.xy"
    fn.write_text(code)

    project = builder.parse_module(str(fn), module_name="test")
    with pytest.raises(CompilationError, match=err_msg):
        builder.compile_project(project)

code_ast = [
    ("""def func(t: MissingType) -> void {
    }""",
    "Cannot find type"),
    ("""
    def func(x: int, y: int) -> int {
        return x + y;
    }
     

    def main() -> void {
        x : long = 0;
        y : int = 0;
        func(x, y);
    }
    """,
    "Cannot find function"),
    ("""
    import posix~[CLib{headers=["errno.h"]}] in c

    def main() -> int {
        x := c.errno;
        return x;
    }
    """,
    "The types of c symbols cannot be inferred. Please be explicit and specify the type."),
]
@pytest.mark.parametrize("code, err_msg", code_ast)
def test_common_errors(code, err_msg, tmp_path):
    fn = tmp_path / "test.xy"
    fn.write_text(code)

    project = builder.parse_module(str(fn), module_name="test")
    with pytest.raises(CompilationError, match=err_msg):
        builder.compile_project(project)


@pytest.mark.parametrize("module", [
    "funcAndStruct",
    "submodules",
    "paramDefaultValue",
])
def test_module_compilation(resource_dir, module, tmp_path):
    base_dir = resource_dir / "multi_src"
    output_fn = tmp_path / f"{module}.c"
    builder = Builder(
        input=str(base_dir / module),
        output=str(output_fn),
        compile_only=True
    )
    builder.search_paths.append(str(base_dir))

    builder.build()
    c_act = output_fn.read_text()

    c_exp = open(resource_dir / "multi_src" / f"{module}.c").read()
    assert c_act == c_exp