#!/usr/bin/env python3

import setuptools
from tchess import VERSION

readme_f = open('README.md', 'r')
long_description = readme_f.read()
readme_f.close()

setuptools.setup(
    name="tchess",
    version=VERSION,
    author="parsa shahmaleki",
    author_email="parsampsh@gmail.com",
    description="The Chess game in terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parsampsh/tchess",
    packages=setuptools.find_packages(),
    scripts=['bin/tchess'],
    data_files = [('man/man1', ['man/tchess.1']),],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
    install_requires=[
        'Flask >= 1.1',
        'requests >= 2.0',
        'karafs >= 0.1',
    ]
)
