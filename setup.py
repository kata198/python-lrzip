#!/usr/bin/env python


#vim: set ts=4 sw=4 expandtab

import os
import sys
from setuptools import setup


if __name__ == '__main__':
 

    dirName = os.path.dirname(__file__)
    if dirName and os.getcwd() != dirName:
        os.chdir(dirName)

    if '--no-deps' in sys.argv:
        requires = []
        sys.argv.remove('--no-deps')
    else:
        requires = ['QueryableList']


    summary = 'Python bindings for LRZIP'

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Exception when reading long description: %s\n' %(str(e),))
        long_description = summary

    setup(name='lrzip',
            version='1.0.0',
            packages=['lrzip'],
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            setup_requires=['cffi>=1.0.0'],
            requires=['cffi'],
            install_requires=['cffi'],
            cffi_modules=["lrzip/build_lrzip.py:ffi"],
            url='https://github.com/kata198/lrzip',
            maintainer_email='kata198@gmail.com',
            description=summary,
            long_description=long_description,
            license='LGPLv3',
            keywords=['lrzip', 'python', 'bindings', 'compression', 'compress', 'decompress', 'lzma', 'gz', 'bzip2', 'rzip', 'zpaq'],
            classifiers=['Development Status :: 4 - Beta',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Programming Language :: Python :: 3.5',
                          'Programming Language :: Python :: 3.6',
                          'Topic :: Software Development :: Libraries :: Python Modules',
            ]
    )

