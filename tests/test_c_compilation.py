import os.path
import pytest
import pathlib
from xyc import xyc
from xyc.cstringifier import stringify

@pytest.fixture
def resource_dir(request):
    return pathlib.Path(os.path.dirname(request.path))


@pytest.mark.parametrize("filename", [
    "noop",
    "typeInferenceBasic",
    "typeInferenceAdvanced",
    # "stringCtor",
    # "cimport",  # TODO
    # "entry_point",  # TODO
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