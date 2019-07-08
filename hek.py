#!/usr/bin/env python
# Copyright (C) 2019 Josep Oliver Arlès <josep.oliver@tutanota.com>
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
import signal
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

version = "0.0.1"

config_dir = os.path.expanduser("~/.config/hek/")

error_found = False
errors_files = []
errors_tags = []
tags = None


class MusicFile:
    tracknumber = None
    discnumber = None
    title = None
    album = None
    artist = None
    albumartist = None
    year = None
    comment = None
    relative_path = None
    id = None


def warn_tags(music_file, message):
    global error_found
    error_found = True
    if [music_file.id, message] not in errors_tags:
        print("> %s --- %s" % (music_file.relative_path, message))
    errors_tags.append([music_file.id, message])


def warn_files(file, message):
    global error_found
    error_found = True
    if [file, message] not in errors_files:
        print("> %s --- %s" % (file, message))
    errors_files.append([file, message])


def capitalize_after(word, symbol, relative_path, music_file):
    i = word.rfind(symbol) + len(symbol)
    x = 0
    if symbol == "'" or symbol == "’":
        x = 1
    if len(word) > i + x and str(word[i]).islower():
        for e in read_config_file("ignore_quote_case"):
            if word == e:
                return
        if music_file:
            warn_tags(music_file, "Capitalize")
        else:
            warn_files(relative_path, "Capitalize")
        word = word[0: i - 1]
        if symbol in word:
            capitalize_after(word, symbol, relative_path, music_file)


def check_name_tags(music_file, field):
    if field.startswith(" ") or field.endswith(" "):
        warn_tags(music_file, "Trailing spaces found")
    if "  " in field:
        warn_tags(music_file, "Double space found")
    if any(i in field for i in read_config_file("rules/sequences_tags")):
        if field not in read_config_file("ignore_contains"):
            warn_tags(music_file, "Contains")
    words = field.split(" ")
    for i in words:
        if i[:1].islower() and field not in read_config_file("ignore_case"):
            warn_tags(music_file, "Capitalize")
        for s in read_config_file("rules/capitalize_after"):
            if s in i:
                capitalize_after(i, s, music_file.relative_path, music_file)


def check_name_files(name, relative_path):
    name_without_extension, extension = os.path.splitext(name)
    if name_without_extension.startswith(" ") or name_without_extension.endswith(" "):
        warn_files(relative_path, "Trailing spaces found")
    if "  " in name_without_extension:
        warn_files(relative_path, "Double space found")
    if any(i in name_without_extension for i in read_config_file("rules/sequences_files")):
        if name not in read_config_file("ignore_contains"):
            warn_files(relative_path, "Contains")
    words = name_without_extension.split(" ")
    for i in words:
        if i[:1].islower() and name_without_extension not in read_config_file("ignore_case"):
            warn_files(relative_path, "Capitalize")
        for s in read_config_file("rules/capitalize_after"):
            if s in i:
                capitalize_after(i, s, relative_path, None)


def manage_dir(f):
    name = f.rsplit('/', 1)[1]
    relative_path = f.rsplit(args, 1)[1]
    if name.startswith("."):
        warn_files(relative_path, "Hidden directory")
    if len(os.listdir(f)) is 0:
        warn_files(relative_path, "Empty directory")
    if len(read_config_file("rules/dir_ends")) > 0:
        if not any(name.endswith(i) for i in read_config_file("rules/dir_ends")):
            if name not in read_config_file("ignore_dir_ends"):
                warn_files(relative_path, "Check directory name")
    check_name_files(name, relative_path)


def manage_file(f):
    name = f.rsplit('/', 1)[1]
    relative_path = f.rsplit(args, 1)[1]
    if name.startswith("."):
        warn_files(relative_path, "Hidden file")
    extensions = [i for i in read_config_file("rules/filetypes") if i.startswith(".")]
    exact_matches = [i for i in read_config_file("rules/filetypes") if not i.startswith(".")]
    if not any(name.endswith(i) for i in extensions) and name not in exact_matches:
        warn_files(relative_path, "Check filetype")
    if not any(name == i for i in exact_matches) and not any(name.endswith(i) for i in extensions):
        warn_files(relative_path, "Check filetype")
    check_name_files(name, relative_path)


