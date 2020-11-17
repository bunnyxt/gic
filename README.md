# gic - gif in console

```
        _                      _  __   _                                   _      
   __ _(_) ___            __ _(_)/ _| (_)_ __     ___ ___  _ __  ___  ___ | | ___ 
  / _` | |/ __|  _____   / _` | | |_  | | '_ \   / __/ _ \| '_ \/ __|/ _ \| |/ _ \
 | (_| | | (__  |_____| | (_| | |  _| | | | | | | (_| (_) | | | \__ \ (_) | |  __/
  \__, |_|\___|          \__, |_|_|   |_|_| |_|  \___\___/|_| |_|___/\___/|_|\___|
  |___/                  |___/                                                    

```

gic - gif in console, play char gif in console via python

## Requirements

- `python3`
- `Pillow==6.1.0`

## Usage

### basic usage

`python gic.py test.gif`

### options

use `python gic.py -h` for help

```
usage: gic.py [-h] [-v] [-t] [-s SIZE] [-r RATIO] filename

positional arguments:
  filename              gif filename

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         show verbose log when running
  -t, --top-empty-rows  enable frame top empty rows
  -s SIZE, --size SIZE  char array size, only support 16 now
  -r RATIO, --ratio RATIO
                        char block height / width ratio
```

## Licence

[GNU General Public License v3.0](LICENCE)
