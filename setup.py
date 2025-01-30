#!/usr/bin/env python
from setuptools import setup

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="api",
    version="0.0.0",
    description="MAIN API",
    author="HexaTransit",
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
