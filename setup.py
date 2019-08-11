from setuptools import setup, find_packages
from nhentai_downloader import __version__,__author__,__email__,__repo_url__


with open("requirements.txt") as file:
    requirements = file.read().splitlines()
    
with open("README.md", encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='nhentai-downloader',
   
    version = __version__,
    packages = find_packages(),
    author=__author__,
    author_email=__email__,
    keywords='nhentai, doujinshi',
    description="Nhentai doujinshi fetcher and downloader",
    package_data = {
        "nhentai_data" : [".commit_date","requirements.txt","LICENSE","README.md"]
        },
    #include_package_data=True,
    
     #data_files = [("", [".commit_date","requirements.txt"])],
     zip_safe=False,
    install_requires=requirements,
    license = 'Apache',
    url = __repo_url__,
    download_url = 'https://gitlab.com/DukeValentine/nhentai-downloader/-/archive/master/nhentai-downloader-master.tar.gz',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
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

