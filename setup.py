import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('VERSION', "r", encoding="utf-8") as version_file:
    version = version_file.read().strip()

setuptools.setup(
    name="nix-check-build-merge",
    version=version,
    author="Florian Brandes",
    author_email="florian.brandes@posteo.de",
    description="This project will allow you to check for build failures all the nixpkgs you maintain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gador/nix-check-build-merge",
    project_urls={
        "Bug Tracker": "https://github.com/gador/nix-check-build-merge/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Unix",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    include_package_data=True,
    package_data={'': ['*.nix' '+.css' '*.js' '*.html']},
    entry_points={
        'console_scripts': [
            'nixcbm = nix_cbm:main',
        ],
    },
)
