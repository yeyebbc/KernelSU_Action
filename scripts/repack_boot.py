#!/usr/bin/env python3
"""Replace an Android boot kernel and rebuild its unsigned AVB hash footer.

Requires an unlocked bootloader and a compatible installed ROM. The source
ramdisk, header metadata, AVB properties, and non-kernel payloads survive.
"""

import argparse
import hashlib
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

PAYLOADS = {"--kernel", "--ramdisk", "--second", "--recovery_dtbo", "--dtb"}


def run(script, *args):
    return subprocess.check_output(
        [sys.executable, str(script), *map(str, args)], text=True
    ).strip()


def unpack(tools, image, directory):
    args = shlex.split(run(tools / "unpack_bootimg.py", "--boot_img", image,
                           "--out", directory, "--format", "mkbootimg"))
    if len(args) % 2:
        raise ValueError("unpack_bootimg returned malformed arguments")
    return dict(zip(args[::2], args[1::2]))


def digest(path):
    with open(path, "rb") as stream:
        result = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.digest()


def repack(args):
    source, kernel, output = (Path(p).resolve() for p in
                              (args.source, args.kernel, args.output))
    tools, avbtool = Path(args.tools).resolve(), Path(args.avbtool).resolve()
    if output in (source, kernel):
        raise ValueError("output must not overwrite an input")
    with source.open("rb") as stream:
        magic = stream.read(8)
    partition_size = source.stat().st_size
    if magic != b"ANDROID!" or partition_size == 0 or partition_size % 4096:
        raise ValueError("expected a page-aligned Android boot partition image")
    if kernel.stat().st_size == 0:
        raise ValueError("kernel image is empty")

    # Require the unsigned boot hash metadata used by the supplied ROM image.
    info = run(avbtool, "info_image", "--image", source)
    fields = dict(line.strip().split(":", 1) for line in info.splitlines()
                  if ":" in line and not line.strip().startswith("Prop:"))
    for key, expected in {"Algorithm": "NONE", "Partition Name": "boot",
                          "Rollback Index": "0", "Rollback Index Location": "0",
                          "Flags": "0", "Hash Algorithm": "sha256"}.items():
        if fields.get(key, "").strip() != expected:
            raise ValueError(f"unsupported source AVB {key}: {fields.get(key)}")
    props = []
    for line in info.splitlines():
        if line.strip().startswith("Prop:"):
            key, value = line.strip()[5:].strip().split(" -> ", 1)
            props.extend(["--prop", f"{key}:{shlex.split(value)[0]}"])

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="repack-", dir=output.parent) as temp:
        temp = Path(temp)
        original = unpack(tools, source, temp / "original")
        if "--kernel" not in original or "--ramdisk" not in original:
            raise ValueError("source must contain kernel and ramdisk")
        if original.get("--header_version") not in {"1", "3"}:
            raise ValueError("only Android boot header versions 1 and 3 are supported")
        replaced = dict(original, **{"--kernel": str(kernel)})
        fresh = temp / "boot.img"
        run(tools / "mkbootimg.py",
            *(arg for pair in replaced.items() for arg in pair), "--output", fresh)
        # avbtool also enforces the space reserved for vbmeta and the footer.
        run(avbtool, "add_hash_footer", "--image", fresh,
            "--partition_name", "boot", "--partition_size", partition_size,
            "--algorithm", "NONE", "--hash_algorithm", "sha256", *props)
        run(avbtool, "verify_image", "--image", fresh)
        rebuilt = unpack(tools, fresh, temp / "rebuilt")
        if original.keys() != rebuilt.keys():
            raise ValueError("repacked image changed header/payload fields")
        for key, value in original.items():
            if key in PAYLOADS:
                expected = kernel if key == "--kernel" else value
                if digest(expected) != digest(rebuilt[key]):
                    raise ValueError(f"repacked payload differs: {key}")
            elif value != rebuilt[key]:
                raise ValueError(f"repacked boot metadata differs: {key}")
        if fresh.stat().st_size != partition_size:
            raise ValueError("repacked image has incorrect partition size")
        fresh.replace(output)
    print(f"Verified boot image: {output} ({partition_size} bytes)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools", required=True, help="AOSP mkbootimg directory")
    parser.add_argument("--avbtool", required=True, help="AOSP avbtool.py")
    parser.add_argument("--source", required=True)
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--output", required=True)
    try:
        repack(parser.parse_args())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"repack_boot: {exc}\n")


if __name__ == "__main__":
    main()
