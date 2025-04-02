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
    "strings/stringCtor",
    "entrypoint",
    "entrypoint_priority",
    "arrays/arrays",
    "arrays/arrayComprehension",
    "arrays/listLiterals",
    "cinterop/cimport",
    "ifs/ifs",
    "ifs/ifs2",
    "ifs/ifs3",
    "loops/whiles",
    "loops/dowhiles",
    "slices",
    "fors/for1",
    "fors/for2",
    "fors/for3",
    "fors/for4",
    "fors/for5",
    "loops/continue",
    "pointers",
    "pseudoParams",
    "errors",
    "nameCollisions",
    "opOverloading",
    "globalConstants",
    "funcs",
    "strings/stringInterpolation",
    "strings/embedFile",
    "namedArguments",
    "namedFields",
    "positionalTags",
    "indices/pseudoFields",
    "guards",
    "indices/indices",
    "indices/refValue",
    "dtors/dtors1",
    "dtors/dtors2",
    "dtors/dtors3",
    "dtors/dtors4",
    "paramsVsArgs",
    "boundaryExpr/boundaryExpr1",
    "boundaryExpr/boundaryExpr2",
    "boundaryExpr/boundaryExpr3",
    # TODO "properties",
    "exitWithError",
    "ctti/fieldsof",
    "injectScopeArgs",
    "callbacks/callbacks1",
    "callbacks/callbacks2",
    "callbacks/callbacks3",
    "callbacks/callbacks4",
    "macros1",
    "move/moveOperators1",
    "move/moveOperators2",
    "move/moveOperators3",
    "move/moveOperators4",
    "move/moveOperators5",
    "splitNamespaces",
    "cinterop/usingCtypes",
    "bitwiseOperations/bitBasics",
    "bitwiseOperations/bitwiseOps",
    "indices/enums/enums",
    "indices/enums/enums2",
    "indices/flags/flags",
    "logicCmp/cmpBools",
    "logicCmp/cmpBits",
    "logicCmp/shortcircuit",
    "ctti/srcLocFuncs",
])
def test_c_compilation(resource_dir, filename):
    module_name=os.path.basename(filename)
    src_path=str(resource_dir / "xy_c_compile_resources" / f"{filename}.xy")
    project = builder.parse_module(
        src_path,
        module_name=module_name
    )
    c_project = builder.compile_project(project, os.path.dirname(src_path))
    assert len(c_project) == 1
    assert f"{module_name}.c" in c_project
    c_act = stringify(c_project[f"{module_name}.c"])

    c_exp = open(resource_dir / "xy_c_compile_resources" / f"{filename}.c").read()
    assert c_act == c_exp


code_ast = [
    ("""def main() -> void {
        arr: @Int[];
    }""",
    "Only pseudo params are allowed to have a length not known at compile time"),
    ("""def func(nums: @Int[]) -> void {
    }""",
    "Only pseudo params are allowed to have a length not known at compile time"),
]
@pytest.mark.parametrize("code, err_msg", code_ast)
def test_arrays_common_errors(code, err_msg, tmp_path):
    fn = tmp_path / "test.xy"
    fn.write_text(code)

    project = builder.parse_module(str(fn), module_name="test")
    with pytest.raises(CompilationError, match=err_msg):
        builder.compile_project(project, tmp_path)

code_ast = [
    ("""def func(t: MissingType) -> void {
    }""",
    "Cannot find type"),
    ("""
    def func(x: Int, y: Int) -> Int {
        return x + y;
    }
     

    def main() -> void {
        x : Long = 0;
        y : Int = 0;
        func(x, y);
    }
    """,
    "Cannot find function"),
    ("""
    import posix~[CLib{headers=@{"errno.h"}}] in c;

    def main() -> Int {
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
        builder.compile_project(project, tmp_path)


@pytest.mark.parametrize("module", [
    "funcAndStruct",
    "submodules",
    "paramDefaultValue",
    "boundaryExprMultiModule",
    "visibility/package1",
    "visibility/package2",
    "visibility/package3",
    "structVisibility/package2",
    "multipleMacros",
    "macrosAndFuncs",
    "crossModuleSelect",
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