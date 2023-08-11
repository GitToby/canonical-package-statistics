# canonical-package-statistics

### Install

While in project dir

```shell
pip install .
```

packaged artifact

```shell
pip install dist/canonical-package-statistics-0.1.0.tar.gz
```

The project used PDM, which has a set of extra utils for managing python projects.

### Usage:

```shell
python src/canonical_package_statistics/app.py --help
```

or, after installing the app can be run with the command:

```shell
package-stats -- help
```

### Help Message

```shell
 Usage: package-stats [OPTIONS] [ARCH]:[all|amd64|arm64|armel|armhf|i386|mips64                                                                                                 
                      el|mipsel|ppc64el|s390x|source|udeb-all|udeb-amd64|udeb-                                                                                                  
                      arm64|udeb-armel|udeb-armhf|udeb-i386|udeb-mips64el|udeb-                                                                                                 
                      mipsel|udeb-ppc64el|udeb-s390x]                                                                                                                           
                                                                                                                                                                                
 Downloads the compressed Contents file associated with it from a Debian mirror & output the statistics of the top 10 packages that have the most files associated with them.   
                                                                                                                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   arch      [ARCH]:[all|amd64|arm64|armel|armhf|i386|mips64el|mipsel|ppc64el|s390x|source|  Specific architecture to print statistics for [default: all]                     │
│             udeb-all|udeb-amd64|udeb-arm64|udeb-armel|udeb-armhf|udeb-i386|udeb-mips64el|u                                                                                   │
│             deb-mipsel|udeb-ppc64el|udeb-s390x]                                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --cache                 --no-cache             Whether to bypass any cached results [default: cache]                                                                         │
│ --mirror                              TEXT     The Debian Repo Mirror to use [default: http://ftp.uk.debian.org/debian/dists/stable/main]                                    │
│ --list-count                          INTEGER  The number of packages to list with the most files [default: 10]                                                              │
│ --install-completion                           Install completion for the current shell.                                                                                     │
│ --show-completion                              Show completion for the current shell, to copy it or customize the installation.                                              │
│ --help                                         Show this message and exit.                                                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Notes

Overall this was a relatively trivial python problem; the hardest part for me was understanding the data format and problem.

time taken:

- Understanding format & problem 40 mins
- Initial project setup 20 mins
- Writing http request to dist 15 mins
- Writing cache logic 30 mins
- Parse & count logic 20 mins
- Tests via TDD 35 mins
- Packaging & config 10 mins

There is linking via ruff, formatting with black and test coverage with pytest cov. I decided against type testing like
mypy as this is a very small script; maybe in larger projects.

There are some areas id improve, including:

- More thorough testing, incl negative testing and multiplatform in CI
- More useful cache file settings (timeouts and such)
- More UI feedback for processes that take time (http calls, reading files etc)
