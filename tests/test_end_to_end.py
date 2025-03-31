import subprocess
import re
import sys
import pytest
import xyc.xyc as xyc

valgrind_supported = "linux" in sys.platform

@pytest.mark.parametrize("testname, output, valgrind", [
    ("helloworldSelfContained", "Hello World\n", False),
    ("helloworldSelfContained2", "Hello World\n", False),
    ("helloworld", "Hello World\n", False),
    ("globalConstants", "Speed of Light = 299792458 m/s\nPi = 3.14\n", False),
    ("argEval", "In Func 1\nIn Func 2\nIn Func 1\nIn Func 2\nIn Take2\nIn Func 1\nIn Func 2\n"
                "In Ignore First\nIn Func 1\nIn Func 2\nIn Ignore Second\n"
                "In Func 1\nIn Func 2\nIn Ignore Both\nIn Func 1\nIn Ignore First\nIn Func 2\nIn Ignore Second\n", False),
    ("operatorSlices", "In compute\nIn len\nSlice 42 52\nSlice 52 62\n", False),
    ("dynamicArray", "len=100\nres=-9900\n", True),
    ("printCliArgs", "--arg1\n2\n3.14\n", False),
    ("ptrBasics", "0 0\n1 1\n2 2\n4 4 2 2\n", True),
    ("printTypeInfo",
r""";; MyStruct comment
struct MyStruct {
    ;; My name
    name: Str; # size=\d+ offset=\d+ alignof=\d+
    ;; Some number
    num: Size; # size=\d offset=\d+ alignof=\d+
    integer: Int; # size=4 offset=\d+ alignof=\d+
    ;; Array of
floats
    arr: Float\[10\]; # size=40 offset=\d+ alignof=\d+
    next: Ptr; # size=\d offset=\d+ alignof=\d+
}\n""", False),
    ("uniqueTmpVarNames", "", False),
    ("strAndIfs", "100", False),
    ("earlyReturn", "", False),
    ("iterWithDtor", "Destroying Iter\n", False),
])
def test_end_to_end(testname, output, tmp_path, resource_dir, valgrind):
    test_base = resource_dir / "end_to_end" / testname
    if not test_base.exists():
        test_base = test_base.with_suffix(".xy")
        assert test_base.exists()
    executable = tmp_path / testname
    assert xyc._main([
        str(test_base),
        "-L", str(resource_dir / "end_to_end_deps/"),
        "-o", str(executable)
    ]) == 0
    assert executable.exists()

    if valgrind_supported and valgrind:
        vg_log_file = str(tmp_path / "valgrind.log")
        pr_to_run = [
            "valgrind", "--leak-check=full", "--log-file=" + vg_log_file,
            str(executable)
        ]
    else:
        pr_to_run = [str(executable)]

    if testname == "printCliArgs":
        pr_to_run.extend(["--arg1", "2", "3.14"])

    proc = subprocess.run(pr_to_run, capture_output=True, text=True)

    assert proc.returncode == 0
    if re.match("^" + output + "$", proc.stdout) is None:
        assert  proc.stdout == output  # provide nice output

    if valgrind_supported and valgrind:
        vg_log = open(vg_log_file).read()
        assert "definitely lost: " not in vg_log
        assert "ERROR SUMMARY: 0 errors" in vg_log, vg_log