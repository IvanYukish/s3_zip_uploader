from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.4'
DESCRIPTION = 'Upload zip files to s3'

# Setting up
setup(
    name="s3_zip_uploader_Ivan_Yukish",
    version=VERSION,
    author="Yukish Ivan",
    url='https://github.com/IvanYukish/s3_zip_uploader',
    author_email="<iwan.jukisch@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['boto3', 'requests', 'pytest'],
    keywords=['python', 'zip', 'upload file', 's3'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)