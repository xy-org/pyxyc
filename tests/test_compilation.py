import os.path
import pytest
import pathlib
import xyc.builder as builder
from xyc.builder import Builder
from xyc.cstringifier import stringify
from xyc.compiler import CompilationError


@pytest.mark.parametrize("filename", [
    "basic/noop",
    "typeInferenceBasic",
    "basic/arithmatic1",
    "basic/arithmatic2",
    "basic/arithmatic3",
    "basic/arithmatic4",
    "basic/checkedDivision",
    "typeInferenceAdvanced",
    "funcs/funcOverloadingSimple",
    "funcs/funcRecursive",
    "funcs/anyParam1",
    "strings/stringCtor",
    "entrypoint",
    "entrypoint_priority",
    "arrays/arrays",
    "arrays/arrayComprehension",
    "arrays/listLiterals",
    "arrays/modifyingArrays",
    "arrays/arrayAppend",
    #"arrays/arrayTypeInference",
    #"arrays/arrayAddress",
    "cinterop/cimport",
    "ifs/ifs",
    "ifs/ifs2",
    "ifs/ifs3",
    "ifs/ifs4",
    "loops/whiles",
    "loops/while1",
    "loops/while2",
    "loops/while3",
    "loops/while4",
    "loops/dowhile1",
    "loops/dowhile2",
    "loops/dowhile3",
    "slices",
    "fors/for1",
    "fors/for2",
    "fors/for3",
    "fors/for4",
    "fors/for5",
    "fors/for6",
    "fors/for7",
    "loops/continue",
    "pointers",
    "pseudoParams",
    "errors/errors",
    "nameCollisions",
    "opBasics",
    "opOverloading",
    "consts/globalConstants",
    "consts/asFieldValue",
    "consts/arrayConstants",
    "funcs/funcs",
    "funcs/largeParams",
    "strings/stringInterpolation",
    "strings/embedFile",
    "strings/chars",
    "strings/escapes",
    "namedArguments",
    "namedFields",
    "tags/positionalTags",
    "tags/defaultValue",
    "tags/forgettingTags1",
    "tags/forgettingTags2",
    "tags/paramTags1",
    "tags/paramTags2",
    "indices/pseudoFields",
    "errors/guards",
    "errors/richErrors",
    "indices/indices",
    "indices/refValue",
    "indices/settingRef",
    "dtors/dtors1",
    "dtors/dtors2",
    "dtors/dtors3",
    "dtors/dtors4",
    "dtors/dtorsInLogicExpr",
    "dtors/funcParamWithDtor",
    "paramsVsArgs",
    "boundaryExpr/boundaryExpr1",
    "boundaryExpr/boundaryExpr2",
    "boundaryExpr/boundaryExpr3",
    "boundaryExpr/boundaryExpr4",
    "boundaryExpr/boundaryExpr5",
    "structs/properties",
    "exitWithError",
    "ctti/fieldsof",
    "injectScopeArgs",
    "callbacks/callbacks1",
    "callbacks/callbacks2",
    "callbacks/callbacks3",
    "callbacks/callbacks4",
    "callbacks/callbacks5",
    "lambdas/lambdas1",
    "lambdas/lambdas2",
    "lambdas/lambdas3",
    "lambdas/lambdas4",
    "lambdas/lambdas5",
    "lambdas/lambdas6",
    "macros1",
    "move/moveOperators1",
    "move/moveOperators2",
    "move/moveOperators3",
    "move/moveOperators4",
    "move/moveOperators5",
    "move/moveOperators6",
    "move/moveOperators7",
    "funcs/donatedArgs1",
    "funcs/donatedArgs2",
    "funcs/donatedArgs3",
    "funcs/donatedArgs4",
    "funcs/donatedArgs5",
    "funcs/donatedArgs6",
    "funcs/donatedArgs7",
    "funcs/donatedArgs8",
    "splitNamespaces",
    "cinterop/usingCtypes",
    "cinterop/callFuncOnString",
    "cinterop/inlinecBlock",
    "cinterop/defines",
    "cinterop/instantiateCtypes",
    "bitwiseOperations/bitBasics",
    "bitwiseOperations/toBits",
    "bitwiseOperations/bitFloats",
    "bitwiseOperations/bitShifts",
    "bitwiseOperations/bitShiftCmp",
    "bitwiseOperations/bitwiseOps",
    "indices/enums/enums",
    "indices/enums/enums2",
    "indices/flags/flags",
    "logicCmp/cmpBools",
    "logicCmp/cmpBits",
    "logicCmp/cmpNums",
    "logicCmp/cmpNumConsts",
    "logicCmp/cmpPtrs",
    "logicCmp/overloadingCmp",
    "logicCmp/minMax",
    "logicCmp/shortcircuit",
    "logicCmp/mixingAndOr",
    "ctti/srcLocFuncs",
    "ctti/sizeofNoEval",
    "ctti/cmpTypes",
    "funcs/paramTypeEnum",
    "structs/fieldInit",
    "structs/subFieldInit",
    "structs/subInitFunc",
    "structs/moveInStructLit",
    "structs/fieldExternalType",
    "structs/fieldExternalTypeInit",
    "globals/globals1",
    "globals/globals2",
    "errors/handling1",
    "errors/handling2",
    "errors/uncaught1",
    "strings/unstringing",
    "funcs/namedReturn",
    "funcs/namedReturnImplicit",
    "funcs/ignoreRetVal",
    "exprBlocks/exprBlocks1",
    "exprBlocks/exprBlocks2",
    "exprBlocks/exprBlocks3",
    "exprBlocks/exprBlocks4",
    "synonyms/synonym1",
])
def test_c_compilation(resource_dir, filename):
    module_name=os.path.basename(filename)
    src_path=str(resource_dir / "xy_c_compile_resources" / f"{filename}.xy")
    project = builder.parse_module(
        src_path,
        module_name=module_name
    )
    rich_errors = "richErrors" in filename or "uncaught" in filename
    c_project = builder.compile_project(
        project, os.path.dirname(src_path),
        rich_errors=rich_errors, abort_on_unhandled=not rich_errors
    )
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
    import posix~[Clib{headers=@{"errno.h"}}] in c;

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
    "macroErrorAndDtor",
    "globalAndMacro",
    "macroBlockDtor",
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