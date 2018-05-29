from setuptools import setup, find_packages

setup(
    name='pylabcontrol',
    version='0.1a0',
    packages=find_packages(),
    package_data={'pylabcontrol': ['gui/ui_files/*ui']},
    url='https://github.com/LISE-B26/pylabcontrol',
    license='GPL',
    author='Arthur Safira, Jan Gieseler, and Aaron Kabcenell',
    author_email='asafira@fas.harvard.edu',
    description='Python Laboratory Control Software',
    keywords='laboratory experiment control',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        ],
    install_requires=[
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'pyyaml',
        'PyQt5',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points={
        'console_scripts': ['pylabcontrol = pylabcontrol.gui.launch_gui:launch_gui']
    }
)
