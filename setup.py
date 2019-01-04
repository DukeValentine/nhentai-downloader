from setuptools import setup, find_packages
from nhentai_downloader import __version__,__author__,__email__


with open("requirements.txt") as file:
    requirements = file.read().splitlines()


setup(
    name='nhentai-downloader',
    version = __version__,
    packages = find_packages(),
    author=__author__,
    author_email=__email__,
    keywords='nhentai, doujinshi',
    description="Nhentai doujinshi fetcher and downloader",
    include_package_data=True,
     zip_safe=False,
    install_requires=requirements,
    license = 'Apache',
    
    entry_points={
        'console_scripts': [
            'nhentai-downloader = nhentai_downloader.nhentai:main',
    ]},
        
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        
    ],
    
)

