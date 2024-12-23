import subprocess
import pytest
import xyc.xyc as xyc

@pytest.mark.parametrize("testname, output", [
    ("helloworldSelfContained", "Hello World\n"),
    ("helloworldSelfContained2", "Hello World\n"),
])
def test_end_to_end(testname, output, tmp_path, resource_dir):
    test_base = resource_dir / "end_to_end" / testname
    if not test_base.exists():
        test_base = test_base.with_suffix(".xy")
        assert test_base.exists()
    executable = tmp_path / testname
    xyc.main([str(test_base), "-o", str(executable)])
    assert executable.exists()

    proc = subprocess.run([str(executable)], capture_output=True, text=True)
    assert proc.returncode == 0

    assert proc.stdout == output