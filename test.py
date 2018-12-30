import cli
import fetcher


options = cli.option_parser()

print (sys.argv)


print(options.login)
print(options.password)

fetcher.get_doujinshi_data(0)
