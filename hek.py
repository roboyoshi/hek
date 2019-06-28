#!/usr/bin/env python
import sys
import os

version = "0.0.1"

error_found = False


def warn(file, message):
    global error_found
    error_found = True
    print("> %s --- %s" % (file, message))


def manage_dir(f):
    name = f.rsplit('/', 1)[1]
    relative_path = f.rsplit(args, 1)[1]

    if name.startswith("."):
        warn(relative_path, "Hidden directory")

    if len(os.listdir(f)) is 0:
        warn(relative_path, "Empty directory")

    if not name.endswith(") [FLAC]") and not name.endswith(") [mp3]"):
        warn(relative_path, "Check directory name")


def manage_file(f):
    name = f.rsplit('/', 1)[1]
    relative_path = f.rsplit(args, 1)[1]

    if name.startswith("."):
        warn(relative_path, "Hidden file")

    if not name.endswith(".jpg") and not name.endswith(".flac") and not name.endswith(".mp3"):
        warn(relative_path, "Check filetype")

    if name.endswith(".jpg"):
        if not name == "cover.jpg":
            warn(relative_path, "Check filetype")


def tree(root):
    for item in sorted(os.listdir(root)):
        f = os.path.join(root, item)
        if os.path.isdir(f):
            manage_dir(f)
            tree(f)
        elif os.path.isfile(f):
            manage_file(f)


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
