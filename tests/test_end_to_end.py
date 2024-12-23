import subprocess
import pytest
import xyc.xyc as xyc

@pytest.mark.parametrize("testname, output", [
    ("helloworldSelfContained", "Hello World\n"),
    ("helloworldSelfContained2", "Hello World\n"),
    ("helloworld", "Hello World\n"),
    ("globalConstants", "Speed of Light = 299792458 m/s\nPi = 3.14\n"),
    ("argEval", "In Func 1\nIn Func 2\nIn Func 1\nIn Func 2\nIn Take2\nIn Func 1\nIn Func 2\nIn Ignore Second\n"),
    ("dynamicArray", "len=100\n"),
])
def test_end_to_end(testname, output, tmp_path, resource_dir):
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

    proc = subprocess.run([str(executable)], capture_output=True, text=True)
    assert proc.returncode == 0

    assert proc.stdout == output