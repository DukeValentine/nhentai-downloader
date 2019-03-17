# Nhentai downloader
Python command line program to retrieve information from and download nhentai galleries. 

This project idea was inspired by [RicterZhen nhentai doujinshi downloader](https://github.com/RicterZ/nhentai)

Support for output the found doujinshi in json or a id list

## Instalation

### With pip

```
pip install nhentai-downloader
```

### With setup.py

```
git clone https://gitlab.com/DukeValentine/nhentai-downloader.git
cd nhentai-downloader
python setup.py install
```

## Building the windows binary
The available windows binary is built with pyinstaller, to build it yourself, execute the following in windows or wine:

`pyinstaller ./nhentai_downloader/nhentai.py -F -p ./nhentai_downloader --hidden-import=requests --hidden-import=bs4`

You must have requests and beaultifulSoup4 already installed prior to building the binary
## Available options
To see all command line options for nhentai-downloader, run it with the --help argument:
```
nhentai-downloader --help
```

The expected output is:
```
optional arguments:
  -h, --help            show this help message and exit

Authentication:
  -l LOGIN, --login LOGIN
  -p PASSWORD, --password PASSWORD

Debug:
  -V, --verbose         Print aditional debug information

File options:
  --dir [DIR], -D [DIR]
                        Directory for saved files, defaults to ./nhentai/
  -o OUTPUT_FILENAME, --output OUTPUT_FILENAME
                        Output filename, empty by default
  -i INPUT_FILENAME, --input INPUT_FILENAME
                        Extract doujinshi from input file
  --json                Switch between id list and json outputs

Search options:
  --search              Sets whether it will get doujinshi from favorites or
                        site-wide search
  --id [ID [ID ...]]    Fetch doujinshi from supplied ids
  -t [TAGS [TAGS ...]], --tags [TAGS [TAGS ...]]
                        Narrow doujinshi down by tags
  --page INITIAL_PAGE   Initial page
  --max-page LAST_PAGE  Last page

Download options:
  --download            Download found doujinshi
  --overwrite-disable   Overwrite already downloaded images
  --threads THREADS     How many download threads the program will use
```

## Usage
For more information on usage, please read the full list of options

### Only fetch metadata (don't download)

Do not supply the --download argument. The program by default only fetch metadata



### Download doujinshi by ids
```
nhentai-downloader --download --id ID1 ID2 ID3 ID4
```


### Search and download doujinshi

```
nhentai-downloader --search --download -t TAG1 TAG2 TAG3
```


### Download doujinshi from your favorites

```
nhentai-downloader --login USERNAME --password PASSWORD --download
```


### Download in specified direcory
```
nhentai-downloader --dir /path/to/download [Remaining arguments]
```

The dir argument is also used to determine where the output file will be written


### Do not overwrite already downloaded files


```
nhentai-downloader --overwrite-disable [Remaining arguments]
```


### Restrict initial and max page for fetching

```
nhentai-downloader --search TAG1 TAG2 --page 2 --max-page 4
```

### Have the program output results to a file
To enable output, the output filename must be given. If the format is not specified, the program will assume a id list

For json:
```
nhentai-downloader --json --output doujinshi.json [Remaining options]
```

For id list
```
nhentai-downloader --output list.txt [Remaining options]
```
