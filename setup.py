# -*- coding: utf-8 -*-


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vpplib",
    version="0.0.3",
    author="Sascha Birk",
    author_email="birk-sascha@web.de",
    description="simulating distributed energy appliances in a virtual power plant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pyosch/vpplib",
    packages=setuptools.find_packages(),
    license='gpl-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    install_requires=[
          'windpowerlib',
          'pvlib',
          'pandapower',
          'simbench',
          'simses',
          'tqdm',
          'pandapower',
          'numba',
          'matplotlib',
          'NREL-PySAM'
          ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)", # https://pypi.org/classifiers/
        "Operating System :: OS Independent",   #hopefully
    ],
    python_requires='>=3.8',
)