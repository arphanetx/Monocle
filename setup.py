from setuptools import setup

setup(
    name='monocle',
    version='0.1',
    install_requires=[
        'argparse',
        'rich',
        'setuptools',
        'huggingface_hub',
        'numpy',
        'pyyaml',
        'torchvision',
        'torchaudio',
        'bitsandbytes',
        'accelerate',
        'transformers',
        'torch'
    ],
    entry_points={
        'console_scripts': [
            'monocle = Monocle.monocle:run'
        ]
    }
)
