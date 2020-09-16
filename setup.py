#!/usr/bin/env python

import setuptools

def get_long_description():
    with open('README.rst', 'r') as file:
        text = file.read()
    return text

def get_requirements():
    with open('requirements.txt', 'r') as file:
        text = file.read().splitlines()
    return text

long_description = get_long_description()
requirements = get_requirements()

setuptools.setup(
    name='PyGRB',
    version='1.0.2',
    author='James Paynter',
    author_email='jims.astronomy@gmail.com',
    description='A GRB light-curve analysis package.',
    license='BSD-3',
    long_description=long_description,
    url='https://github.com/JamesPaynter/PyGRB',
    packages=setuptools.find_packages(),
    package_dir = { 'PyGRB' : 'PyGRB'},
    package_data={'PyGRB': ['data/*']},
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6.0, <3.9',
)
