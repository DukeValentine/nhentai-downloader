import argparse
import os


def option_parser():
    parser = argparse.ArgumentParser (description = "Extract information and download doujinshis \n Fetch them from your favorites, searching by tags or by inputing a file with a list of doujinshi \n Ample configuration options")

    auth = parser.add_argument_group('Authentication')
    debug = parser.add_argument_group('Debug')
    file_args = parser.add_argument_group('File options')
    search = parser.add_argument_group('Search options')
    download = parser.add_argument_group('Download options')


    file_args.add_argument ("--dir",'-D', action ="store", nargs='?', default=os.path.join(os.getcwd(),"nhentai"),help ='Directory for saved files, defaults to ./nhentai/')
    file_args.add_argument ('-o','--output', action="store", dest = "output_filename", default = 'doujinshi', help='Output filename, ids.txt by default')
    file_args.add_argument ('-i','--input', action='store', dest = "input_filename", default = "", help = 'Extract doujinshi from input file')
    file_args.add_argument('--json',action = 'store_true', default = False, help = 'Switch between id list and json outputs')


    auth.add_argument ('-l','--login', action="store", dest = "login", default = '')
    auth.add_argument ('-p','--password', action="store", dest = "password",default = '')
    

    debug.add_argument('-V','--verbose', action = "store_true", dest = "verbose", default = False, help = "Print aditional debug information") 

    search.add_argument ('--search', action = "store_true", default = False, help = "Sets whether it will get doujinshi from favorites or site-wide search")
    search.add_argument ('--id', nargs='*',default=[], help = "Fetch doujinshi from supplied ids")
    search.add_argument ('-t','--tags' , action="store", dest = "tags", nargs='*',default=[], help ='Narrow doujinshi down by tags')
    search.add_argument ('--page', action = "store", type=int, dest = "initial_page", default = 1, help = "Initial page")
    search.add_argument ('--max-page', action = "store", type=int, dest = "last_page", default = 0, help = "Last page")


    download.add_argument('--download',action = "store_true", default = False, help = "Download found doujinshi")
    download.add_argument('--overwrite-disable',dest = "overwrite", action = "store_false",default = True, help ="Overwrite already downloaded images")
    download.add_argument("--threads",action = "store", type=int, default = 7, help = "How many download threads the program will use")
    
    
    return (parser.parse_args())
