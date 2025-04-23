from setuptools import setup, find_packages

setup(
    name='marstimeconverter',
    version='0.1.0',
    description='Convert UTC time to Martian time (Mars Sol Date, LMST, etc.)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Gregory S.',
    url='https://github.com/GregS1t/marstimeconverter',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'mars-time=marstimeconverter.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
    license='MIT',
)
