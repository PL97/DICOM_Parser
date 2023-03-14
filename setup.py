from setuptools import setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
print(this_directory)
long_description = (this_directory / "README.md").read_text()

setup(
    name='dcm-parser',
    version='0.1.0',    
    description='A lightning DICOM Parser',
    url='https://github.com/PL97/DICOM_Parser',
    author='Le Peng',
    author_email='peng0347@umn.edu',
    license='MIT',
    packages=['dcm-parser'],
    install_requires=['numpy'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
