from setuptools import setup

setup(
    name="my-harness",
    version="0.1.0",
    py_modules=["harness"],
    entry_points={
        "console_scripts": [
            "harness=harness:main",
        ],
    },
)
