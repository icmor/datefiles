#!/usr/bin/env python

import argparse
import pathlib
import re
from dateutil.parser import isoparse

parser = argparse.ArgumentParser()
parser.add_argument("path", help="image directory", type=pathlib.Path)
parser.add_argument("-y", "--year", help="year of datestamps", type=int)
parser.add_argument("-m", "--month", help="month of datestamps", type=int)
args = parser.parse_args()

if not args.path.is_dir(): raise NotADirectoryError("Path is not a directory.")

days = "(0[1-9]|[0-2][0-9]|3[01])"
months = f"{args.month:02}" if args.month else "(0[1-9]|1[0-2])"
years = str(args.year) if args.year else "(19[7-9][0-9]|2[01][0-9]{2})"
ex = re.compile("-?".join([years, months, days]))

outliers = []

for file in args.path.iterdir():
    if not file.is_file(): continue

    if not (date := ex.search(file.stem)):
        outliers.append(file.name)
        continue

    date = isoparse(date.group())
    if (args.year and args.year != date.year or
        args.month and args.month != date.month):
        outliers.append(file.name)
        continue


    new = args.path.joinpath(date.strftime("%Y_%m_%d") + file.suffix)
    if new.exists():
        i = 1
        while args.path.joinpath(f"{new.stem}_{i:02}{new.suffix}").exists():
            i += 1
        new = args.path.joinpath(f"{new.stem}_{i:02}{new.suffix}")
    file.replace(new)

if outliers:
    outliers_dir = args.path.joinpath("outliers")
    if not outliers_dir.exists(): outliers_dir.mkdir()
    for file in outliers:
        file = args.path.joinpath(file)
        file.replace(outliers_dir.joinpath(file.name))

print(f"Completed renaming successfully with {len(outliers)} outliers.")
