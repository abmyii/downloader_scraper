import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

CLASSIFIERS = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Topic :: Software Development
Operating System :: POSIX
Operating System :: Unix
"""


setuptools.setup(
    name="downloader_scraper",
    version="0.1",
    author="abmyii",
    author_email="abmyii@protonmail.com",
    packages=setuptools.find_packages(),
    description="Downloader and scraper library",
    long_description=long_description,
    url="https://github.com/abmyii/downloader_scraper",
    py_modules=['downloader_scraper'],
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
)
