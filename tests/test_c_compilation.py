import os.path
import pytest
import pathlib
from xyc import xyc
from xyc.cast import stringify

@pytest.fixture
def resource_dir(request):
    return pathlib.Path(os.path.dirname(request.path))

def test_c_compilation(resource_dir):
    project = xyc.parse_project(
        str(resource_dir / "xy_c_compile_resources" / "noop.xy")
    )
    c_project = xyc.compile_project(project)
    assert len(c_project) == 1
    assert "noop.c" in c_project
    c_act = stringify(c_project["noop.c"])

    c_exp = open(resource_dir / "xy_c_compile_resources" / "noop.c").read()
    assert c_act == c_exp