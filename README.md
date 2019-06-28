# hek

## Depends on
- `python-mutagen`

## Installation
```
$ git clone https://gitlab.com/dunon/hek.git
$ cd hek
$ sudo cp hek.py /usr/bin/hek
```

## Usage
```
$ hek ~/Music
$ hek .         # run on current directory
$ hek -v        # display version
```

## Configuration
See `example_config`

### Rules
Stored in `~/.config/hek/rules`
- Do not allow certain symbols `symbols`
- Do not allow sequences in files `sequences_files`
- Do not allow sequences in tags `sequences_tags`
- Capitalize after these symbols `capitalize_after`
- Only allow these filetypes `filetypes`
- How directories must end `dir_ends`

### Exceptions
Stored in `~/.config/hek`
- Some words are not capitalized `ignore_case`
- Do not warn about lower case after ' `ignore_quote_case`
- Allow symbols or sequences as exceptions `ignore_contains`
- Do no warn about missing year `ignore_year`
- Do not warn about different albumartist/artist `ignore_albumartist`
- Ignore how directory ends `ignore_dir_ends`
