import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aamp_app",  # This is the name of the package
    version="0.0.1.27",  # The initial release version
    author="Piyush Pahuja",  # Full name of the author
    description="AAMP App",
    long_description=long_description,  # Long description read from the the readme file
    long_description_content_type="text/markdown",
    # packages=setuptools.find_packages(),  # List of all python modules to be installed
    packages=[
        "aamp_app",
        "aamp_app/commands",
        "aamp_app/devices",
        "aamp_app/pages",
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  # Information to filter the project on PyPi website
    python_requires=">=3.6",  # Minimum version requirement of the package
    # py_modules=[
    #     # "aamp_app",
    #     # "command_invoker",
    #     # "commands.*",
    # ],  # Name of the python package
    # package_dir={
    #     "": "src/aamp_app",
    #     # "": "src/aamp_app/commands",
    #     # "devices": "src/devices",
    # },  # Directory of the source code of the package
    install_requires=[
        "certifi",
        "colorama",
        "dash",
        "dash-ace",
        "dash-bootstrap-components",
        "dash-table",
        "mfc",
        "pandas",
        "pdoc",
        "Pillow",
        "pymongo",
        "pyserial",
        "PyVISA",
        "pyyaml",
        "questionary",
        "scipy",
        "slackclient",
        "ximea-py",
        "pyfirmata",
    ],  # Install other dependencies if any
    entry_points={"console_scripts": ["aamp_app=aamp_app.aamp_app:main"]},
)
