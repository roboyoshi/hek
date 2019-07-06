#!/usr/bin/env python
# Copyright (C) 2019 Josep Oliver Arles <josep.oliver@tutanota.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import os

version = "0.0.1"

error_found = False
config_dir = "./example_config/"
comma = "'"

lower_letters = "abcdefghijklmnopqrstuvwxyzçñ"


def warn(file, message):
    global error_found
    error_found = True
    print("> %s --- %s" % (file, message))


def warn_trailing(file, message):
    global error_found
    error_found = True
    print("> %s --- %s" % (file, message))
    print("Correct trailing spaces and re-run the program")
    sys.exit(0)


def capitalize_after(word, symbol, relative_path):
    i = word.rfind(symbol) + len(symbol)
    x = 0
    if symbol == comma:
        x = 1
    if len(word) > i + x and word[i] in lower_letters:
        for e in read_config_file("ignore_quote_case"):
            if word == e:
                return
        warn(relative_path, "Capitalize")

        word = word[0: i - 1]
        if symbol in word:
            capitalize_after(word, symbol, relative_path)


def check_name_files(name, relative_path):
    name_without_extension, extension = os.path.splitext(name)
    if name_without_extension.startswith(" ") or name_without_extension.endswith(" "):
        warn_trailing(relative_path, "Trailing spaces found")
    if "  " in name_without_extension:
        warn_trailing(relative_path, "Double space found")
    if any(i in name_without_extension for i in read_config_file("rules/sequences_files")):
        warn(relative_path, "Contains")
    # capitalize
    words = name_without_extension.split(" ")
    for i in words:
        if i[:1] in lower_letters and name_without_extension not in read_config_file("ignore_case"):
            warn(relative_path, "Capitalize")
        for s in read_config_file("rules/capitalize_after"):
            if s in i:
                capitalize_after(i, s, relative_path)


def manage_dir(f):
    name = f.rsplit('/', 1)[1]
    relative_path = f.rsplit(args, 1)[1]

    if name.startswith("."):
        warn(relative_path, "Hidden directory")

    if len(os.listdir(f)) is 0:
        warn(relative_path, "Empty directory")

    if not any(name.endswith(i) for i in read_config_file("rules/dir_ends")):
        if name not in read_config_file("ignore_dir_ends"):
            warn(relative_path, "Check directory name")

    check_name_files(name, relative_path)


def manage_file(f):
    name = f.rsplit('/', 1)[1]
    relative_path = f.rsplit(args, 1)[1]

    if name.startswith("."):
        warn(relative_path, "Hidden file")

    if not any(name.endswith(i) for i in read_config_file("rules/filetypes")):
        warn(relative_path, "Check filetype")

    # option
    if name.endswith(".jpg"):
        if not name == "cover.jpg":
            warn(relative_path, "Check filetype")

    check_name_files(name, relative_path)


def tree(root):
    for item in sorted(os.listdir(root)):
        f = os.path.join(root, item)
        if os.path.isdir(f):
            manage_dir(f)
            tree(f)
        elif os.path.isfile(f):
            manage_file(f)


def read_config_file(filename):
    with open(config_dir + filename) as f:
        return [x.strip() for x in f.readlines()]


def init_config():
    os.system("mkdir -p ~/.config/hek/rules")
    os.system("touch -a ~/.config/hek/ignore_albumartist")
    os.system("touch -a ~/.config/hek/ignore_case")
    os.system("touch -a ~/.config/hek/ignore_contains")
    os.system("touch -a ~/.config/hek/ignore_dir_ends")
    os.system("touch -a ~/.config/hek/ignore_quote_case")
    os.system("touch -a ~/.config/hek/ignore_year")
    os.system("touch -a ~/.config/hek/rules/capitalize_after")
    os.system("touch -a ~/.config/hek/rules/dir_ends")
    os.system("touch -a ~/.config/hek/rules/filetypes")
    os.system("touch -a ~/.config/hek/rules/sequences_files")
    os.system("touch -a ~/.config/hek/rules/sequences_tags")


init_config()

if len(sys.argv) != 2:
    print("Usage:")
    print("$ hek /path/to/music")
    print("$ hek relative/path/to/music")
    print("$ hek .")
    sys.exit(0)

if len(sys.argv) is 2:
    args = sys.argv[1]
    if args == "-v":
        print(version)
    elif os.path.isdir(args):
        args = os.path.abspath(args)
        print("Working on %s" % args)
        tree(args)
        if not error_found:
            print("No errors found")
    elif not os.path.isdir(args):
        print("%s is not a directory" % args)
