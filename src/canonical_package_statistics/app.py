import gzip
from collections import Counter
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Annotated, Iterable

import requests
import typer

DEFAULT_MIRROR = "http://ftp.uk.debian.org/debian/dists/stable/main/"
CACHE_DIR = Path().home() / ".cache" / "package-statistics"  # technically not correct on Windows machines


class Arch(Enum):
    """
    This is the list of enums we can search for, as per the directory structure of
     http://ftp.uk.debian.org/debian/dists/stable/main/
    """

    all = "all"
    amd64 = "amd64"
    arm64 = "arm64"
    armel = "armel"
    armhf = "armhf"
    i386 = "i386"
    mips64el = "mips64el"
    mipsel = "mipsel"
    ppc64el = "ppc64el"
    s390x = "s390x"
    source = "source"
    udeb_all = "udeb-all"
    udeb_amd64 = "udeb-amd64"
    udeb_arm64 = "udeb-arm64"
    udeb_armel = "udeb-armel"
    udeb_armhf = "udeb-armhf"
    udeb_i386 = "udeb-i386"
    udeb_mips64el = "udeb-mips64el"
    udeb_mipsel = "udeb-mipsel"
    udeb_ppc64el = "udeb-ppc64el"
    udeb_s390 = "udeb-s390x"


def main(
    arch: Annotated[Arch, typer.Option(help="Specific architecture to print statistics for")] = Arch.all.value,
    use_cached: Annotated[bool, typer.Argument(help="Whether to bypass any cached results")] = True,
    mirror: Annotated[str, typer.Argument(help="The Debian Repo Mirror to use")] = DEFAULT_MIRROR,
    list_count: Annotated[int, typer.Argument(help="The number of packages to list with the most files")] = 10,
):
    """
    Downloads the compressed Contents file associated with it from a Debian mirror & output the statistics of the top
    10 packages that have the most files associated with them.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    contents_file = f"Contents-{arch.value}.gz"
    cache_file = (CACHE_DIR / contents_file).resolve()
    if use_cached and cache_file.exists():
        # use cached file, no need to network requests
        print(f"Using cached file {cache_file}")
        data = read_gzip_file(cache_file)
    else:
        url = f"{mirror}/{contents_file}"
        print(f"making request to mirror {url} to download Contents File")
        res = requests.get(url)
        res.raise_for_status()

        # store content as the cached file for next time.
        bin_data = res.content
        persist_file(cache_file, bin_data)

        # use in-memory data for reading, no need for disk again
        cache_file_like = BytesIO(bin_data)
        data = read_gzip_file(cache_file_like)

    print(f"Data file contains {len(data)} rows")
    package_file_counts, err_lines = parse_file_rows(data)

    print(f"Done. Found {err_lines} error lines in file {contents_file}")
    for i, (package, file_count) in enumerate(package_file_counts.most_common(list_count)):
        print(i + 1, package.decode(), file_count)


def persist_file(cache_file_path: Path, bin_data: bytes):
    """
    Write some binary data to disk.

    :param cache_file_path: the path to store data
    :param bin_data: the data to store.
    :return: Nothing
    """
    cache_file_path.touch(exist_ok=True)
    print(f"writing content to cache file {cache_file_path}")
    with open(cache_file_path, "wb"):
        cache_file_path.write_bytes(bin_data)


def read_gzip_file(filename) -> Iterable[bytes]:
    """
    Reads a file like data structure to an iterable structure of bytes.

    :param filename: a filename object that conforms to `gzip.open()` filename
    :return: an iterable of binary data.
    """
    with gzip.open(filename, "r") as f:
        data = f.readlines()
    return data


def parse_file_rows(file_rows: Iterable[bytes]):
    """
    Takes the iterable of rows, parses each row to figure out how many packages a file is associated with then counts
    the number of files associated with each package.

    :param file_rows: an iterable of the rows in the uncompressed text file.
    :return: a Counter of packages and their file counts, a count of error lines in the file.
    """
    # as per the mirror docs (see readme) we should have a table in the form
    # FILE LOCATION[,LOCATION]
    # FILE LOCATION[,LOCATION]
    # where location maps to a qualified package; we will use the qualified package name as the key to count files.

    # This var will contain the name of the package for each time there is a file associated with it.
    package_files = []
    err_lines = 0
    for row in file_rows:
        try:
            # we don't care about the names of the files, just the packages is associated with a file
            # the package names are the last string element in a whitespace sep list.
            row_split = row.split()
            # the file name can include spaces, leading to tuple unpacking being unsuitable
            # e.g "usr/src/rustc-1.63.0/compiler/rustc/Windows Manifest.xml devel/rust-src"
            locations = row_split[-1].strip()
        except ValueError:
            # any lines not conforming to the standard will be ignored as per docs
            err_lines += 1
            continue

        locations_split = locations.strip().split(b",")
        package_files.extend(locations_split)

    # because of python natives being slow, this is a faster counting mechanism than custom counting dict
    return Counter(package_files), err_lines


if __name__ == "__main__":
    typer.run(main)
