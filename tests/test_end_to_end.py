import subprocess
import pytest
import xyc.xyc as xyc

@pytest.mark.parametrize("testname, output, valgrind", [
    ("helloworldSelfContained", "Hello World\n", False),
    ("helloworldSelfContained2", "Hello World\n", False),
    ("helloworld", "Hello World\n", False),
    ("globalConstants", "Speed of Light = 299792458 m/s\nPi = 3.14\n", False),
    ("argEval", "In Func 1\nIn Func 2\nIn Func 1\nIn Func 2\nIn Take2\nIn Func 1\nIn Func 2\nIn Ignore Second\n", False),
    ("operatorSlices", "In compute\nIn len\nSlice 42 52\nSlice 52 62\n", False),
    ("dynamicArray", "len=100\nres=-9900\n", True),
])
def test_end_to_end(testname, output, tmp_path, resource_dir, valgrind):
    test_base = resource_dir / "end_to_end" / testname
    if not test_base.exists():
        test_base = test_base.with_suffix(".xy")
        assert test_base.exists()
    executable = tmp_path / testname
    assert xyc._main([
        str(test_base),
        "-P", str(resource_dir / "end_to_end_deps/libxy"),
        "-o", str(executable)
    ]) == 0
    assert executable.exists()

    if valgrind:
        vg_log_file = str(tmp_path / "valgrind.log")
        pr_to_run = [
            "valgrind", "--leak-check=full", "--log-file=" + vg_log_file,
            str(executable)
        ]
    else:
        pr_to_run = [str(executable)]

    proc = subprocess.run(pr_to_run, capture_output=True, text=True)

    assert proc.returncode == 0
    assert proc.stdout == output

    if valgrind:
        vg_log = open(vg_log_file).read()
        assert "definitely lost: " not in vg_log
        assert "ERROR SUMMARY: 0 errors" in vg_log, vg_log