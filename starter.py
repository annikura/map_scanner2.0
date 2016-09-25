import argparse
import os
import gzip
import subprocess

import filework

parser = argparse.ArgumentParser()
parser.add_argument("format")
args = parser.parse_args()

directory = r'maps/' + args.format + r'/'
folder = 'errors/'
files = os.listdir(directory)
for file in files:
    print(file)
    try:
        subprocess.check_call(["python", "main.py", directory + file, "--extended"])
    except Exception:
        with open(directory + file, "rb") as curf, open(folder + file, "wb") as wrto:
                wrto.write(filework.degzip(curf.read()))