from setuptools import setup, find_packages

setup(
    name='monocle',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'transformers',
        'torch',
        'argparse',
        'rich',
        'setuptools'
    ],
    entry_points={
        'console_scripts': [
            'llm = Monocle.monocle:run'
        ]
    }
)
