from setuptools import find_packages, setup
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

setup(
    name="xyc",
    version='0.1',
    ext_modules=cythonize(
        [
           Extension('xyc.*', ['xyc/*.py']),
        ],
        build_dir="build_cythonize",
        compiler_directives={
            'language_level' : "3",
            'always_allow_keywords': True,
        },
    ),
    cmdclass=dict(
        build_ext=build_ext
    ),
    packages=['xyc'],
)
