import setuptools


with open('README.rst', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r', encoding='utf-8') as fh:
    INSTALL_REQUIRES = [line.strip() for line in fh if line]

# INSTALL_REQUIRES = [
#     "idelib",
#     "pandas",
#     "jinja2",  # required for pandas.DataFrame.style
#     ]

TEST_REQUIRES = [
    "pytest",
    "pytest-cov",
    ]

EXAMPLE_REQUIRES = [
    ]

setuptools.setup(
        name='endaq-python-ide',
        version='1.0.0a1',
        author='Mide Technology',
        author_email='help@mide.com',
        description='A comprehensive, user-centric Python API for working with enDAQ data and devices',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/MideTechnology/endaq-python',
        license='MIT',
        classifiers=['Development Status :: 2 - Pre-Alpha',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Programming Language :: Python :: 3.5',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Topic :: Scientific/Engineering',
                     ],
        keywords='ebml binary ide mide endaq',
        packages=['endaq.ide'],
        package_dir={'endaq.ide': './endaq/ide'},
        install_requires=INSTALL_REQUIRES,
        extras_require={
            'test': INSTALL_REQUIRES + TEST_REQUIRES,
            'example': INSTALL_REQUIRES + EXAMPLE_REQUIRES,
            },
)
