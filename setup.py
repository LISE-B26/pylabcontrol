from distutils.core import setup

# def readme():
#     with open('README.rst') as f:
#         return f.read()

setup(
    name='PythonLab',
    version='0.1.0',
    packages=['', 'src', 'src.gui', 'src.core', 'src.tools', 'src.scripts',
              'src.instruments', 'tests'],
    url='https://github.com/LISE-B26/PythonLab',
    license='GPL',
    author='Aaron Kabcenell, Jan Gieseler, and Arthur Safira',
    author_email='',
    # long_description=readme(),
    description='Python Laboratory Control Software',
    keywords='laboratory control',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        ],
    test_suite='nose.collector',
    tests_require=['nose']
)
