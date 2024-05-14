from setuptools import setup
from common.constants import VERSION

setup(
    name='djuliAPIpython',
    version=VERSION,
    description='Djuli API Python package',
    author='Linhongjia Xiong, Sindre Søpstad, Jose Montoya',
    author_email='linhongjia.xiong@zimmerpeacock.com, sindre@zimmerpeacock.com, jose.montoya@zimmerpeacock.com',
    packages=['djuliAPIpython'],
    install_requires=[
        'cycler==0.11.0',
        'imageio==2.10.4',
        'joblib==1.1.0',
        'kiwisolver==1.3.2',
        'matplotlib==3.4.3',
        'networkx==2.6.3',
        'numpy==1.23.3',
        'pandas==1.3.4',
        'Pillow==8.4.0',
        'pyparsing==3.0.6',
        'python-dateutil==2.8.2',
        'python-multipart==0.0.5',
        'pytz==2021.3',
        'PyWavelets==1.2.0',
        'scikit-image==0.18.3',
        'scikit-learn==1.0.1',
        'scipy==1.9.1',
        'six==1.16.0',
        'tifffile==2021.11.2',
        'impedance==1.4.0',
        'schemdraw==0.8',
        'fastapi==0.89.1',
        'pydantic==1.10.4',
        'uvicorn==0.20.0'
    ],
)