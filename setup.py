from setuptools import setup, find_packages


setup(
    name='momo',
    version='0.1.0',
    description="Tiny CLI file manager",
    long_description=open('README.md').read(),
    keywords='momo files',
    author='Shichao An',
    author_email='shichao.an@nyu.edu',
    url='https://github.com/shichao-an/momo',
    license='BSD',
    install_requires=open('requirements.txt').read().splitlines(),
    packages=find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'momo = momo.cli:main',
        ],
        'momo.cli': [
            'add = momo.cli:Add',
            'addpath = momo.cli:AddPath',
            'buckets = momo.cli:Buckets',
            'dump = momo.cli:Dump',
            'cd = momo.cli:Chdir',
            'e = momo.cli:External',
            'ls = momo.cli:Ls',
            'pl = momo.cli:Plugin',
            'reload = momo.cli:Reload',
            'rm = momo.cli:Remove',
            'serve = momo.cli:Serve',
            'use = momo.cli:Use',
        ],
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)
