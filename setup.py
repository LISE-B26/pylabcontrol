from distutils.core import setup

# def readme():
#     with open('README.rst') as f:
#         return f.read()

setup(
    name='PythonLab',
    version='0.1.0',
    packages=['', 'src', 'src.gui', 'src.core', 'src.tools', 'src.scripts', 'src.scripts.basic', 'src.plotting',
              'src.instruments', 'src.data_processing', 'src.labview_fpga_lib.old', 'src.labview_fpga_lib.read_fifo',
              'src.labview_fpga_lib.galvo_scan', 'src.labview_fpga_lib.read_ai_ao',
              'src.labview_fpga_lib.pid_loop_simple', 'src.labview_fpga_lib.labview_helper_functions',
              'tests', 'tests.core_tests',
              'tests.scripts_tests', 'tests.qt_creator_gui', 'tests.instrument_tests'],
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
    install_requires=[
        'pyserial',
        'trackpy',
        'pythonnet',
        'pyvisa'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points = {
        'console_scripts': ['PythonLabGui = command_line:main']
    }
)
