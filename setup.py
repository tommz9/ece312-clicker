"""Setup file.

Tomas Barton, 2018
"""

import setuptools

setuptools.setup(
    name="ece312_clicker",
    version="0.1.0",
    url="https://github.com/tommz9/ece312-clicker",

    author="Tomas Barton",
    author_email="tommz9@gmail.com",

    description="A simple clicker server for ECE312.",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages('src'),  # include all packages under src
    package_dir={'': 'src'},   # tell distutils packages are under src

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
