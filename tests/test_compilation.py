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
    "funcRecursive",
    "stringCtor",
    "entrypoint",
    "entrypoint_priority",
    "arrays/arrays",
    "arrays/arrayComprehension",
    "cimport",
    "ifs",
    "ifs2",
    "ifs3",
    "whiles",
    "dowhiles",
    "slices",
    "for1",
    "for2",
    "for3",
    "for4",
    "for5",
    "continue",
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
    "indices",
    "refValue",
    "dtors1",
    "dtors2",
    "paramsVsArgs",
    "boundaryExpr1",
    "boundaryExpr2",
    "boundaryExpr3",
    # TODO "properties",
    "exitWithError",
    "fieldsof",
    "injectScopeArgs",
    "callbacks1",
    "callbacks2",
    "callbacks3",
    "callbacks4",
    "macros1",
    "moveOperators1",
    "moveOperators2",
    "moveOperators3",
])
def test_c_compilation(resource_dir, filename):
    module_name=os.path.basename(filename)
    project = builder.parse_module(
        str(resource_dir / "xy_c_compile_resources" / f"{filename}.xy"),
        module_name=module_name
    )
    c_project = builder.compile_project(project)
    assert len(c_project) == 1
    assert f"{module_name}.c" in c_project
    c_act = stringify(c_project[f"{module_name}.c"])

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
    import posix~[CLib{headers=@{"errno.h"}}] in c;

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
    "boundaryExprMultiModule",
    "visibility/package1",
    "visibility/package2",
    "visibility/package3",
    "structVisibility/package2",
])
def test_module_compilation(resource_dir, module, tmp_path):
    base_dir = resource_dir / "multi_src"
    output_fn = tmp_path / f"{module.replace('/', '.')}.c"
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