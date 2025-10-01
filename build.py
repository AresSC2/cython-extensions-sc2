import os
import shutil

import numpy
from Cython.Build import cythonize
from setuptools import Distribution, Extension
from setuptools.command.build_ext import build_ext

link_args = []
include_dirs = [numpy.get_include()]
libraries = []


def build():
    source_files = []
    for root, directories, files in os.walk("cython_extensions"):
        for file in files:
            if file.endswith("pyx"):
                source_files.append(os.path.join(root, file))

    extensions = cythonize(
        Extension(
            name="cython_extensions.bootstrap",
            sources=source_files,
            include_dirs=include_dirs,
        ),
        compiler_directives={"binding": True, "language_level": 3},
    )

    distribution = Distribution({
        "name": "extended",
        "ext_modules": extensions,
        "package_dir": {"": "."}
    })

    cmd = build_ext(distribution)
    cmd.ensure_finalized()
    cmd.run()

    # Copy built extensions back to the project
    for output in cmd.get_outputs():
        relative_extension = os.path.relpath(output, cmd.build_lib)
        shutil.copyfile(output, relative_extension)
        mode = os.stat(relative_extension).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_extension, mode)


if __name__ == "__main__":
    build()
