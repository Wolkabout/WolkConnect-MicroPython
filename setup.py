import sys

# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup

sys.path.append("..")
import sdist_upip

setup(
    name="micropython-wolk-connect",
    version="0.1.0",
    description="Connectivity package for WolkAbout IoT Platform",
    long_description=open("README.md", "r").read(),
    url="https://github.com/WolkAbout/WolkConnect-MicroPython",
    author="WolkAbout",
    author_email="info@wolkabout.com",
    maintainer="WolkAbout",
    maintainer_email="info@wolkabout.com",
    license="Apache Licence 2.0",
    cmdclass={"sdist": sdist_upip.sdist},
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: Implementation :: MicroPython",
        "Operating System :: Other OS",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Software Development :: Embedded Systems",
    ),
    py_modules=["wolk"],
)

# TODO: cmdclass , package, py_modules
