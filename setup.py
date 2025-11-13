from setuptools import setup, find_packages

setup(
    name='webex_message_logger',
    version='0.1',
    description='A tool to download and organize Webex messages where you were involved.',
    author='Your Name',
    packages=find_packages(),
    py_modules=['webex_log'],  # change to your actual script filename without .py
    install_requires=[
        'requests',
        'matplotlib',
        'networkx'
    ],
    entry_points={
        'console_scripts': [
            'webex-log=webex_log:main'  # If you define a `main()` in your script
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
