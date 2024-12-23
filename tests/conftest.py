import os
import pathlib
import pytest


@pytest.fixture
def resource_dir(request):
    return pathlib.Path(os.path.dirname(request.path))