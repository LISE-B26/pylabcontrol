from setuptools import setup, find_packages
from pylabcontrol import __version__ as current_version

# NOTES for updating this file:
# 1) for version update in the pylabcotnrol.__init__
# 2) update the following comment_on_changes
comment_on_changes = 'Added the arc option to select_points (used in script_iterator). Also added more error msg when saving of gui config fails.'

setup(
    name='pylabcontrol',
    version=current_version,
    packages=find_packages(),
    package_data={'pylabcontrol': ['gui/ui_files/*ui']},
    url='https://github.com/LISE-B26/pylabcontrol',
    license='GPL',
    author='Arthur Safira, Jan Gieseler, and Aaron Kabcenell',
    author_email='b26lab@hotmail.com',
    description='Python Laboratory Control Software',
    keywords='laboratory experiment control',
    long_description=comment_on_changes,
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
