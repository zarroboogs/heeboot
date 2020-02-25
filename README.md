
# heeboot

Applies RPCS3 style yaml patches directly to an eboot file.

## Dependencies

- `python3`
  - `pyelftools`
  - `ruamel.yaml`

To install: `pip install -r requirements.txt`

## Usage

```txt
usage: heeboot.py [-h] [-n [N [N ...]]] [-p HASH]
                  [in_eboot] [in_yml] [out_eboot]

positional arguments:
  in_eboot        path to eboot
  in_yml          path to patch
  out_eboot       path to patched eboot

optional arguments:
  -h, --help      show this help message and exit
  -n [N [N ...]]  filter patches by name
  -p HASH         filter patches by hash
```