def check_music_file(music_file):
    if music_file.tracknumber and music_file.tracknumber.startswith("0"):
        warn_tags(music_file, "Track starts with 0")
    if music_file.title:
        check_name_tags(music_file, music_file.title)
    if music_file.album:
        check_name_tags(music_file, music_file.album)
    if music_file.artist:
        check_name_tags(music_file, music_file.artist)
    if music_file.albumartist:
        check_name_tags(music_file, music_file.albumartist)
    if not music_file.year:
        if music_file.album and music_file.album not in read_config_file("ignore_year"):
            warn_tags(music_file, "Missing year")
    else:
        if len(music_file.year) != 4:
            warn_tags(music_file, "Year format")
    if music_file.comment:
        if len(music_file.comment) != 4:
            warn_tags(music_file, "Year format")
    if music_file.artist and music_file.albumartist:
        if not music_file.albumartist == "" and not music_file.artist == music_file.albumartist:
            if music_file.album and music_file.album not in read_config_file("ignore_albumartist"):
                warn_tags(music_file, "Artist != albumartist")


def read_tags(f):
    global tags
    relative_path = f.rsplit(args, 1)[1]
    name, extension = os.path.splitext(f)
    music_file = MusicFile()
    try:
        if extension == ".flac":
            flac_file = FLAC(f)
            tags = flac_file.tags
        elif extension == ".mp3":
            mp3_file = MP3(f, ID3=EasyID3)
            tags = mp3_file.tags
    except Exception as e:
        print(e)
    if tags:
        if "tracknumber" in tags:
            music_file.tracknumber = tags['tracknumber'][0]
        if "title" in tags:
            music_file.title = tags['title'][0]
        if "album" in tags:
            music_file.album = tags['album'][0]
        if "artist" in tags:
            music_file.artist = tags['artist'][0]
        if "albumartist" in tags:
            music_file.albumartist = tags['albumartist'][0]
        if "date" in tags:
            music_file.year = tags['date'][0]
        else:
            music_file.year = None
        if "comment" in tags:
            music_file.comment = tags['comment'][0]
        music_file.relative_path = relative_path
        music_file.id = "%s - %s - %s - %s" % \
                        (music_file.albumartist, music_file.album, music_file.year, music_file.title)
        check_music_file(music_file)


def tree_tags(root):
    for i in sorted(os.listdir(root)):
        f = os.path.join(root, i)
        if os.path.isdir(f):
            tree_tags(f)
        elif os.path.isfile(f):
            read_tags(f)


def tree_files(root):
    for i in sorted(os.listdir(root)):
        f = os.path.join(root, i)
        if os.path.isdir(f):
            manage_dir(f)
            tree_files(f)
        elif os.path.isfile(f):
            manage_file(f)


def read_config_file(filename):
    with open(config_dir + filename) as f:
        return [i.strip() for i in f.readlines()]


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


def show_info():
    print("Usage:")
    print("$ hek /path/to/music")
    print("$ hek relative/path/to/music")
    print("$ hek .")
    print("$ hek /path/to/music --files")
    print("$ hek /path/to/music --tags")
    sys.exit(0)


def signal_handler(s, f):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

init_config()

if len(sys.argv) != 2 and len(sys.argv) != 3:
    show_info()
else:
    if len(sys.argv) == 2:
        args = sys.argv[1]
        if args == "-v":
            print(version)
        elif os.path.isdir(args):
            args = os.path.abspath(args)
            print("Working on %s" % args)
            tree_files(args)
            tree_tags(args)
            if not error_found:
                print("No errors found")
        elif not os.path.isdir(args):
            print("%s is not a directory" % args)
    elif len(sys.argv) == 3:
        args = sys.argv[1]
        option = sys.argv[2]
        if option not in "--files" and option not in "--tags":
            show_info()
        if os.path.isdir(args) and option == "--files":
            args = os.path.abspath(args)
            print("Working on %s" % args)
            tree_files(args)
            if not error_found:
                print("No errors found")
        elif os.path.isdir(args) and option == "--tags":
            args = os.path.abspath(args)
            print("Working on %s" % args)
            tree_tags(args)
            if not error_found:
                print("No errors found")
        elif not os.path.isdir(args):
            print("%s is not a directory" % args)
