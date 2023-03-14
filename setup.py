from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='dcm_parser',
    version='0.2.2', 
    description='A lightning DICOM Parser',
    url='https://github.com/PL97/DICOM_Parser',
    author='Le Peng',
    author_email='peng0347@umn.edu',
    license='MIT',
    packages=['dcm_parser'],
    keywords=['dcm', 'dicom', 'meta', 'dicom_header', 'png'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
