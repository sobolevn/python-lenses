import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, 'readme.rst')) as handle:
        long_desc = handle.read()
except IOError:
    # the readme should get included in source tarballs, but it shouldn't
    # be in the wheel. I can't find a way to do both, so we'll just ignore
    # the long_description when installing from the source tarball.
    long_desc = None

dependencies = [
    'singledispatch',
    'typing;python_version<"3"',
]

documentation_dependencies = [
    'sphinx',
]

optional_dependencies = [
    'pyrsistent',
    'frozendict',
]

test_dependencies = optional_dependencies + [
    'pytest', 'coverage', 'pytest-coverage', 'hypothesis',
    'mypy;python_version>="3.3" and implementation_name=="cpython"'
]

setuptools.setup(
    name='lenses',
    version='0.5.0',
    description='A lens library for python',
    long_description=long_desc,
    url='https://github.com/ingolemo/python-lenses',
    author='Adrian Room',
    author_email='ingolemo@gmail.com',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='lens lenses immutable functional optics',
    packages=setuptools.find_packages(exclude=['tests']),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    install_requires=dependencies,
    tests_require=test_dependencies,
    extras_require={
        'docs': documentation_dependencies,
        'optional': optional_dependencies,
        'tests': test_dependencies,
    },
)
