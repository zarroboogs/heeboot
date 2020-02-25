
import bisect
import struct
import shutil
import argparse
from pathlib import Path
from ruamel.yaml import YAML
from elftools.elf.elffile import ELFFile


PATCHTYPE = {
    "load": "",
    "byte": "B",
    "le16": "<H",
    "be16": ">H",
    "le32": "<I",
    "be32": ">I",
    "le64": "<Q",
    "be64": ">Q",
    "lef32": "<f",
    "bef32": ">f",
    "lef64": "<d",
    "bef64": ">d",
}


def file_path(test):
    p = Path(test)
    if p.is_file():
        return p
    else:
        raise argparse.ArgumentTypeError(f"file does not exist -- {test}")


def parse_eboot(in_eboot):
    with open(in_eboot, "rb") as eboot:
        elf = ELFFile(eboot)
        segs = sorted(elf.iter_segments(), key=lambda x: x.header.p_vaddr)

    segv = [s.header.p_vaddr for s in segs]
    sego = [s.header.p_offset for s in segs]

    return segv, sego


def parse_patch(in_yml, by_names=None, by_hash=None):
    with open(in_yml) as yml_patch:
        yml = YAML(typ="safe", pure=True)
        yml.allow_duplicate_keys = True
        units = dict(yml.load(yml_patch))

    funits = units

    if by_hash:
        funits = {pname: funits[pname] for ptype, pname in funits[by_hash]}

    if by_names:
        funits = {pname: funits[pname] for pname in funits
                  if pname in by_names}

    return funits


def patch_eboot(in_eboot, patch, segs, out_eboot=None):
    segv, sego = segs
    shutil.copyfile(str(in_eboot), str(out_eboot))

    with open(out_eboot, "r+b") as out:
        for patch_name in patch:
            if len(patch[patch_name][0]) != 3:
                continue
            print(f"applying patch {patch_name}")
            for utype, uaddr, uvalue in patch[patch_name]:
                seg_idx = bisect.bisect(segv, uaddr) - 1
                at = uaddr - segv[seg_idx] + sego[seg_idx]
                out.seek(at, 0)
                out.write(struct.pack(PATCHTYPE[utype.lower()], uvalue))
                print((f"wrote ({utype}, 0x{uvalue:08x}) @ 0x{uaddr:08x} "
                       f"=> 0x{at:08x}"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_eboot", nargs='?', default="eboot.elf",
                        help="path to eboot", type=file_path)
    parser.add_argument("in_yml", nargs='?', default="patch.yml",
                        help="path to patch", type=file_path)
    parser.add_argument("out_eboot", nargs='?', help="path to patched eboot",
                        type=str)
    parser.add_argument("-n", nargs="*", help="filter patches by name")
    parser.add_argument("-p", help="filter patches by hash", metavar='HASH')
    args = parser.parse_args()

    # parse eboot
    try:
        segs = parse_eboot(args.in_eboot)
    except Exception:
        raise ValueError("error parsing eboot")

    # parse yml
    try:
        units = parse_patch(args.in_yml, by_names=args.n, by_hash=args.p)
    except Exception:
        raise ValueError("error parsing/filtering patch file")

    # patch eboot
    try:
        if not args.out_eboot:
            args.out_eboot = f"{args.in_eboot.name}-out"
        eo = Path(args.out_eboot)
        patch_eboot(args.in_eboot, units, segs, eo)
    except Exception:
        raise ValueError("error patching eboot")

    print("patching successful")


if __name__ == "__main__":
    main()
