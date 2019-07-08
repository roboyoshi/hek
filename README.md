# hek

Python script that checks your music collection given a set of rules

- Does not modify files
- Reads FLAC and mp3 tags
- Checks capitalization, filetypes, missing tags
- Manage exceptions

## Depends on
- `python-mutagen`

## Installation
```bash
$ git clone https://github.com/dunon/hek.git
$ cd hek
$ sudo cp hek.py /usr/bin/hek
```
### Arch Linux
Available on the [AUR](https://aur.archlinux.org/packages/hek/)

## Usage
```bash
$ hek ~/Music
$ hek .                 # run on current directory
$ hek -v                # display version
$ hek ~/Music --files    # check files only
$ hek ~/Music --tags    # check tags only
```

## Configuration
See [example_config](https://github.com/dunon/hek/tree/master/example_config)

### Rules
Stored in `~/.config/hek/rules`
- Capitalize after these symbols `capitalize_after`
- Only allow these filetypes `filetypes`
- How directories must end `dir_ends`
- Do not allow certain symbols or sequences in files `sequences_files`
- Do not allow certain symbols or sequences in tags `sequences_tags`

### Exceptions
Stored in `~/.config/hek`
- Some words are not capitalized `ignore_case`
- Do not warn about lower case after ' `ignore_quote_case`
- Allow symbols or sequences as exceptions `ignore_contains`
- Do no warn about missing year `ignore_year`
- Do not warn about different albumartist/artist `ignore_albumartist`
- Ignore how directory ends `ignore_dir_ends`

## License
hek is released under the GNU GPLv3 license. See `LICENSE` for details.
