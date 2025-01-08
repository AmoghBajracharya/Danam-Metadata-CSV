import os
import argparse
import pyperclip as pclip

def copy_dirs(path):
	dirs = os.listdir(path)
	pclip.copy("\n".join(dirs))

if __name__ == "__main__":
	
    args = argparse.ArgumentParser(description="copy everything in a folder to clipboard, separated by a line break")	
    args.add_argument("-p", "--path", required=True, help="path of folder")
    args = args.parse_args()

    copy_dirs(args.path)

	
