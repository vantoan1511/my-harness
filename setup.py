from setuptools import setup

setup(
    name="my-harness",
    version="0.1.0",
    py_modules=["harness"],
    include_package_data=True,
    package_data={
        "": ["template/**/*", "packs/**/*", "scripts/*", "assets/*"],
    },
    entry_points={
        "console_scripts": [
            "harness=harness:main",
        ],
    },
)
